import typer
from rich.console import Console
from rich.prompt import Prompt
from reserchium.config import load_config, save_config
from reserchium.parsers.pdf import get_document_nodes
from reserchium.engine.rag import ingest_documents, get_query_engine

app = typer.Typer(
    name="reserchium",
    help="AI-powered Research Paper Review CLI",
    add_completion=False,
)
console = Console()

@app.command()
def auth():
    """Configure LLM providers and API keys."""
    config = load_config()
    console.print("[bold cyan]Reserchium Configuration[/bold cyan]")
    
    provider = Prompt.ask(
        "Select LLM Provider", 
        choices=["openai", "anthropic", "ollama"], 
        default=config.get("provider", "openai")
    )
    config["provider"] = provider
    
    if provider == "openai":
        key = Prompt.ask("OpenAI API Key (leave blank to keep current)", default="")
        if key:
            config["openai_api_key"] = key
    elif provider == "anthropic":
        key = Prompt.ask("Anthropic API Key (leave blank to keep current)", default="")
        if key:
            config["anthropic_api_key"] = key
    elif provider == "ollama":
        url = Prompt.ask("Ollama Base URL", default=config.get("ollama_base_url", "http://localhost:11434"))
        # We can dynamically set the ollama model here
        ollama_model = Prompt.ask("Ollama Model (e.g., llama3.2, mistral-small3.2)", default=config.get("ollama_model", "llama3.2"))
        config["ollama_base_url"] = url
        config["ollama_model"] = ollama_model
        
    brave_key = Prompt.ask("Brave Search API Key (optional, for web search agent)", default="")
    if brave_key:
        config["brave_api_key"] = brave_key
        
    s2_key = Prompt.ask("Semantic Scholar API Key (optional, for premium paper fetching)", default="")
    if s2_key:
        config["semanticscholar_api_key"] = s2_key
        
    llamaparse_key = Prompt.ask("LlamaParse API Key (optional, for advanced math & table extraction)", default="")
    if llamaparse_key:
        config["llamaparse_api_key"] = llamaparse_key
        
    save_config(config)
    console.print("[bold green]Configuration saved successfully to ~/.researchium/config.json[/bold green]")

@app.command()
def ingest(file_path: str = typer.Argument(..., help="Path to the PDF or text file to ingest."), collection: str = typer.Option("papers", help="ChromaDB collection name.")):
    """
    Parse a paper, generate RAG embeddings, and extract Knowledge Graph entities.
    """
    console.print(f"[bold cyan]Ingesting document:[/bold cyan] {file_path}")
    docs = get_document_nodes(file_path)
    if docs:
        ingest_documents(docs, collection_name=collection)
        # Optional: Build KG, though this calls the LLM for every document chunk and can be expensive/slow
        # Disabling by default unless a flag is passed to save local API costs for huge PDFs.
        build_kg = typer.confirm("Do you also want to build a Knowledge Graph? (This uses the LLM heavily and takes time)", default=False)
        if build_kg:
            from reserchium.graph.builder import build_knowledge_graph
            build_knowledge_graph(docs, store_path="./kg_store.json")

@app.command()
def fetch(query: str = typer.Argument(..., help="Search Query or ArXiv ID of the paper"), provider: str = typer.Option("arxiv", help="Source provider to use: 'arxiv' or 'semanticscholar'"), collection: str = typer.Option("papers", help="ChromaDB collection name."), refs: bool = typer.Option(False, "--refs", help="Also fetch and ingest cited references (Semantic Scholar only)")):
    """
    Fetch a paper directly from a provider (ArXiv or Semantic Scholar) and ingest it into the vector store.
    """
    if provider.lower() == "arxiv":
        from reserchium.parsers.arxiv import fetch_and_ingest_arxiv
        if refs:
            console.print("[yellow]Reference fetching is currently only supported via the Semantic Scholar provider. Ignoring --refs flag.[/yellow]")
        fetch_and_ingest_arxiv(arxiv_id=query, collection_name=collection)
    elif provider.lower() == "semanticscholar":
        from reserchium.parsers.semanticscholar import fetch_and_ingest_semanticscholar
        fetch_and_ingest_semanticscholar(query=query, collection_name=collection, fetch_references=refs)
    else:
        console.print("[bold red]Unsupported provider.[/bold red] Please choose between 'arxiv' or 'semanticscholar'.")
    
@app.command()
def query(question: str = typer.Argument(..., help="The question to ask against the parsed papers."), collection: str = typer.Option("papers", help="ChromaDB collection name.")):
    """
    Query the vector store and knowledge graph to answer a question.
    """
    console.print(f"[bold green]Query:[/bold green] {question}")
    engine = get_query_engine(collection_name=collection)
    response = engine.query(question)
    console.print(f"\n[bold magenta]Answer:[/bold magenta]\n{response}")

