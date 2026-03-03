import os
from llama_index.core import PropertyGraphIndex
from llama_index.core.graph_stores import SimpleGraphStore
from llama_index.core.indices.property_graph import SimpleLLMPathExtractor
from rich.console import Console
from reserchium.engine.rag import configure_settings

console = Console()

def build_knowledge_graph(docs, store_path="./kg_store.json"):
    """
    Extracts entities and relationships from the provided documents and
    constructs a PropertyGraphIndex.
    """
    configure_settings()
    console.print("[yellow]Extracting Knowledge Graph Entities (This may take a while)...[/yellow]")
    
    # We will use the SimpleGraphStore which persists to a local JSON file or dict
    graph_store = SimpleGraphStore()
    
    # SimpleLLMPathExtractor uses the configured Settings.llm to extract (entity)->[relation]->(entity) triplets
    kg_extractor = SimpleLLMPathExtractor(
        max_paths_per_chunk=10,
        num_workers=4,
        show_progress=True
    )
    
    index = PropertyGraphIndex.from_documents(
        docs,
        embed_model=None, # We don't embed the graph strictly yet, just structural queries
        kg_extractors=[kg_extractor],
        property_graph_store=graph_store,
        show_progress=True
    )
    
    # SimpleGraphStore doesn't immediately persist to disk intuitively out-of-the-box like ChromaDB persistent client,
    # so we usually persist the entire storage context, but for graph we can just dump the dict.
    # LlamaIndex SimpleGraphStore uses persist()
    graph_store.persist(store_path)
    console.print("[bold green]Knowledge Graph Construction Complete![/bold green]")
    return index

def load_knowledge_graph(store_path="./kg_store.json"):
    """Loads a previously extracted Property Graph from disk."""
    configure_settings()
    if not os.path.exists(store_path):
        console.print("[red]Knowledge graph store not found. Please ingest a document first.[/red]")
        return None
        
    graph_store = SimpleGraphStore.from_persist_path(store_path)
    index = PropertyGraphIndex.from_existing(
        property_graph_store=graph_store,
        embed_model=None
    )
    return index
