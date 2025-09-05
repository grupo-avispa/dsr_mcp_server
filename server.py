"""MCP server wrapping DSR functionality.

This module exposes tools and resources for communicating with the DSR
via FastMCP.
"""

from typing import Optional, Dict, Any, List
from fastmcp import FastMCP, Context
from pydsr import DSRGraph, Node, Edge, Attribute

# DSR Configuration
AGENT_ID = 42             # unique among agents
DSR_NAME = 'mcp_server'   # target DSR graph name

# Global DSR instance
dsr_graph: Optional[DSRGraph] = None

# Create MCP application
mcp = FastMCP('dsr-mcp-server')


def _init_dsr() -> bool:
    """Initialize DSR connection.

    Returns:
        bool: True if connection successful, False otherwise.
    """
    global dsr_graph
    try:
        dsr_graph = DSRGraph(0, DSR_NAME, AGENT_ID)
        return True
    except (ImportError, RuntimeError, ConnectionError) as e:
        print(f'Error initializing DSR: {e}')
        return False


def _check_dsr_connection() -> dict:
    """Check DSR connection status.

    Returns:
        dict: Connection status information.
    """
    if dsr_graph is None:
        return {
            'connected': False,
            'message': 'DSR not initialized',
            'agent_id': AGENT_ID,
            'dsr_name': DSR_NAME
        }

    try:
        # Try to get root node to test connection
        root_node = dsr_graph.get_node_root()
        return {
            'connected': True,
            'message': 'DSR connection active',
            'agent_id': AGENT_ID,
            'dsr_name': DSR_NAME,
            'root_node_id': root_node.id if root_node else None
        }
    except (AttributeError, RuntimeError) as e:
        return {
            'connected': False,
            'message': f'DSR connection error: {str(e)}',
            'agent_id': AGENT_ID,
            'dsr_name': DSR_NAME
        }


def _get_node_attributes(node) -> Dict[str, Dict[str, str]]:
    """
    Return a dictionary with all attributes of a node, excluding internal ones.

    Args:
        node: Node object from DSRGraph.

    Returns:
        Dict[str, Dict[str, str]]: Dictionary of attribute names and
        their details (value, type, timestamp).
    """
    EXCLUDED_NODE_ATTRIBUTES: List[str] = [
        'color', 'depth', 'height', 'level', 'number', 'parent',
        'pos_x', 'pos_y', 'texture', 'width'
    ]
    attributes: Dict[str, Dict[str, str]] = {}
    if hasattr(node, 'attrs'):
        for attr_name in node.attrs:
            if attr_name in EXCLUDED_NODE_ATTRIBUTES:
                continue
            try:
                attributes[attr_name] = {
                    'value': str(node.attrs[attr_name].value),
                    'type': type(node.attrs[attr_name].value).__name__,
                    'timestamp': str(node.attrs[attr_name].timestamp)
                }
            except Exception as e:
                attributes[attr_name] = {
                    'error': f'Could not access attribute: {e}',
                    'type': 'unknown'
                }
    return attributes


def _get_node_edges(node) -> List[Dict[str, Any]]:
    """
    Return a list of dictionaries with all edges of a node.

    Args:
        node: Node object from DSRGraph.

    Returns:
        List[Dict[str, Any]]: List of edge details (origin, destination,
        type, attributes).
    """
    edges = []
    if hasattr(node, 'get_edges'):
        try:
            node_edges = node.get_edges()
            for edge in node_edges:
                origin_id = edge.origin
                destination_id = edge.destination
                edge_type = edge.type
                edge_attrs: Dict = {}
                if hasattr(edge, 'attrs'):
                    for attr_name in edge.attrs:
                        try:
                            edge_attrs[attr_name] = {
                                'value': str(edge.attrs[attr_name].value),
                                'type': type(edge.attrs[attr_name].value).
                                __name__,
                            }
                        except Exception:
                            edge_attrs[attr_name] = {
                                'error': 'Could not access'
                            }
                edges.append({
                    'to': str(destination_id),
                    'from': str(origin_id),
                    'type': str(edge_type),
                    'attributes': edge_attrs,
                })
        except Exception as e:
            edges = [{'error': f'Could not access edges: {e}'}]
    return edges