@app.command()
def lit_review(topic: str = typer.Argument(..., help="Topic to generate a literature review for"), collection: str = typer.Option("papers", help="ChromaDB collection name.")):
    """
    Synthesize findings across multiple papers in the database relevant to a topic.
    """
    from reserchium.engine.rag import get_query_engine
    console.print(f"[bold magenta]Generating Literature Review for Topic:[/bold magenta] {topic}")
    
    synthesis_prompt = (
        f"You are an expert researcher writing a literature review. "
        f"Synthesize the findings, methodologies, agreements, and contradictions "
        f"from the available documents related to the following topic: '{topic}'. "
        f"Format the review in markdown with headings for 'Overview', 'Key Findings', 'Methodologies', and 'Synthesis/Conclusion'. "
        f"Cite specific papers or authors mentioned in the context where possible."
    )
    
    engine = get_query_engine(collection_name=collection)
    response = engine.query(synthesis_prompt)
    console.print(f"\n[bold green]Literature Review:[/bold green]\n{response}")

@app.command()
def review(file_path: str = typer.Argument(..., help="Path to the research paper PDF to review."), collection: str = typer.Option("papers", help="ChromaDB collection to query against")):
    """
    Generate a comprehensive structured review of a given research paper.
    """
    from reserchium.engine.rag import get_query_engine
    console.print(f"[bold magenta]Generating review for:[/bold magenta] {file_path}")
    
    # We ask the user if they've ingested the paper already, if not we could ingest it here.
    # For now, we assume it's in the DB and query the engine.
    engine = get_query_engine(collection_name=collection)
    
    prompt = f"""
    Based on the ingested document '{file_path}', please provide a comprehensive academic review.
    Structure the review precisely with the following headings:
    
    ## 1. Summary
    (A brief paragraph summarizing the core idea of the paper)
    
    ## 2. Key Contributions
    (Bullet points of the main novelties)
    
    ## 3. Methodology
    (How did they achieve their results?)
    
    ## 4. Strengths & Weaknesses
    (Critical analysis of what they did well and what is lacking)
    """
    
    with console.status("[cyan]Analyzing paper...[/cyan]", spinner="dots"):
        response = engine.query(prompt)
        
    console.print(f"\n[bold magenta]Structured Review:[/bold magenta]\n{response}")

@app.command()
def evaluate(topic_or_file: str = typer.Argument(..., help="Topic or Paper Title to evaluate."), collection: str = typer.Option("papers", help="ChromaDB collection to query against")):
    """
    Generate a high-grade critical report assessing the solidity and validity of the paper or topic.
    """
    from reserchium.engine.rag import get_query_engine
    console.print(f"[bold red]Critically Evaluating:[/bold red] {topic_or_file}")
    
    evaluate_prompt = (
        f"You are a highly critical and expert peer reviewer. "
        f"I need a rigorous evaluation report concerning: '{topic_or_file}'. "
        f"Using your deep context and retrieved data, evaluate the scientific solidity, methodology, and validity. "
        f"Address the following strictly: "
        f"1. Core claims and their scientific plausibility. "
        f"2. Methodological rigor and potential theoretical/practical flaws. "
        f"3. Evaluation metrics and evidence solidity. "
        f"4. Missing baselines, assumptions, or biases. "
        f"5. Final verdict on whether the findings are trustworthy. "
        f"Be brutal but fair. Format as a professional Markdown report."
    )
    
    # We guarantee we use hybrid search here for the highest accuracy
    engine = get_query_engine(collection_name=collection, use_hybrid=True)
    with console.status("[cyan]Running critical assessment via Hybrid Search...[/cyan]", spinner="dots"):
        response = engine.query(evaluate_prompt)
    
    console.print(f"\n[bold green]Critical Evaluation Report:[/bold green]\n{response}")

@app.command()
def graph(export: bool = typer.Option(True, "--export", "-e", help="Export to HTML")):
    """
    Visualize or export the extracted Knowledge Graph.
    """
    console.print("[bold yellow]Processing Knowledge Graph...[/bold yellow]")
    if export:
        from reserchium.graph.visualize import export_to_html
        export_to_html()

@app.command()
def agent(objective: str = typer.Argument(..., help="The research objective for the agent (e.g., 'Search for recent papers on RAG and summarize them')")):
    """
    Launch an autonomous agent equipped with web search and shell tools to achieve a research objective.
    """
    console.print(f"[bold cyan]Launching Agent with objective:[/bold cyan] {objective}")
    
    # We need to initialize the LLM settings first
    from reserchium.engine.rag import configure_settings
    from llama_index.core import Settings
    from llama_index.core.agent import ReActAgent
    from reserchium.agent.tools import get_all_tools
    
    configure_settings()
    tools = get_all_tools()
    
    if not tools:
         console.print("[yellow]Warning: No tools are configured. The agent may not be able to perform external actions. Set BRAVE_API_KEY in .env to enable search.[/yellow]")
         
    import asyncio
    
    import asyncio
    
    async def run_agent_task(obj: str):
        # ReActAgent requires an LLM that supports reasoning.
        agent = ReActAgent(name="agent", tools=tools, llm=Settings.llm)
        console.print("[bold green]Agent started...[/bold green]")
        return await agent.run(user_msg=obj)
        
    try:
         # v0.14 agents inherit from BaseWorkflowAgent and are async natively
         response = asyncio.run(run_agent_task(objective))
         console.print(f"\n[bold magenta]Agent Final Response:[/bold magenta]\n{response}")
    except Exception as e:
         console.print(f"\n[bold red]Agent encountered an error:[/bold red] {e}")

def main():
    app()

if __name__ == "__main__":
    main()
