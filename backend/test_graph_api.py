import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.config_new import get_config
from app.services.graph_builder import GraphBuilderService

config = get_config()
graph_id = "mirofish_2857f0813854472c"

print(f"Testing graph API for: {graph_id}")
print(f"LLM_API_KEY configured: {bool(config.LLM_API_KEY)}")

try:
    builder = GraphBuilderService(api_key=config.LLM_API_KEY)
    print("GraphBuilderService initialized successfully")
    
    print(f"\nFetching graph data...")
    graph_data = builder.get_graph_data(graph_id)
    
    print(f"\nSuccess!")
    print(f"Node count: {graph_data.get('node_count', 0)}")
    print(f"Edge count: {graph_data.get('edge_count', 0)}")
    
except Exception as e:
    print(f"\nError: {type(e).__name__}: {str(e)}")
    import traceback
    traceback.print_exc()
