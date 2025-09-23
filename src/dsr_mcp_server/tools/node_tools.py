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

"""Node management tools for DSR MCP server."""

from typing import Dict, Any
from fastmcp import Context

from ..dsr_client import DSRClient
from ..response_utils import create_success_response, create_error_response


def convert_attribute_value(value: str, attr_type: str) -> Any:
    """
    Convert string attribute value to appropriate type.

    Args:
        value (str): The string value to convert.
        attr_type (str): The target type ('string', 'int', 'float', 'bool').

    Returns:
        Any: The converted value.

    Raises:
        ValueError: If conversion fails.
    """
    if attr_type == 'int':
        return int(value)
    elif attr_type == 'float':
        return float(value)
    elif attr_type == 'bool':
        return value.lower() in ('true', '1', 'yes', 'on')
    return value  # Default to string


async def get_all_nodes(dsr_client: DSRClient, ctx: Context) -> Dict[str, Any]:
    """
    Return all nodes from the DSR graph with their basic information.

    Args:
        dsr_client (DSRClient): The DSR client instance.
        ctx (Context): The MCP context.

    Returns:
        Dict[str, Any]: Dictionary containing a list of nodes and
            their basic info.
    """
    await ctx.info('Retrieving all nodes from DSR graph...')

    try:
        nodes = dsr_client.get_all_nodes()
        nodes_data = []
        for node in nodes:
            nodes_data.append({
                'id': str(node.id),
                'name': node.name,
                'type': node.type,
                'agent_id': getattr(node, 'agent_id', None)
            })

        await ctx.info(f'Retrieved {len(nodes_data)} nodes successfully')
        return create_success_response(
            f'Retrieved {len(nodes_data)} nodes',
            {
                'nodes': nodes_data,
                'count': len(nodes_data),
                'dsr_name': dsr_client.config.DSR_NAME
            }
        )
    except RuntimeError as e:
        error_msg = str(e)
        await ctx.error(error_msg)
        return create_error_response(error_msg, {'nodes': []})


async def get_nodes_by_type(
    node_type: str, dsr_client: DSRClient, ctx: Context
) -> Dict[str, Any]:
    """
    Retrieve nodes filtered by their type from the DSR graph.

    Args:
        node_type (str): The type of nodes to retrieve.
        dsr_client (DSRClient): The DSR client instance.
        ctx (Context): The MCP context.

    Returns:
        Dict[str, Any]: Standardized response containing filtered nodes.
    """
    await ctx.info(f'Retrieving nodes of type: {node_type}')

    try:
        nodes = dsr_client.get_nodes_by_type(node_type)
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
        return create_success_response(
            f'Retrieved {len(nodes_data)} nodes of type {node_type}',
            {
                'nodes': nodes_data,
                'count': len(nodes_data),
                'type': node_type
            }
        )
    except RuntimeError as e:
        error_msg = str(e)
        await ctx.error(error_msg)
        return create_error_response(error_msg, {'nodes': []})


async def get_node_details(
    node_identifier: str, dsr_client: DSRClient, ctx: Context
) -> Dict[str, Any]:
    """
    Return detailed information about a specific node by ID.

    Args:
        node_identifier (str): The ID of the node to retrieve.
        dsr_client (DSRClient): The DSR client instance.
        ctx (Context): The MCP context.

    Returns:
        Dict[str, Any]: A dictionary containing the node details.
    """
    await ctx.info(f'Retrieving details for node: {node_identifier}')

    try:
        node = dsr_client.get_node_by_id(int(node_identifier))
        if node is None:
            error_msg = f'Node {node_identifier} not found'
            await ctx.warning(error_msg)
            return create_error_response(error_msg, {'node': None})

        attributes = dsr_client.get_node_attributes(node)
        edges = dsr_client.get_node_edges(node)

        await ctx.info(f'Retrieved details for node {node_identifier}')
        return create_success_response(
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
    except (RuntimeError, ValueError) as e:
        error_msg = str(e)
        await ctx.error(error_msg)
        return create_error_response(error_msg, {'node': None})


async def insert_node(
    name: str, node_type: str, dsr_client: DSRClient, ctx: Context
) -> Dict[str, Any]:
    """
    Insert a new node into the DSR graph.

    Args:
        name (str): The name of the node to insert.
        node_type (str): The type of the node to insert.
        dsr_client (DSRClient): The DSR client instance.
        ctx (Context): The MCP context.

    Returns:
        Dict[str, Any]: Dictionary with the result of the insertion.
    """
    await ctx.info(f'Inserting new node: {name} (type: {node_type})')

    try:
        node_id = dsr_client.insert_node(name, node_type)
        await ctx.info(f'Node inserted successfully with ID: {node_id}')
        return create_success_response(
            'Node inserted successfully',
            {
                'id': str(node_id),
                'name': name,
                'type': node_type
            }
        )
    except RuntimeError as e:
        error_msg = str(e)
        await ctx.error(error_msg)
        return create_error_response(error_msg, {'node': None})


async def update_node(
    node_id: str, attribute_name: str, attribute_value: str,
    dsr_client: DSRClient, ctx: Context, attribute_type: str = 'string'
) -> Dict[str, Any]:
    """
    Update a node with new attributes in the DSR graph.

    Args:
        node_id (str): ID of the node to update.
        attribute_name (str): Name of the attribute to update.
        attribute_value (str): Value of the attribute.
        dsr_client (DSRClient): The DSR client instance.
        ctx (Context): The MCP context.
        attribute_type (str): Type of the attribute.

    Returns:
        Dict[str, Any]: Dictionary with the result of the update.
    """
    await ctx.info(f'Updating node {node_id} with attribute {attribute_name}')

    try:
        # Convert attribute value to the appropriate type
        converted_value = convert_attribute_value(
            attribute_value, attribute_type)

        success = dsr_client.update_node(
            int(node_id), attribute_name, converted_value
        )
        if success:
            await ctx.info('Node updated successfully')
            return create_success_response(
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
            return create_error_response(error_msg, {'node': None})
    except (RuntimeError, ValueError) as e:
        error_msg = str(e)
        await ctx.error(error_msg)
        return create_error_response(error_msg, {'node': None})


async def delete_node(
    node_id: str, dsr_client: DSRClient, ctx: Context
) -> Dict[str, Any]:
    """
    Delete a node from the DSR graph.

    Args:
        node_id (str): ID of the node to delete.
        dsr_client (DSRClient): The DSR client instance.
        ctx (Context): The MCP context.

    Returns:
        Dict[str, Any]: Dictionary with the result of the deletion.
    """
    await ctx.info(f'Deleting node: {node_id}')

    try:
        success = dsr_client.delete_node(int(node_id))
        if success:
            await ctx.info(f'Node {node_id} deleted successfully')
            return create_success_response(
                'Node deleted successfully',
                {'node_id': node_id}
            )
        else:
            error_msg = 'Failed to delete node'
            await ctx.error(error_msg)
            return create_error_response(error_msg, {'node': None})
    except (RuntimeError, ValueError) as e:
        error_msg = str(e)
        await ctx.error(error_msg)
        return create_error_response(error_msg, {'node': None})
