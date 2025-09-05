"""MCP server wrapping DSR functionality.

This module exposes tools and resources for communicating with the DSR
via FastMCP.
"""

from typing import Optional
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


# @mcp.tool(
#     name='get_all_dsr_nodes',
#     description='Retrieve all nodes from the DSR graph',
#     tags={'dsr', 'nodes', 'graph', 'query'}
# )
# def get_all_nodes() -> dict:
#     """Return all nodes from the DSR graph with their basic information."""
#     if dsr_graph is None:
#         return {
#             'error': 'DSR not initialized',
#             'nodes': []
#         }

#     try:
#         # Get root node first
#         root_node = dsr_graph.get_node_root()
#         nodes_data = []

#         if root_node:
#             nodes_data.append({
#                 'id': root_node.id,
#                 'name': root_node.name,
#                 'type': root_node.type,
#                 'agent_id': root_node.agent_id,
#                 'is_root': True
#             })

#         return {
#             'nodes': nodes_data,
#             'count': len(nodes_data),
#             'dsr_name': DSR_NAME
#         }
#     except (AttributeError, RuntimeError) as e:
#         return {
#             'error': f'Error retrieving nodes: {str(e)}',
#             'nodes': []
#         }


# @mcp.tool(
#     name='get_dsr_nodes_legacy',
#     description='Legacy endpoint to retrieve all DSR nodes '
#                 '(deprecated, use get_all_dsr_nodes instead)',
#     tags={'dsr', 'nodes', 'legacy', 'deprecated'}
# )
# def get_nodes() -> dict:
#     """Return all nodes from the DSR (legacy endpoint)."""
#     if dsr_graph is None:
#         return {
#             'error': 'DSR not initialized',
#             'nodes': []
#         }

#     try:
#         # Get root node first
#         root_node = dsr_graph.get_node_root()
#         nodes_data = []

#         if root_node:
#             nodes_data.append({
#                 'id': root_node.id,
#                 'name': root_node.name,
#                 'type': root_node.type,
#                 'agent_id': root_node.agent_id,
#                 'is_root': True
#             })

#         return {
#             'nodes': nodes_data,
#             'count': len(nodes_data),
#             'dsr_name': DSR_NAME
#         }
#     except (AttributeError, RuntimeError) as e:
#         return {
#             'error': f'Error retrieving nodes: {str(e)}',
#             'nodes': []
#         }


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
                'id': node.id,
                'name': node.name,
                'type': node.type
            })
            print(node)

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
def get_node_details(node_identifier: int) -> dict:
    """Return detailed information about a specific node by ID.

    Args:
        node_identifier (int): The ID of the node to retrieve.

    Returns:
        dict: A dictionary containing the node details or an error message.
    """
    if dsr_graph is None:
        return {
            'error': 'DSR not initialized',
            'node': None
        }

    try:
        node = dsr_graph.get_node(node_identifier)

        if node is None:
            return {
                'error': f'Node {node_identifier} not found',
                'node': None
            }

        # Extract attributes
        attributes = {}
        if hasattr(node, 'attrs'):
            try:
                for attr_name in node.attrs:
                    try:
                        attr_obj = node.attrs[attr_name]
                        if hasattr(attr_obj, 'value'):
                            value_str = str(attr_obj.value)
                            type_name = type(attr_obj.value).__name__
                        else:
                            value_str = str(attr_obj)
                            type_name = type(attr_obj).__name__

                        timestamp = None
                        if hasattr(attr_obj, 'timestamp'):
                            timestamp = attr_obj.timestamp

                        attributes[attr_name] = {
                            'value': value_str,
                            'type': type_name,
                            'timestamp': timestamp
                        }
                    except Exception as e:
                        attributes[attr_name] = {
                            'error': f'Could not access attribute: {str(e)}',
                            'type': 'unknown'
                        }
            except Exception as e:
                attributes = {
                    'error': f'Could not access attributes: {str(e)}'
                }

        # Extraer edges de forma segura
        edges = []
        if hasattr(node, 'edges'):
            try:
                # En DSR, node.edges es un diccionario con clave (node_id, edge_type)
                for edge_key, edge in node.edges.items():
                    to_node_id = 'unknown'
                    edge_type = 'unknown'

                    # La clave es una tupla (node_id, edge_type)
                    if isinstance(edge_key, tuple) and len(edge_key) >= 2:
                        to_node_id = edge_key[0]
                        edge_type = edge_key[1]

                    # El edge también tiene propiedades origin y destination
                    origin_id = node.id  # Por defecto el nodo actual
                    destination_id = to_node_id

                    if hasattr(edge, 'origin'):
                        origin_id = edge.origin
                    if hasattr(edge, 'destination'):
                        destination_id = edge.destination

                    # Extraer atributos del edge si los tiene
                    edge_attrs = {}
                    if hasattr(edge, 'attrs'):
                        try:
                            for attr_name in edge.attrs:
                                try:
                                    attr_obj = edge.attrs[attr_name]
                                    if hasattr(attr_obj, 'value'):
                                        edge_attrs[attr_name] = {
                                            'value': str(attr_obj.value),
                                            'type': type(attr_obj.value).__name__
                                        }
                                except Exception:
                                    edge_attrs[attr_name] = {
                                        'error': 'Could not access'}
                        except Exception:
                            edge_attrs = {
                                'error': 'Could not access edge attributes'}

                    edges.append({
                        'to': destination_id,
                        'from': origin_id,
                        'type': edge_type,
                        'attributes': edge_attrs
                    })
            except Exception as e:
                edges = [{'error': f'Could not access edges: {str(e)}'}]

        return {
            'node': {
                'id': node.id,
                'name': node.name,
                'type': node.type,
                'agent_id': node.agent_id,
                'attributes': attributes,
                'edges': edges
            },
            'dsr_name': DSR_NAME
        }
    except (AttributeError, RuntimeError) as e:
        return {
            'error': f'Error retrieving node details: {str(e)}',
            'node': None
        }

