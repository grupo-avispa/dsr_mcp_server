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

"""Connection management tools for DSR MCP server."""

from typing import Dict, Any
from fastmcp import Context

from ..dsr_client import DSRClient
from ..response_utils import create_success_response, create_error_response


async def initialize_dsr_connection(
    dsr_client: DSRClient, ctx: Context
) -> Dict[str, Any]:
    """Initialize or reinitialize the DSR connection."""
    await ctx.info(
        f'Initializing DSR connection to {dsr_client.config.DSR_NAME}...'
    )

    if dsr_client.initialize():
        status = dsr_client.check_connection()
        status_msg = 'DSR connection initialized successfully'
        await ctx.info(status_msg)
        return create_success_response(status_msg, {'status': status})
    else:
        error_msg = 'Failed to initialize DSR connection'
        await ctx.error(error_msg)
        return create_error_response(error_msg, {'error': 'Unknown error'})


async def check_dsr_connection(
    dsr_client: DSRClient, ctx: Context
) -> str:
    """Check DSR connection and return status information."""
    await ctx.info('Checking DSR connection status...')

    status = dsr_client.check_connection()
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
