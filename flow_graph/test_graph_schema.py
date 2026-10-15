"""The graph must validate against the pydantic schema the exporters load (flow_graph/models.py)."""
import json, os
from flow_graph.models import PlantFlowGraph
def test_graph_validates():
    PlantFlowGraph.model_validate(json.load(open(os.path.join(os.path.dirname(__file__), 'plant_flow_graph.json'))))
