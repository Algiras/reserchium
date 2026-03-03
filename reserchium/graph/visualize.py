import os
from pyvis.network import Network
from rich.console import Console

console = Console()

def export_to_html(graph_store_path="./kg_store.json", output_file="graph.html"):
    """
    Reads the persisted SimpleGraphStore JSON and uses PyVis to generate an interactive HTML graph.
    """
    if not os.path.exists(graph_store_path):
        console.print("[red]Knowledge graph store not found. Please ingest a document first.[/red]")
        return
        
    console.print(f"[cyan]Loading graph data from {graph_store_path}...[/cyan]")
    
    # SimpleGraphStore format under the hood is a dict: {"graph_dict": {"nodes": {}, "edges": {}}}
    import json
    try:
        with open(graph_store_path, 'r') as f:
            data = json.load(f)
    except Exception as e:
        console.print(f"[red]Error loading graph data: {e}[/red]")
        return
        
    # Build PyVis Network
    net = Network(height="750px", width="100%", bgcolor="#222222", font_color="white", directed=True)
    
    # In LlamaIndex's SimpleGraphStore, edges are typically stored mapping subjects to list of objects
    # Or in PropertyGraphStore format. Since PropertyGraphIndex uses a specific structure:
    # Let's inspect data safely
    
    nodes_added = set()
    
    if "graph_dict" in data:
       # Standard SimpleGraphStore structure
       edges = data.get("graph_dict", {}).get("edges", {})
       for subj, relations in edges.items():
            if subj not in nodes_added:
                net.add_node(subj, label=subj, title=subj)
                nodes_added.add(subj)
                
            for obj_list in relations.values():
                for obj in obj_list:
                    if obj not in nodes_added:
                        net.add_node(obj, label=obj, title=obj)
                        nodes_added.add(obj)
                    
                    # We don't have relation label in basic SimpleGraphStore easily, but PropertyGraphStore is different.
                    net.add_edge(subj, obj)
                    
    elif "node_dict" in data:
        # PropertyGraphStore structure
        nodes = data.get("node_dict", {})
        for node_id, node_info in nodes.items():
            label = node_info.get("name", node_id)
            if label not in nodes_added:
                net.add_node(label, label=label, title=label)
                nodes_added.add(label)
                
        # To get edges in PropertyGraphStore, it depends heavily on the exact version/format.
        # Fallback handling just structural visualization if detailed properties aren't easily parsed.
        # For simplicity, we assume nodes have connections in a generic way if we can't parse edges perfectly here.
        
    console.print(f"[yellow]Exporting interactive graph to {output_file}...[/yellow]")
    net.write_html(output_file)
    console.print(f"[bold green]Knowledge Graph exported successfully to {output_file}![/bold green]")
