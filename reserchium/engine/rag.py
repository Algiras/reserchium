import os
import chromadb
from llama_index.core import VectorStoreIndex, Settings, StorageContext
from llama_index.core.node_parser import SentenceSplitter
from llama_index.vector_stores.chroma import ChromaVectorStore
from dotenv import load_dotenv
from rich.console import Console

console = Console()
load_dotenv()

from reserchium.config import load_config

# Setup Default LLM and Embedding models
def configure_settings():
    """Configure LlamaIndex global settings based on user config."""
    config = load_config()
    provider = config.get("provider", "openai")
    
    if provider == "openai":
        from llama_index.llms.openai import OpenAI
        from llama_index.embeddings.openai import OpenAIEmbedding
        
        api_key = config.get("openai_api_key") or os.environ.get("API_KEY") or os.environ.get("OPENAI_API_KEY")
        api_base = os.environ.get("API_BASE_URL")
        
        if not api_key and not api_base:
            console.print("[yellow]Warning: API Key not found in config or env.[/yellow]")
            
        Settings.llm = OpenAI(
            model=config.get("model_name", "gpt-4o-mini"), 
            api_key=api_key or "sk-dummy", 
            api_base=api_base
        )
        Settings.embed_model = OpenAIEmbedding(
            model=config.get("embed_model_name", "text-embedding-3-small"), 
            api_key=api_key or "sk-dummy", 
            api_base=api_base
        )
        
    elif provider == "anthropic":
        from llama_index.llms.anthropic import Anthropic
        # Anthropic doesn't have a direct embedding model in LlamaIndex by default, usually we use Voyage or OpenAI for embeddings with Anthropic
        # We'll use OpenAI for embeddings or HuggingFace locally as a fallback, but let's stick to OpenAI embeddings for simplicity if mixing, or add a local one.
        # For now, let's just use HuggingFace embedding locally to avoid OpenAI dependency if they chose Anthropic.
        try:
            from llama_index.embeddings.huggingface import HuggingFaceEmbedding
            Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")
        except ImportError:
            console.print("[yellow]Hint: Run `uv add llama-index-embeddings-huggingface` for local embeddings with Anthropic.[/yellow]")

        api_key = config.get("anthropic_api_key") or os.environ.get("ANTHROPIC_API_KEY")
        Settings.llm = Anthropic(model="claude-3-5-sonnet-20241022", api_key=api_key)
        
    elif provider == "ollama":
        from llama_index.llms.ollama import Ollama
        from llama_index.embeddings.ollama import OllamaEmbedding
        
        base_url = config.get("ollama_base_url", "http://localhost:11434")
        model_name = config.get("ollama_model", "llama3.2")
        Settings.llm = Ollama(model=model_name, base_url=base_url, request_timeout=120.0)
        Settings.embed_model = OllamaEmbedding(model_name="nomic-embed-text", base_url=base_url)

    Settings.node_parser = SentenceSplitter(chunk_size=1024, chunk_overlap=20)

def get_chroma_collection(collection_name="papers", path="./chroma_db"):
    """Initialize ChromaDB client and get or create a collection."""
    db = chromadb.PersistentClient(path=path)
    chroma_collection = db.get_or_create_collection(collection_name)
    return chroma_collection

def ingest_documents(docs, collection_name="papers"):
    """
    Ingest a list of Document objects into the ChromaDB vector store.
    """
    configure_settings()
    console.print("[cyan]Configuring Vector Store (ChromaDB)...[/cyan]")
    chroma_collection = get_chroma_collection(collection_name)
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    
    console.print(f"[cyan]Indexing {len(docs)} documents...[/cyan]")
    index = VectorStoreIndex.from_documents(
        docs, storage_context=storage_context, show_progress=True
    )
    console.print("[bold green]Ingestion complete![/bold green]")
    return index

def get_query_engine(collection_name="papers", similarity_top_k=10, use_hybrid=True):
    """
    Returns a LlamaIndex query engine backed by the persisted ChromaDB.
    If use_hybrid is True, combines Vector DB with BM25 sparse search and reranks using a Cross-Encoder.
    """
    configure_settings()
    chroma_collection = get_chroma_collection(collection_name)
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    
    # Generate index from existing vector store mapping
    index = VectorStoreIndex.from_vector_store(vector_store)
    
    if use_hybrid:
        console.print("[cyan]Initializing Hybrid Search (BM25 + Reranking)...[/cyan]")
        try:
            from llama_index.retrievers.bm25 import BM25Retriever
            from llama_index.core.retrievers import QueryFusionRetriever
            from llama_index.postprocessor.flag_embedding_reranker import FlagEmbeddingReranker
            from llama_index.core.query_engine import RetrieverQueryEngine
            
            vector_retriever = index.as_retriever(similarity_top_k=similarity_top_k)
            
            from llama_index.core.schema import TextNode
            
            nodes = []
            if chroma_collection.count() > 0:
                result = chroma_collection.get(include=["documents", "metadatas"])
                if result and "documents" in result and result["documents"]:
                    for doc, meta, doc_id in zip(result["documents"], result["metadatas"], result["ids"]):
                        nodes.append(TextNode(text=doc, metadata=meta or {}, id_=doc_id))
                
            bm25_retriever = BM25Retriever.from_defaults(nodes=nodes, similarity_top_k=similarity_top_k)
            
            retriever = QueryFusionRetriever(
                [vector_retriever, bm25_retriever],
                similarity_top_k=similarity_top_k,
                num_queries=1,  # Keep it simple
                mode="reciprocal_rank",
            )
            
            reranker = FlagEmbeddingReranker(top_n=5, model="BAAI/bge-reranker-base")
            query_engine = RetrieverQueryEngine.from_args(
                retriever=retriever,
                node_postprocessors=[reranker]
            )
            return query_engine
        except Exception as e:
            console.print(f"[yellow]Hybrid search initialization failed ({e}). Falling back to standard Vector RAG.[/yellow]")
            return index.as_query_engine(similarity_top_k=5)
    else:
        # Standard Engine
        return index.as_query_engine(similarity_top_k=5)