@mcp.tool(
    name='initialize_dsr_connection',
    description='Initialize or reinitialize the DSR connection',
    tags={'dsr', 'initialization', 'connection', 'setup'}
)
def initialize_dsr_connection() -> dict:
    """Initialize or reinitialize the DSR connection."""
    if _init_dsr():
        status = _check_dsr_connection()
        return {
            'success': True,
            'message': 'DSR connection initialized successfully',
            'status': status
        }
    else:
        return {
            'success': False,
            'message': 'Failed to initialize DSR',
            'error': 'Unknown error'
        }


@mcp.tool(
    name='check_dsr_connection',
    description='Check DSR connection and return status information',
    tags={'dsr', 'connection', 'health', 'status', 'configuration'}
)
def check_dsr() -> str:
    """Check DSR connection and return status information."""
    status = _check_dsr_connection()
    if status['connected']:
        root_id = status.get('root_node_id', 'Unknown')
        return (f'DSR Status: Connected\n'
                f'Agent ID: {status["agent_id"]}\n'
                f'DSR Name: {status["dsr_name"]}\n'
                f'Root Node ID: {root_id}')
    else:
        return (f'DSR Status: Disconnected\n'
                f'Reason: {status["message"]}\n'
                f'Agent ID: {status["agent_id"]}\n'
                f'DSR Name: {status["dsr_name"]}')


@mcp.tool(
    name='get_all_nodes',
    description='Retrieve all nodes from the DSR graph',
    tags={'dsr', 'nodes', 'graph', 'query'}
)
def get_all_nodes() -> dict:
    """
    Return all nodes from the DSR graph with their basic information.

    Returns:
        dict: Dictionary containing a list of nodes and their basic info.
    """
    if dsr_graph is None:
        return {
            'error': 'DSR not initialized',
            'nodes': []
        }
    try:
        nodes = dsr_graph.get_nodes()
        nodes_data = []
        for node in nodes:
            nodes_data.append({
                'id': str(node.id),
                'name': node.name,
                'type': node.type,
                'agent_id': getattr(node, 'agent_id', None)
            })
        return {
            'nodes': nodes_data,
            'count': len(nodes_data),
            'dsr_name': DSR_NAME
        }
    except (AttributeError, RuntimeError) as e:
        return {
            'error': f'Error retrieving nodes: {str(e)}',
            'nodes': []
        }


@mcp.tool(
    name='get_nodes_by_type',
    description='Retrieve DSR nodes filtered by their type',
    tags={'dsr', 'nodes', 'filter', 'type'}
)
def get_nodes_by_type(node_type: str) -> dict:
    """Return nodes filtered by their type from the DSR graph."""
    if dsr_graph is None:
        return {
            'error': 'DSR not initialized',
            'nodes': []
        }

    try:
        nodes = dsr_graph.get_nodes_by_type(node_type)
        nodes_data = []

        for node in nodes:
            nodes_data.append({
                'id': str(node.id),
                'name': node.name,
                'type': node.type
            })

        return {
            'nodes': nodes_data,
            'count': len(nodes_data),
            'type': node_type
        }
    except (AttributeError, RuntimeError) as e:
        return {
            'error': f'Error retrieving nodes by type: {str(e)}',
            'nodes': []
        }


@mcp.tool(
    name='get_node_details',
    description='Get detailed information about a specific DSR node '
                'including attributes and edges',
    tags={'dsr', 'node', 'details', 'attributes', 'edges'}
)
def get_node_details(node_identifier: str) -> dict:
    """Return detailed information about a specific node by ID.

    Args:
        node_identifier (str): The ID of the node to retrieve.

    Returns:
        dict: A dictionary containing the node details or an error message.
    """
    if dsr_graph is None:
        return {
            'error': 'DSR not initialized',
            'node': None
        }

    try:
        node = dsr_graph.get_node(int(node_identifier))
        if node is None:
            return {
                'error': f'Node {node_identifier} not found',
                'node': None
            }
        attributes = _get_node_attributes(node)
        edges = _get_node_edges(node)
        return {
            'node': {
                'id': str(node.id),
                'name': node.name,
                'type': node.type,
                'edges': edges,
                'attributes': attributes
            }
        }
    except (AttributeError, RuntimeError) as e:
        return {
            'error': f'Error retrieving node details: {str(e)}',
            'node': None
        }


