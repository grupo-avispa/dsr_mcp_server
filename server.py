# Copyright (c) 2025 Alberto J. Tudela Roldán
# Copyright (c) 2025 Grupo Avispa, DTE, Universidad de Málaga
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""MCP server wrapping DSR functionality.

This module exposes tools and resources for communicating with the DSR
via FastMCP.
"""

from typing import Optional, Dict, Any, List
from fastmcp import FastMCP, Context
from fastmcp.utilities.logging import get_logger
from pydsr import DSRGraph, Node, Edge, Attribute

# DSR Configuration
AGENT_ID = 42             # unique among agents
DSR_NAME = 'mcp_server'   # target DSR graph name

# Global DSR instance
dsr_graph: Optional[DSRGraph] = None

# Create MCP application
mcp = FastMCP('dsr-mcp-server')

# Get logger
logger = get_logger(__name__)


def _create_success_response(
    message: str,
    data: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Create a standardized success response.

    Args:
        message (str): Success message.
        data (Optional[Dict[str, Any]]): Additional data to include.

    Returns:
        Dict[str, Any]: Standardized success response.
    """
    response = {
        'success': True,
        'message': message
    }
    if data:
        response.update(data)
    return response


def _create_error_response(
    error: str,
    details: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Create a standardized error response.

    Args:
        error (str): Error message.
        details (Optional[Dict[str, Any]]): Additional error details.

    Returns:
        Dict[str, Any]: Standardized error response.
    """
    response = {
        'success': False,
        'error': error
    }
    if details:
        response.update(details)
    return response


def _init_dsr() -> bool:
    """
    Initialize DSR connection.

    Returns:
        bool: True if connection successful, False otherwise.
    """
    global dsr_graph
    try:
        dsr_graph = DSRGraph(0, DSR_NAME, AGENT_ID)
        return True
    except (ImportError, RuntimeError, ConnectionError) as e:
        logger.error(f'Error initializing DSR: {e}')
        return False


def _check_dsr_connection() -> dict:
    """
    Check DSR connection status.

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


def _get_node_attributes(node: Node) -> Dict[str, Dict[str, str]]:
    """
    Retrieve all attributes of a node.

    Args:
        node (Node): Node object from DSRGraph.

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
            except (AttributeError, KeyError, TypeError) as e:
                attributes[attr_name] = {
                    'error': f'Could not access attribute: {e}',
                    'type': 'unknown'
                }
    return attributes


def _get_node_edges(node: Node) -> List[Dict[str, Any]]:
    """
    Retrieve all outgoing and incoming edges of a node.

    Args:
        node (Node): Node object from DSRGraph.

    Returns:
        List[Dict[str, Any]]: List of edge details (origin, destination,
        type, attributes).
    """
    edges = []

    # Try to get edges using the edges property (node.fano() in C++)
    if hasattr(node, 'edges'):
        try:
            # Access the edges map directly
            for edge in node.edges.values():
                edge_attrs: Dict = {}
                if hasattr(edge, 'attrs'):
                    for attr_name in edge.attrs:
                        try:
                            edge_attrs[attr_name] = {
                                'value': str(edge.attrs[attr_name].value),
                                'type': type(
                                    edge.attrs[attr_name].value).__name__,
                            }
                        except (AttributeError, KeyError, TypeError):
                            edge_attrs[attr_name] = {
                                'error': 'Could not access'
                            }
                edges.append({
                    'origin': str(edge.origin),
                    'destination': str(edge.destination),
                    'type': str(edge.type),
                    'attributes': edge_attrs,
                })
        except (AttributeError, RuntimeError) as e:
            # Fallback: try using get_edges method if available
            if hasattr(node, 'get_edges'):
                try:
                    for edge in node.get_edges():
                        fallback_edge_attrs: Dict = {}
                        if hasattr(edge, 'attrs'):
                            for attr_name in edge.attrs:
                                try:
                                    fallback_edge_attrs[attr_name] = {
                                        'value': str(
                                            edge.attrs[attr_name].value),
                                        'type': type(
                                            edge.attrs[attr_name].value
                                        ).__name__,
                                    }
                                except (AttributeError, KeyError, TypeError):
                                    fallback_edge_attrs[attr_name] = {
                                        'error': 'Could not access'
                                    }
                        edges.append({
                            'origin': str(edge.origin),
                            'destination': str(edge.destination),
                            'type': str(edge.type),
                            'attributes': fallback_edge_attrs,
                        })
                except (AttributeError, RuntimeError):
                    edges = [{'error': f'Could not access edges: {e}'}]
            else:
                edges = [{'error': f'Could not access edges: {e}'}]

    # Additionally, use DSRGraph to get incoming edges to this node
    if dsr_graph is not None:
        try:
            # Get edges that point to this node (incoming edges)
            incoming_edges = dsr_graph.get_edges_to_id(node.id)
            for edge in incoming_edges:
                # Check if this edge is already in our list to avoid duplicates
                edge_exists = any(
                    e.get('from') == str(edge.origin) and
                    e.get('to') == str(edge.destination) and
                    e.get('type') == str(edge.type)
                    for e in edges if 'error' not in e
                )

                if not edge_exists:
                    incoming_edge_attrs: Dict = {}
                    if hasattr(edge, 'attrs'):
                        for attr_name in edge.attrs:
                            try:
                                incoming_edge_attrs[attr_name] = {
                                    'value': str(edge.attrs[attr_name].value),
                                    'type': type(
                                        edge.attrs[attr_name].value).__name__,
                                }
                            except (AttributeError, KeyError, TypeError):
                                incoming_edge_attrs[attr_name] = {
                                    'error': 'Could not access'
                                }
                    edges.append({
                        'origin': str(edge.origin),
                        'destination': str(edge.destination),
                        'type': str(edge.type),
                        'attributes': incoming_edge_attrs,
                    })
        except (AttributeError, RuntimeError):
            # If we couldn't get incoming edges, that's not necessarily
            # an error since we might have gotten the outgoing ones
            # successfully
            pass

    return edges


@mcp.tool(
    enabled=False,
    name='initialize_dsr_connection',
    description='Initialize or reinitialize the DSR connection',
    tags={'dsr', 'graph', 'initialization', 'connection', 'setup'}
)
async def initialize_dsr_connection(ctx: Context) -> dict:
    """Initialize or reinitialize the DSR connection."""
    await ctx.info(f'Initializing DSR connection to {DSR_NAME}...')

    if _init_dsr():
        status = _check_dsr_connection()
        status_msg = 'DSR connection initialized successfully'
        await ctx.info(status_msg)
        return _create_success_response(status_msg, {'status': status})
    else:
        error_msg = 'Failed to initialize DSR connection'
        await ctx.error(error_msg)
        return _create_error_response(error_msg, {'error': 'Unknown error'})


@mcp.tool(
    name='check_dsr_connection',
    description='Check DSR connection and return status information',
    tags={'dsr', 'graph', 'connection', 'health', 'status', 'configuration'}
)
async def check_dsr(ctx: Context) -> str:
    """Check DSR connection and return status information."""
    await ctx.info('Checking DSR connection status...')

    status = _check_dsr_connection()
    if status['connected']:
        root_id = status.get('root_node_id', 'Unknown')
        await ctx.info('DSR connection is active')
        return (f'DSR Status: Connected\n'
                f'Agent ID: {status["agent_id"]}\n'
                f'DSR Name: {status["dsr_name"]}\n'
                f'Root Node ID: {root_id}')
    else:
        await ctx.warning(f'DSR connection is not active: {status["message"]}')
        return (f'DSR Status: Disconnected\n'
                f'Reason: {status["message"]}\n'
                f'Agent ID: {status["agent_id"]}\n'
                f'DSR Name: {status["dsr_name"]}')


@mcp.tool(
    name='get_all_nodes',
    description='Retrieve all nodes from the DSR graph',
    tags={'dsr', 'graph', 'nodes', 'query'}
)
async def get_all_nodes(ctx: Context) -> dict:
    """
    Return all nodes from the DSR graph with their basic information.

    Returns:
        dict: Dictionary containing a list of nodes and their basic info.
    """
    await ctx.info('Retrieving all nodes from DSR graph...')

    if dsr_graph is None:
        error_msg = 'DSR not initialized'
        await ctx.error(error_msg)
        return _create_error_response(error_msg, {'nodes': []})

    try:
        nodes_data = []
        for node in dsr_graph.get_nodes():
            nodes_data.append({
                'id': str(node.id),
                'name': node.name,
                'type': node.type,
                'agent_id': getattr(node, 'agent_id', None)
            })

        await ctx.info(f'Retrieved {len(nodes_data)} nodes successfully')
        return _create_success_response(
            f'Retrieved {len(nodes_data)} nodes',
            {
                'nodes': nodes_data,
                'count': len(nodes_data),
                'dsr_name': DSR_NAME
            }
        )
    except (AttributeError, RuntimeError) as e:
        error_msg = f'Error retrieving nodes: {str(e)}'
        await ctx.error(error_msg)
        return _create_error_response(error_msg, {'nodes': []})


@mcp.tool(
    name='get_nodes_by_type',
    description="""Retrieve DSR nodes filtered by their type (e.g. robot,
        person, human, battery, room). Helps narrow search before checking
        relationships.
        Intents: "Find all humans", "People near the robot"
        (then call get_node_details per node).
        Combine with get_node_details to inspect edges
        (has, is, is_with) for presence / proximity reasoning.""",
    tags={'dsr', 'graph', 'nodes', 'filter', 'type'}
)
async def get_nodes_by_type(node_type: str, ctx: Context) -> dict:
    """
    Retrieve nodes filtered by their type from the DSR graph.

    Parameters:
        node_type (str): The type of nodes to retrieve
            (e.g., robot, person, human, battery, room).
        ctx (Context): The MCP context object.

    Returns:
        dict: Standardized response containing a list of nodes of the
            specified type and their basic information, or an error message.
    """
    await ctx.info(f'Retrieving nodes of type: {node_type}')

    if dsr_graph is None:
        error_msg = 'DSR not initialized'
        await ctx.error(error_msg)
        return _create_error_response(error_msg, {'nodes': []})

    try:
        nodes = dsr_graph.get_nodes_by_type(node_type)
        nodes_data = []

        for node in nodes:
            nodes_data.append({
                'id': str(node.id),
                'name': node.name,
                'type': node.type
            })

        await ctx.info(
            f'Retrieved {len(nodes_data)} nodes of type {node_type}'
        )
        return _create_success_response(
            f'Retrieved {len(nodes_data)} nodes of type {node_type}',
            {
                'nodes': nodes_data,
                'count': len(nodes_data),
                'type': node_type
            }
        )
    except (AttributeError, RuntimeError) as e:
        error_msg = f'Error retrieving nodes by type: {str(e)}'
        await ctx.error(error_msg)
        return _create_error_response(error_msg, {'nodes': []})


@mcp.tool(
    name='get_node_details',
    description='Get detailed information about a specific DSR node '
                'including attributes and edges',
    tags={'dsr', 'graph', 'node', 'details', 'attributes', 'edges'}
)
async def get_node_details(node_identifier: str, ctx: Context) -> dict:
    """
    Return detailed information about a specific node by ID.

    Args:
        node_identifier (str): The ID of the node to retrieve.

    Returns:
        dict: A dictionary containing the node details or an error message.
    """
    await ctx.info(f'Retrieving details for node: {node_identifier}')

    if dsr_graph is None:
        error_msg = 'DSR not initialized'
        await ctx.error(error_msg)
        return _create_error_response(error_msg, {'nodes': []})

    try:
        node = dsr_graph.get_node(int(node_identifier))
        if node is None:
            error_msg = f'Node {node_identifier} not found'
            await ctx.warning(error_msg)
            return _create_error_response(error_msg, {'node': None})

        attributes = _get_node_attributes(node)
        edges = _get_node_edges(node)

        await ctx.info(f'Retrieved details for node {node_identifier}')
        return _create_success_response(
            f'Retrieved details for node {node_identifier}',
            {
                'node': {
                    'id': str(node.id),
                    'name': node.name,
                    'type': node.type,
                    'edges': edges,
                    'attributes': attributes
                }
            }
        )
    except (AttributeError, RuntimeError) as e:
        error_msg = f'Error retrieving node details: {str(e)}'
        await ctx.error(error_msg)
        return _create_error_response(error_msg, {'node': None})


@mcp.tool(
    name='get_all_edges',
    description='Retrieve all edges from the DSR graph',
    tags={'dsr', 'graph', 'edges', 'query'}
)
async def get_all_edges(ctx: Context) -> dict:
    """
    Retrieve all edges from the DSR graph.

    Returns:
        dict: Dictionary containing a list of edges and their basic info.
    """
    await ctx.info('Retrieving all edges from DSR graph...')

    if dsr_graph is None:
        error_msg = 'DSR not initialized'
        await ctx.error(error_msg)
        return _create_error_response(error_msg, {'edges': []})

    try:
        edges_data = []
        for node in dsr_graph.get_nodes():
            for destination_id, edge_type in dsr_graph.get_edges(node.id):
                edges_data.append({
                    'origin': str(node.id),
                    'destination': str(destination_id),
                    'type': edge_type
                })

        await ctx.info(f'Retrieved {len(edges_data)} edges successfully')
        return _create_success_response(
            f'Retrieved {len(edges_data)} edges',
            {
                'edges': edges_data,
                'count': len(edges_data),
                'dsr_name': DSR_NAME
            }
        )
    except (AttributeError, RuntimeError, TypeError) as e:
        error_msg = f'Error retrieving edges: {str(e)}'
        await ctx.error(error_msg)
        return _create_error_response(error_msg, {'edges': []})


@mcp.tool(
    name='insert_node',
    description='Insert a new node into the DSR graph.',
    tags={'dsr', 'graph', 'node', 'insert'}
)
async def insert_node(name: str, node_type: str, ctx: Context) -> dict:
    """
    Insert a new node into the DSR graph.

    Args:
        name (str): The name of the node to insert.
        node_type (str): The type of the node to insert.

    Returns:
        dict: Dictionary with the result of the insertion or error message.
    """
    await ctx.info(f'Inserting new node: {name} (type: {node_type})')

    if dsr_graph is None:
        error_msg = 'DSR not initialized'
        await ctx.error(error_msg)
        return _create_error_response(error_msg, {'nodes': []})

    try:
        node = Node(AGENT_ID, node_type, name)
        node_id = dsr_graph.insert_node(node)

        await ctx.info(f'Node inserted successfully with ID: {node_id}')
        return _create_success_response(
            'Node inserted successfully',
            {
                'id': str(node_id),
                'name': name,
                'type': node_type
            }
        )
    except (AttributeError, RuntimeError, ValueError) as e:
        error_msg = f'Error inserting node: {str(e)}'
        await ctx.error(error_msg)
        return _create_error_response(error_msg, {'node': None})


@mcp.tool(
    name='insert_edge',
    description='Insert a new edge between two nodes in the DSR graph',
    tags={'dsr', 'graph', 'edge', 'insert'}
)
async def insert_edge(origin_id: str, destination_id: str, edge_type: str,
                      ctx: Context) -> dict:
    """
    Insert a new edge between two nodes in the DSR graph.

    Args:
        origin_id (str): ID of the origin node.
        destination_id (str): ID of the destination node.
        edge_type (str): Type of the edge to insert.

    Returns:
        dict: Dictionary with the result of the insertion or error message.
    """
    await ctx.info(
        f'Inserting edge: {origin_id} -> {destination_id} (type: {edge_type})'
    )

    if dsr_graph is None:
        error_msg = 'DSR not initialized'
        await ctx.error(error_msg)
        return _create_error_response(error_msg, {'nodes': []})

    try:
        edge = Edge(int(destination_id), int(origin_id), edge_type, AGENT_ID)
        success = dsr_graph.insert_or_assign_edge(edge)

        if success:
            await ctx.info('Edge inserted successfully')
            return _create_success_response(
                'Edge inserted successfully',
                {
                    'origin': str(edge.origin),
                    'destination': str(edge.destination),
                    'type': edge.type
                }
            )
        else:
            error_msg = 'Failed to insert edge'
            await ctx.error(error_msg)
            return _create_error_response(error_msg, {'edge': None}
                                          )
    except (AttributeError, RuntimeError, ValueError) as e:
        error_msg = f'Error inserting edge: {str(e)}'
        await ctx.error(error_msg)
        return _create_error_response(error_msg, {'edge': None})


@mcp.tool(
    name='insert_edge_attribute',
    description='Insert or update an attribute for an edge in the DSR graph',
    tags={'dsr', 'graph', 'edge', 'attribute', 'insert'}
)
async def insert_edge_attribute(origin_id: str, destination_id: str,
                                attribute_name: str, attribute_value: str,
                                ctx: Context,
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
    await ctx.info(
        f'Inserting edge attribute {attribute_name} for edge '
        f'{origin_id} -> {destination_id}'
    )

    if dsr_graph is None:
        error_msg = 'DSR not initialized'
        await ctx.error(error_msg)
        return _create_error_response(error_msg, {'nodes': []})

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
            await ctx.info('Edge attribute inserted successfully')
            return _create_success_response(
                'Edge attribute inserted successfully',
                {
                    'origin': str(origin_id),
                    'destination': str(destination_id),
                    'attribute_name': attribute_name,
                    'attribute_value': str(converted_value),
                    'attribute_type': attribute_type
                }
            )
        else:
            error_msg = 'Failed to insert edge attribute'
            await ctx.error(error_msg)
            return _create_error_response(error_msg, {'attribute': None})
    except (AttributeError, RuntimeError, ValueError) as e:
        error_msg = f'Error inserting edge attribute: {str(e)}'
        await ctx.error(error_msg)
        return _create_error_response(error_msg, {'attribute': None})


@mcp.tool(
    name='update_node',
    description='Update a node with new attributes in the DSR graph',
    tags={'dsr', 'graph', 'node', 'update'}
)
async def update_node(node_id: str, attribute_name: str,
                      attribute_value: str, ctx: Context,
                      attribute_type: str = 'string') -> dict:
    """
    Update a node with new attributes in the DSR graph.

    Args:
        node_id (str): ID of the node to update.
        attribute_name (str): Name of the attribute to update.
        attribute_value (str): Value of the attribute.
        attribute_type (str): Type of the attribute (string, int, float, bool).

    Returns:
        dict: Dictionary with the result of the update or error message.
    """
    await ctx.info(
        f'Updating node {node_id} with attribute {attribute_name}'
    )

    if dsr_graph is None:
        error_msg = 'DSR not initialized'
        await ctx.error(error_msg)
        return _create_error_response(error_msg, {'nodes': []})

    try:
        # Get the existing node
        node = dsr_graph.get_node(int(node_id))
        if node is None:
            error_msg = f'Node {node_id} not found'
            await ctx.warning(error_msg)
            return _create_error_response(error_msg, {'node': None})

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
            await ctx.info('Node updated successfully')
            return _create_success_response(
                'Node updated successfully',
                {
                    'id': str(node_id),
                    'attribute_name': attribute_name,
                    'attribute_value': str(converted_value),
                    'attribute_type': attribute_type
                }
            )
        else:
            error_msg = 'Failed to update node'
            await ctx.error(error_msg)
            return _create_error_response(error_msg, {'node': None})
    except (AttributeError, RuntimeError, ValueError) as e:
        error_msg = f'Error updating node: {str(e)}'
        await ctx.error(error_msg)
        return _create_error_response(error_msg, {'node': None})


@mcp.tool(
    name='delete_node',
    description='Delete a node from the DSR graph',
    tags={'dsr', 'graph', 'node', 'delete'}
)
async def delete_node(node_id: str, ctx: Context) -> dict:
    """
    Delete a node from the DSR graph.

    Args:
        node_id (str): ID of the node to delete.

    Returns:
        dict: Dictionary with the result of the deletion or error message.
    """
    await ctx.info(f'Deleting node: {node_id}')

    if dsr_graph is None:
        error_msg = 'DSR not initialized'
        await ctx.error(error_msg)
        return _create_error_response(error_msg, {'nodes': []})

    try:
        # Reference: DSRGraph.delete_node(node_id)
        success = dsr_graph.delete_node(int(node_id))
        if success:
            await ctx.info(f'Node {node_id} deleted successfully')
            return _create_success_response(
                'Node deleted successfully',
                {'node_id': node_id}
            )
        else:
            error_msg = 'Failed to delete node'
            await ctx.error(error_msg)
            return _create_error_response(error_msg, {'node': None})
    except (AttributeError, RuntimeError, ValueError) as e:
        error_msg = f'Error deleting node: {str(e)}'
        await ctx.error(error_msg)
        return _create_error_response(error_msg, {'node': None})


@mcp.tool(
    name='delete_edge',
    description='Delete an edge from the DSR graph',
    tags={'dsr', 'graph', 'edge', 'delete'}
)
async def delete_edge(origin_id: str, destination_id: str, edge_type: str,
                      ctx: Context) -> dict:
    """
    Delete an edge from the DSR graph.

    Args:
        origin_id (str): ID of the origin node.
        destination_id (str): ID of the destination node.
        edge_type (str): Type of the edge to delete.

    Returns:
        dict: Dictionary with the result of the deletion or error message.
    """
    await ctx.info(
        f'Deleting edge: {origin_id} -> {destination_id} (type: {edge_type})'
    )

    if dsr_graph is None:
        error_msg = 'DSR not initialized'
        await ctx.error(error_msg)
        return _create_error_response(error_msg, {'nodes': []})

    try:
        # Reference: DSRGraph.delete_edge(origin_id, destination_id, edge_type)
        success = dsr_graph.delete_edge(
            int(origin_id), int(destination_id), edge_type)

        if success:
            await ctx.info('Edge deleted successfully')
            return _create_success_response(
                'Edge deleted successfully',
                {
                    'origin': str(origin_id),
                    'destination': str(destination_id),
                    'type': edge_type
                }
            )
        else:
            error_msg = 'Failed to delete edge'
            await ctx.error(error_msg)
            return _create_error_response(error_msg, {'edge': None})
    except (AttributeError, RuntimeError, ValueError) as e:
        error_msg = f'Error deleting edge: {str(e)}'
        await ctx.error(error_msg)
        return _create_error_response(error_msg, {'edge': None})


@mcp.tool(
    name='save_graph',
    description='Save the current state of the DSR graph to a JSON file.',
    tags={'dsr', 'graph', 'save', 'json'}
)
async def save_graph(ctx: Context) -> dict:
    """
    Save the current state of the DSR graph to a JSON file.

    The output file path will be obtained through user elicitation.

    Returns:
        dict: Dictionary with the result of the save operation or an
        error message.
    """
    # Request file path from the user
    result = await ctx.elicit(
        message='Please provide the file path to save the DSR graph:',
        response_type=str
    )

    if result.action != 'accept':
        error_msg = 'File path not provided or operation cancelled.'
        await ctx.error(error_msg)
        return _create_error_response(error_msg, {'file_path': None})

    file_path = result.data

    if dsr_graph is None:
        error_msg = 'DSR not initialized'
        await ctx.error(error_msg)
        return _create_error_response(error_msg, {'file_path': file_path})

    try:
        dsr_graph.write_to_json_file(file_path, skip_atts=[])
        await ctx.info(f'DSR graph saved successfully to {file_path}')
        return _create_success_response(
            'DSR graph saved successfully',
            {'file_path': file_path}
        )
    except (AttributeError, RuntimeError, ValueError) as e:
        error_msg = f'Error saving DSR graph to JSON: {str(e)}'
        await ctx.error(error_msg)
        return _create_error_response(error_msg, {'file_path': file_path})


def main() -> None:
    """
    Run the MCP server.

    Notes
    -----
    Default transport is http for local MCP integration.
    """
    # Initialize DSR connection on startup
    logger.info(f'Initializing DSR connection to {DSR_NAME}...')
    if _init_dsr():
        logger.info('DSR initialized successfully')
    else:
        logger.warning('Could not initialize DSR on startup')

    mcp.run(transport='http', host='127.0.0.1', port=3000)


if __name__ == '__main__':
    main()
