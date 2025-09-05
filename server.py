"""MCP server wrapping DSR functionality.

This module exposes tools and resources for communicating with the DSR
via FastMCP.
"""

from typing import Optional, Dict, Any, List
from fastmcp import FastMCP
from pydsr import DSRGraph

# DSR Configuration
AGENT_ID = 42                    # unique among agents
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