@mcp.tool(
    name='insert_node',
    description='Insert a new node into the DSR graph.',
    tags={'dsr', 'node', 'insert', 'graph'}
)
async def insert_node(name: str, node_type: str) -> dict:
    """
    Insert a new node into the DSR graph.

    Args:
        name (str): The name of the node to insert.
        node_type (str): The type of the node to insert.

    Returns:
        dict: Dictionary with the result of the insertion or error message.
    """
    if dsr_graph is None:
        return {
            'error': 'DSR not initialized',
            'node': None
        }
    try:
        node = Node(AGENT_ID, node_type, name)
        node_id = dsr_graph.insert_node(node)
        return {
            'success': True,
            'message': 'Node inserted successfully.',
            'node_id': str(node_id),
            'node_name': name,
            'node_type': node_type
        }

    except (AttributeError, RuntimeError, ValueError) as e:
        return {
            'success': False,
            'error': f'Error inserting node: {str(e)}',
            'node': None
        }


@mcp.tool(
    name='insert_edge',
    description='Insert a new edge between two nodes in the DSR graph',
    tags={'dsr', 'edge', 'insert', 'graph'}
)
def insert_edge(origin_id: str, destination_id: str, edge_type: str) -> dict:
    """
    Insert a new edge between two nodes in the DSR graph.

    Args:
        origin_id (str): ID of the origin node.
        destination_id (str): ID of the destination node.
        edge_type (str): Type of the edge to insert.

    Returns:
        dict: Dictionary with the result of the insertion or error message.
    """
    if dsr_graph is None:
        return {
            'error': 'DSR not initialized',
            'edge': None
        }
    try:
        edge = Edge(int(origin_id), int(destination_id), edge_type, AGENT_ID)
        success = dsr_graph.insert_or_assign_edge(edge)
        if success:
            return {
                'success': True,
                'message': 'Edge inserted successfully',
                'origin_id': origin_id,
                'destination_id': destination_id,
                'edge_type': edge_type
            }
        else:
            return {
                'success': False,
                'error': 'Failed to insert edge',
                'edge': None
            }
    except (AttributeError, RuntimeError, ValueError) as e:
        return {
            'success': False,
            'error': f'Error inserting edge: {str(e)}',
            'edge': None
        }


@mcp.tool(
    name='update_node',
    description='Update a node with new attributes in the DSR graph',
    tags={'dsr', 'node', 'update', 'graph'}
)
def update_node(node_id: str, attribute_name: str,
                attribute_value: str,
                attribute_type: str = 'string') -> dict:
    """
    Update a node with new attributes in the DSR graph.

    Uses DSRGraph.update_node method.

    Args:
        node_id (str): ID of the node to update.
        attribute_name (str): Name of the attribute to update.
        attribute_value (str): Value of the attribute.
        attribute_type (str): Type of the attribute (string, int, float, bool).

    Returns:
        dict: Dictionary with the result of the update or error message.
    """
    if dsr_graph is None:
        return {
            'error': 'DSR not initialized',
            'node': None
        }
    try:
        # Get the existing node
        node = dsr_graph.get_node(int(node_id))
        if node is None:
            return {
                'error': f'Node {node_id} not found',
                'node': None
            }

        # Convert attribute value to the appropriate type
        converted_value: Any = attribute_value
        if attribute_type == 'int':
            converted_value = int(attribute_value)
        elif attribute_type == 'float':
            converted_value = float(attribute_value)
        elif attribute_type == 'bool':
            converted_value = attribute_value.lower() in (
                'true', '1', 'yes', 'on')

        # Create DSR Attribute and add it to the node
        attribute = Attribute(converted_value, AGENT_ID)
        node.attrs[attribute_name] = attribute

        # Reference: DSRGraph.update_node(node: Node)
        success = dsr_graph.update_node(node)
        if success:
            return {
                'success': True,
                'message': 'Node updated successfully',
                'node_id': node_id,
                'attribute_name': attribute_name,
                'attribute_value': str(converted_value),
                'attribute_type': attribute_type
            }
        else:
            return {
                'success': False,
                'error': 'Failed to update node',
                'node': None
            }
    except (AttributeError, RuntimeError, ValueError) as e:
        return {
            'success': False,
            'error': f'Error updating node: {str(e)}',
            'node': None
        }


