import os
import requests
from pathlib import Path
from rich.console import Console
from reserchium.parsers.pdf import get_document_nodes
from reserchium.engine.rag import ingest_documents
from reserchium.config import load_config

console = Console()

def fetch_and_ingest_semanticscholar(query: str, collection_name: str = "papers", download_dir: str = "./papers", fetch_references: bool = False):
    config = load_config()
    api_key = config.get("semanticscholar_api_key") or os.environ.get("SEMANTICSCHOLAR_API_KEY")
    headers = {}
    if api_key:
        headers["x-api-key"] = api_key
        console.print("[cyan]Using Premium Semantic Scholar API Key...[/cyan]")
    else:
        console.print("[yellow]Using free Semantic Scholar API. Rate limits may apply. Configure a key via `auth`.[/yellow]")

    console.print(f"[cyan]Searching Semantic Scholar for: {query}...[/cyan]")
    search_url = "https://api.semanticscholar.org/graph/v1/paper/search"
    # We ask for references.title and references.openAccessPdf so we can fetch them later if needed
    params = {"query": query, "limit": 1, "fields": "title,authors,openAccessPdf,url,year,references,references.title,references.openAccessPdf"}
    
    try:
        response = requests.get(search_url, headers=headers, params=params, timeout=15)
        if response.status_code != 200:
            console.print(f"[bold red]API Error:[/bold red] {response.status_code} - {response.text}")
            return
            
        data = response.json()
    except Exception as e:
        console.print(f"[bold red]Failed to connect to Semantic Scholar:[/bold red] {e}")
        return
        
    if not data.get("data"):
        console.print("[bold red]No papers found matching the query.[/bold red]")
        return
        
    paper = data["data"][0]
    title = paper.get("title")
    authors = [a["name"] for a in paper.get("authors", [])]
    oa_info = paper.get("openAccessPdf")
    
    console.print(f"[bold green]Found Paper:[/bold green] {title}")
    console.print(f"[dim]Authors: {', '.join(authors)}[/dim]")
    
    if not oa_info or not oa_info.get("url"):
        console.print("[bold red]No Open Access PDF link found for this paper via Semantic Scholar.[/bold red]")
        return
        
    pdf_url = oa_info["url"]
    
    # Download the PDF
    out_dir = Path(download_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    
    # Safe filename
    safe_title = "".join(c if c.isalnum() or c in (" ", "-") else "_" for c in title)[:50].strip().replace(" ", "_")
    pdf_filename = f"{safe_title}.pdf"
    pdf_path = out_dir / pdf_filename
    
    if not pdf_path.exists():
        console.print(f"[yellow]Downloading PDF from {pdf_url}...[/yellow]")
        dl_headers = {"User-Agent": "Mozilla/5.0"}
        try:
            pdf_response = requests.get(pdf_url, headers=dl_headers, stream=True, timeout=30)
            if pdf_response.status_code in [200, 206]:
                with open(pdf_path, 'wb') as f:
                    for chunk in pdf_response.iter_content(chunk_size=8192):
                        f.write(chunk)
            else:
                console.print(f"[bold red]Failed to download PDF. HTTP Status:[/bold red] {pdf_response.status_code}")
                return
        except Exception as e:
            console.print(f"[bold red]Error downloading PDF:[/bold red] {e}")
            return
    else:
        console.print(f"[blue]PDF already exists at {pdf_path}. Skipping download.[/blue]")
         
    # Ingest the document
    console.print("[cyan]Starting ingestion pipeline...[/cyan]")
    docs = get_document_nodes(str(pdf_path))
    
    if docs:
        for doc in docs:
            doc.metadata["source"] = "semanticscholar"
            doc.metadata["title"] = title
            doc.metadata["authors"] = ", ".join(authors)
            doc.metadata["url"] = paper.get("url", "")
            
        ingest_documents(docs, collection_name=collection_name)
        console.print(f"[bold green]Successfully fetched and ingested: {title}[/bold green]")
        
        # Fetch references if requested
        if fetch_references:
            references = paper.get("references", [])
            valid_refs = [r for r in references if r.get("openAccessPdf") and r["openAccessPdf"].get("url")]
            console.print(f"\n[bold magenta]Found {len(valid_refs)} references with Open Access PDFs.[bold magenta]")
            
            for i, ref in enumerate(valid_refs[:5]): # Cap at top 5 to prevent exploding the ingestion time
                ref_title = ref.get("title", f"Reference_{i}")
                ref_url = ref["openAccessPdf"]["url"]
                console.print(f"[cyan]---> Fetching Reference {i+1}/5:[/cyan] {ref_title}")
                
                 # Safe filename
                safe_ref_title = "".join(c if c.isalnum() or c in (" ", "-") else "_" for c in ref_title)[:50].strip().replace(" ", "_")
                ref_pdf_path = out_dir / f"{safe_ref_title}.pdf"
                
                if not ref_pdf_path.exists():
                    try:
                        ref_response = requests.get(ref_url, headers=dl_headers, stream=True, timeout=30)
                        if ref_response.status_code in [200, 206]:
                            with open(ref_pdf_path, 'wb') as f:
                                for chunk in ref_response.iter_content(chunk_size=8192):
                                    f.write(chunk)
                                    
                            console.print(f"     [green]Ingesting reference...[/green]")
                            ref_docs = get_document_nodes(str(ref_pdf_path))
                            if ref_docs:
                                for doc in ref_docs:
                                    doc.metadata["source"] = "semanticscholar_reference"
                                    doc.metadata["title"] = ref_title
                                    doc.metadata["original_paper"] = title
                                ingest_documents(ref_docs, collection_name=collection_name)
                        else:
                            console.print(f"     [red]Failed to download {ref_title}[/red]")
                    except Exception as e:
                        console.print(f"     [red]Error downloading reference:[/red] {e}")
                else:
                    console.print(f"     [blue]Reference already exists, skipping download.[/blue]")
                    
    else:
        console.print("[bold red]Failed to parse the downloaded PDF.[/bold red]")
