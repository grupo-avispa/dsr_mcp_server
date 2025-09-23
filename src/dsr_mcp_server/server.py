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

"""MCP server wrapping DSR functionality (refactored)."""

from fastmcp import FastMCP, Context
from fastmcp.utilities.logging import get_logger

from .dsr_client import DSRClient
from .config import DSRConfig
from .response_utils import create_error_response
from .tools import connection_tools, node_tools, edge_tools, graph_tools


# Create MCP application and global DSR client
mcp = FastMCP('dsr-mcp-server')
dsr_client = DSRClient()
logger = get_logger(__name__)


@mcp.tool(
    enabled=False,
    name='initialize_dsr_connection',
    description='Initialize or reinitialize the DSR connection',
    tags={'dsr', 'graph', 'initialization', 'connection', 'setup'}
)
async def initialize_dsr_connection_tool(ctx: Context) -> dict:
    """Initialize or reinitialize the DSR connection."""
    return await connection_tools.initialize_dsr_connection(dsr_client, ctx)


@mcp.tool(
    name='check_dsr_connection',
    description='Check DSR connection and return status information',
    tags={'dsr', 'graph', 'connection', 'health', 'status', 'configuration'}
)
async def check_dsr_connection_tool(ctx: Context) -> str:
    """Check DSR connection and return status information."""
    return await connection_tools.check_dsr_connection(dsr_client, ctx)


@mcp.tool(
    name='get_all_nodes',
    description='Retrieve all nodes from the DSR graph',
    tags={'dsr', 'graph', 'nodes', 'query'}
)
async def get_all_nodes_tool(ctx: Context) -> dict:
    """Return all nodes from the DSR graph with their basic information."""
    return await node_tools.get_all_nodes(dsr_client, ctx)


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
async def get_nodes_by_type_tool(node_type: str, ctx: Context) -> dict:
    """Retrieve nodes filtered by their type from the DSR graph."""
    return await node_tools.get_nodes_by_type(node_type, dsr_client, ctx)


@mcp.tool(
    name='get_node_details',
    description='Get detailed information about a specific DSR node '
                'including attributes and edges',
    tags={'dsr', 'graph', 'node', 'details', 'attributes', 'edges'}
)
async def get_node_details_tool(node_identifier: str, ctx: Context) -> dict:
    """Return detailed information about a specific node by ID."""
    return await node_tools.get_node_details(node_identifier, dsr_client, ctx)


@mcp.tool(
    name='get_all_edges',
    description='Retrieve all edges from the DSR graph',
    tags={'dsr', 'graph', 'edges', 'query'}
)
async def get_all_edges_tool(ctx: Context) -> dict:
    """Retrieve all edges from the DSR graph."""
    return await edge_tools.get_all_edges(dsr_client, ctx)


@mcp.tool(
    name='insert_node',
    description='Insert a new node into the DSR graph.',
    tags={'dsr', 'graph', 'node', 'insert'}
)
async def insert_node_tool(name: str, node_type: str, ctx: Context) -> dict:
    """Insert a new node into the DSR graph."""
    return await node_tools.insert_node(name, node_type, dsr_client, ctx)


@mcp.tool(
    name='insert_edge',
    description='Insert a new edge between two nodes in the DSR graph',
    tags={'dsr', 'graph', 'edge', 'insert'}
)
async def insert_edge_tool(
    origin_id: str, destination_id: str, edge_type: str, ctx: Context
) -> dict:
    """Insert a new edge between two nodes in the DSR graph."""
    return await edge_tools.insert_edge(
        origin_id, destination_id, edge_type, dsr_client, ctx
    )


@mcp.tool(
    name='insert_edge_attribute',
    description='Insert or update an attribute for an edge in the DSR graph',
    tags={'dsr', 'graph', 'edge', 'attribute', 'insert'}
)
async def insert_edge_attribute_tool(
    origin_id: str, destination_id: str, attribute_name: str,
    attribute_value: str, ctx: Context, attribute_type: str = 'string'
) -> dict:
    """Insert or update an attribute for an edge in the DSR graph."""
    return await edge_tools.insert_edge_attribute(
        origin_id, destination_id, attribute_name, attribute_value,
        dsr_client, ctx, attribute_type
    )


@mcp.tool(
    name='update_node',
    description='Update a node with new attributes in the DSR graph',
    tags={'dsr', 'graph', 'node', 'update'}
)
async def update_node_tool(
    node_id: str, attribute_name: str, attribute_value: str,
    ctx: Context, attribute_type: str = 'string'
) -> dict:
    """Update a node with new attributes in the DSR graph."""
    return await node_tools.update_node(
        node_id, attribute_name, attribute_value,
        dsr_client, ctx, attribute_type
    )


@mcp.tool(
    name='delete_node',
    description='Delete a node from the DSR graph',
    tags={'dsr', 'graph', 'node', 'delete'}
)
async def delete_node_tool(node_id: str, ctx: Context) -> dict:
    """Delete a node from the DSR graph."""
    return await node_tools.delete_node(node_id, dsr_client, ctx)


@mcp.tool(
    name='delete_edge',
    description='Delete an edge from the DSR graph',
    tags={'dsr', 'graph', 'edge', 'delete'}
)
async def delete_edge_tool(
    origin_id: str, destination_id: str, edge_type: str, ctx: Context
) -> dict:
    """Delete an edge from the DSR graph."""
    return await edge_tools.delete_edge(
        origin_id, destination_id, edge_type, dsr_client, ctx
    )


@mcp.tool(
    name='save_graph',
    description='Save the current state of the DSR graph to a JSON file.',
    tags={'dsr', 'graph', 'save', 'json'}
)
async def save_graph_tool(ctx: Context) -> dict:
    """Save the current state of the DSR graph to a JSON file."""
    # Request file path from the user
    result = await ctx.elicit(
        message='Please provide the file path to save the DSR graph:',
        response_type=None
    )

    if result.action != 'accept':
        error_msg = 'File path not provided or operation cancelled.'
        await ctx.error(error_msg)
        return create_error_response(error_msg, {'file_path': None})

    # Extract the file path from the result data
    if isinstance(result.data, str):
        file_path = result.data
    else:
        file_path = str(result.data.get('file_path', ''))

    if not file_path:
        error_msg = 'Invalid file path provided.'
        await ctx.error(error_msg)
        return create_error_response(error_msg, {'file_path': None})

    return await graph_tools.save_graph(file_path, dsr_client, ctx)


def main() -> None:
    """
    Run the MCP server.

    Notes:
        Default transport is http for local MCP integration.
    """
    config = DSRConfig()

    # Initialize DSR connection on startup
    logger.info(f'Initializing DSR connection to {config.DSR_NAME}...')
    if dsr_client.initialize():
        logger.info('DSR initialized successfully')
    else:
        logger.warning('Could not initialize DSR on startup')

    mcp.run(transport='http', host=config.SERVER_HOST, port=config.SERVER_PORT)


if __name__ == '__main__':
    main()
