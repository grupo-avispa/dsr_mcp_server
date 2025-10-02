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

"""Response utilities for standardized API responses."""

from typing import Optional, Dict, Any
import json


def create_success_response(
    message: str,
    data: Optional[Dict[str, Any]] = None
) -> str:
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
    return json.dumps(response, indent=2)


def create_error_response(
    error: str,
    details: Optional[Dict[str, Any]] = None
) -> str:
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
    return json.dumps(response, indent=2)
