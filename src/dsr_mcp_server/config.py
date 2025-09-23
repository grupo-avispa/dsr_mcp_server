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

"""Configuration module for DSR MCP Server."""

import os
from typing import Final


class DSRConfig:
    """Configuration class for DSR connection parameters."""

    # DSR Configuration - can be overridden by environment variables
    AGENT_ID: Final[int] = int(os.getenv('DSR_AGENT_ID', '42'))
    DSR_NAME: Final[str] = os.getenv('DSR_NAME', 'mcp_server')

    # Server configuration
    SERVER_HOST: Final[str] = os.getenv('SERVER_HOST', '127.0.0.1')
    SERVER_PORT: Final[int] = int(os.getenv('SERVER_PORT', '3000'))

    # Excluded node attributes for cleaner output
    EXCLUDED_NODE_ATTRIBUTES: Final[list[str]] = [
        'color', 'depth', 'height', 'level', 'number', 'parent',
        'pos_x', 'pos_y', 'texture', 'width'
    ]