# @mcp.tool(
#     name='search_nodes',
#     description='Search for nodes in the DSR by name pattern or attributes',
#     tags={'dsr', 'search', 'nodes', 'query', 'filter'}
# )
# def search_nodes(search_term: str, search_type: str = 'name') -> dict:
#     """Search for nodes by name pattern or other criteria.

#     Args:
#         search_term: The term to search for
#         search_type: Type of search ('name', 'type', 'all')
#     """
#     if dsr_graph is None:
#         return {
#             'error': 'DSR not initialized',
#             'results': []
#         }

#     try:
#         results = []
#         # This is a simplified search - in a real implementation,
#         # you would use actual DSR search capabilities

#         if search_type == 'name':
#             # Search by name (simplified - would need actual DSR API)
#             results.append({
#                 'message': (f'Searching for nodes with name containing: '
#                            f'{search_term}'),
#                 'search_type': search_type,
#                 'term': search_term
#             })
#         elif search_type == 'type':
#             # Delegate to get_nodes_by_type function directly
#             if dsr_graph is None:
#                 return {
#                     'error': 'DSR not initialized',
#                     'nodes': []
#                 }

#             try:
#                 nodes = dsr_graph.get_nodes_by_type(search_term)
#                 nodes_data = []

#                 for node in nodes:
#                     nodes_data.append({
#                         'id': node.id,
#                         'name': node.name,
#                         'type': node.type,
#                         'agent_id': node.agent_id
#                     })

#                 return {
#                     'nodes': nodes_data,
#                     'count': len(nodes_data),
#                     'filter_type': search_term,
#                     'dsr_name': DSR_NAME
#                 }
#             except (AttributeError, RuntimeError) as e:
#                 return {
#                     'error': f'Error retrieving nodes by type: {str(e)}',
#                     'nodes': []
#                 }
#         else:
#             results.append({
#                 'message': f'General search for: {search_term}',
#                 'search_type': search_type,
#                 'term': search_term
#             })

#         return {
#             'results': results,
#             'count': len(results),
#             'search_term': search_term,
#             'search_type': search_type
#         }
#     except (AttributeError, RuntimeError) as e:
#         return {
#             'error': f'Error searching nodes: {str(e)}',
#             'results': []
#         }


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