@mcp.tool(
    name='insert_edge_attribute',
    description='Insert or update an attribute for an edge in the DSR graph',
    tags={'dsr', 'edge', 'attribute', 'insert', 'graph'}
)
def insert_edge_attribute(origin_id: str, destination_id: str,
                          attribute_name: str, attribute_value: str,
                          attribute_type: str = 'string') -> dict:
    """
    Insert or update an attribute for an edge in the DSR graph.

    Args:
        origin_id (str): ID of the origin node.
        destination_id (str): ID of the destination node.
        attribute_name (str): Name of the attribute to insert/update.
        attribute_value (str): Value of the attribute.
        attribute_type (str): Type of the attribute (string, int, float, bool).

    Returns:
        dict: Dictionary with the result of the insertion or error message.
    """
    if dsr_graph is None:
        return {
            'error': 'DSR not initialized',
            'attribute': None
        }
    try:
        # Convert attribute value to the appropriate type
        converted_value: Any = attribute_value
        if attribute_type == 'int':
            converted_value = int(attribute_value)
        elif attribute_type == 'float':
            converted_value = float(attribute_value)
        elif attribute_type == 'bool':
            converted_value = attribute_value.lower() in (
                'true', '1', 'yes', 'on')

        success = dsr_graph.insert_edge_attribute(
            int(origin_id), int(destination_id),
            attribute_name, converted_value)
        if success:
            return {
                'success': True,
                'message': 'Edge attribute inserted successfully',
                'origin_id': origin_id,
                'destination_id': destination_id,
                'attribute_name': attribute_name,
                'attribute_value': str(converted_value),
                'attribute_type': attribute_type
            }
        else:
            return {
                'success': False,
                'error': 'Failed to insert edge attribute',
                'attribute': None
            }
    except (AttributeError, RuntimeError, ValueError) as e:
        return {
            'success': False,
            'error': f'Error inserting edge attribute: {str(e)}',
            'attribute': None
        }


@mcp.tool(
    name='delete_node',
    description='Delete a node from the DSR graph',
    tags={'dsr', 'node', 'delete', 'graph'}
)
def delete_node(node_id: str) -> dict:
    """
    Delete a node from the DSR graph.

    Args:
        node_id (str): ID of the node to delete.

    Returns:
        dict: Dictionary with the result of the deletion or error message.
    """
    if dsr_graph is None:
        return {
            'error': 'DSR not initialized',
            'node': None
        }
    try:
        # Reference: DSRGraph.delete_node(node_id)
        success = dsr_graph.delete_node(int(node_id))
        if success:
            return {
                'success': True,
                'message': 'Node deleted successfully',
                'node_id': node_id
            }
        else:
            return {
                'success': False,
                'error': 'Failed to delete node',
                'node': None
            }
    except (AttributeError, RuntimeError, ValueError) as e:
        return {
            'success': False,
            'error': f'Error deleting node: {str(e)}',
            'node': None
        }


@mcp.tool(
    name='delete_edge',
    description='Delete an edge from the DSR graph',
    tags={'dsr', 'edge', 'delete', 'graph'}
)
def delete_edge(origin_id: str, destination_id: str, edge_type: str) -> dict:
    """
    Delete an edge from the DSR graph.

    Args:
        origin_id (str): ID of the origin node.
        destination_id (str): ID of the destination node.
        edge_type (str): Type of the edge to delete.

    Returns:
        dict: Dictionary with the result of the deletion or error message.
    """
    if dsr_graph is None:
        return {
            'error': 'DSR not initialized',
            'edge': None
        }
    try:
        # Reference: DSRGraph.delete_edge(origin_id, destination_id, edge_type)
        success = dsr_graph.delete_edge(
            int(origin_id), int(destination_id), edge_type)
        if success:
            return {
                'success': True,
                'message': 'Edge deleted successfully',
                'origin_id': origin_id,
                'destination_id': destination_id,
                'edge_type': edge_type
            }
        else:
            return {
                'success': False,
                'error': 'Failed to delete edge',
                'edge': None
            }
    except (AttributeError, RuntimeError, ValueError) as e:
        return {
            'success': False,
            'error': f'Error deleting edge: {str(e)}',
            'edge': None
        }


def main() -> None:
    """Run the MCP server.

    Notes
    -----
    Default transport is http for local MCP integration.
    """
    # Initialize DSR connection on startup
    print(f'Initializing DSR connection to {DSR_NAME}...')
    if _init_dsr():
        print('DSR initialized successfully')
    else:
        print('Warning: Could not initialize DSR on startup')

    mcp.run(transport='http', host='127.0.0.1', port=3000)
    # mcp.run()


if __name__ == '__main__':
    main()
