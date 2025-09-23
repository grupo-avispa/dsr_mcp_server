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

"""Edge management tools for DSR MCP server."""

from typing import Dict, Any
from fastmcp import Context

from ..dsr_client import DSRClient
from ..response_utils import create_success_response, create_error_response
from .node_tools import convert_attribute_value


async def get_all_edges(dsr_client: DSRClient, ctx: Context) -> Dict[str, Any]:
    """
    Retrieve all edges from the DSR graph.

    Args:
        dsr_client (DSRClient): The DSR client instance.
        ctx (Context): The MCP context.

    Returns:
        Dict[str, Any]: Dictionary containing a list of edges.
    """
    await ctx.info('Retrieving all edges from DSR graph...')

    try:
        edges_data = dsr_client.get_all_edges()
        await ctx.info(f'Retrieved {len(edges_data)} edges successfully')
        return create_success_response(
            f'Retrieved {len(edges_data)} edges',
            {
                'edges': edges_data,
                'count': len(edges_data),
                'dsr_name': dsr_client.config.DSR_NAME
            }
        )
    except RuntimeError as e:
        error_msg = str(e)
        await ctx.error(error_msg)
        return create_error_response(error_msg, {'edges': []})


async def insert_edge(
    origin_id: str, destination_id: str, edge_type: str,
    dsr_client: DSRClient, ctx: Context
) -> Dict[str, Any]:
    """
    Insert a new edge between two nodes in the DSR graph.

    Args:
        origin_id (str): ID of the origin node.
        destination_id (str): ID of the destination node.
        edge_type (str): Type of the edge to insert.
        dsr_client (DSRClient): The DSR client instance.
        ctx (Context): The MCP context.

    Returns:
        Dict[str, Any]: Dictionary with the result of the insertion.
    """
    await ctx.info(
        f'Inserting edge: {origin_id} -> {destination_id} (type: {edge_type})'
    )

    try:
        success = dsr_client.insert_edge(
            int(origin_id), int(destination_id), edge_type
        )
        if success:
            await ctx.info('Edge inserted successfully')
            return create_success_response(
                'Edge inserted successfully',
                {
                    'origin': str(origin_id),
                    'destination': str(destination_id),
                    'type': edge_type
                }
            )
        else:
            error_msg = 'Failed to insert edge'
            await ctx.error(error_msg)
            return create_error_response(error_msg, {'edge': None})
    except (RuntimeError, ValueError) as e:
        error_msg = str(e)
        await ctx.error(error_msg)
        return create_error_response(error_msg, {'edge': None})


async def insert_edge_attribute(
    origin_id: str, destination_id: str, attribute_name: str,
    attribute_value: str, dsr_client: DSRClient, ctx: Context,
    attribute_type: str = 'string'
) -> Dict[str, Any]:
    """
    Insert or update an attribute for an edge in the DSR graph.

    Args:
        origin_id (str): ID of the origin node.
        destination_id (str): ID of the destination node.
        attribute_name (str): Name of the attribute to insert/update.
        attribute_value (str): Value of the attribute.
        dsr_client (DSRClient): The DSR client instance.
        ctx (Context): The MCP context.
        attribute_type (str): Type of the attribute.

    Returns:
        Dict[str, Any]: Dictionary with the result of the insertion.
    """
    await ctx.info(
        f'Inserting edge attribute {attribute_name} for edge '
        f'{origin_id} -> {destination_id}'
    )

    try:
        # Convert attribute value to the appropriate type
        converted_value = convert_attribute_value(
            attribute_value, attribute_type)

        success = dsr_client.insert_edge_attribute(
            int(origin_id), int(destination_id),
            attribute_name, converted_value
        )

        if success:
            await ctx.info('Edge attribute inserted successfully')
            return create_success_response(
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
            return create_error_response(error_msg, {'attribute': None})
    except (RuntimeError, ValueError) as e:
        error_msg = str(e)
        await ctx.error(error_msg)
        return create_error_response(error_msg, {'attribute': None})


async def delete_edge(
    origin_id: str, destination_id: str, edge_type: str,
    dsr_client: DSRClient, ctx: Context
) -> Dict[str, Any]:
    """
    Delete an edge from the DSR graph.

    Args:
        origin_id (str): ID of the origin node.
        destination_id (str): ID of the destination node.
        edge_type (str): Type of the edge to delete.
        dsr_client (DSRClient): The DSR client instance.
        ctx (Context): The MCP context.

    Returns:
        Dict[str, Any]: Dictionary with the result of the deletion.
    """
    await ctx.info(
        f'Deleting edge: {origin_id} -> {destination_id} (type: {edge_type})'
    )

    try:
        success = dsr_client.delete_edge(
            int(origin_id), int(destination_id), edge_type
        )

        if success:
            await ctx.info('Edge deleted successfully')
            return create_success_response(
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
            return create_error_response(error_msg, {'edge': None})
    except (RuntimeError, ValueError) as e:
        error_msg = str(e)
        await ctx.error(error_msg)
        return create_error_response(error_msg, {'edge': None})
