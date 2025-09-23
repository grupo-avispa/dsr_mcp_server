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

"""Graph-level operations tools for DSR MCP server."""

from typing import Dict, Any
from fastmcp import Context

from ..dsr_client import DSRClient
from ..response_utils import create_success_response, create_error_response


async def save_graph(
    file_path: str, dsr_client: DSRClient, ctx: Context
) -> Dict[str, Any]:
    """
    Save the current state of the DSR graph to a JSON file.

    Args:
        file_path (str): Path where to save the graph.
        dsr_client (DSRClient): The DSR client instance.
        ctx (Context): The MCP context.

    Returns:
        Dict[str, Any]: Dictionary with the result of the save operation.
    """
    await ctx.info(f'Saving DSR graph to {file_path}')

    try:
        dsr_client.save_graph(file_path)
        await ctx.info(f'DSR graph saved successfully to {file_path}')
        return create_success_response(
            'DSR graph saved successfully',
            {'file_path': file_path}
        )
    except RuntimeError as e:
        error_msg = str(e)
        await ctx.error(error_msg)
        return create_error_response(error_msg, {'file_path': file_path})
