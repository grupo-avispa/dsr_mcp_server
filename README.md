# DSR MCP Server

A Model Context Protocol (MCP) server that provides tools for interacting with Deep Scene Representation (DSR) graphs. This server enables AI assistants to query, manipulate, and analyze DSR graph structures through standardized MCP tools.

## Overview

The DSR MCP Server wraps DSR functionality using FastMCP, providing a standardized interface for AI systems to interact with robot perception and scene understanding data. It exposes various tools for node management, graph traversal, and edge manipulation within DSR graphs.

## Features

- **Connection Management**: Initialize and monitor DSR connections
- **Node Operations**: Retrieve, filter, and analyze DSR nodes
- **Graph Traversal**: Navigate through node relationships and edges
- **Type-based Filtering**: Find nodes by specific types (robot, person, room, etc.)
- **Edge Management**: Create, query, and delete relationships between nodes
- **Attribute Access**: Read and analyze node attributes and properties

## Installation

1. Clone the repository:
```bash
git clone https://github.com/grupo-avispa/dsr_mcp_server.git
cd dsr_mcp_server
```

2. Install dependencies:
```bash
pip3 install -r requirements.txt
```

3. Ensure you have the DSR library (`pydsr`) installed and properly configured in your environment.

## Configuration

The server uses the following default configuration:

- **Agent ID**: 42 (unique among agents)
- **DSR Name**: 'mcp_server' (target DSR graph name)
- **Server Host**: 127.0.0.1
- **Server Port**: 3000
- **Transport**: HTTP

You can modify these values in the `server.py` file if needed.

## Usage

### Starting the Server

Run the server directly:

```bash
python3 server.py
```

The server will start on `http://localhost:3000/mcp` and attempt to initialize the DSR connection automatically.

### MCP Client Configuration

Add the server to your MCP client configuration (`mcp.json`):

```json
{
    "servers": {
        "dsr_mcp_server": {
            "type": "http",
            "url": "http://localhost:3000/mcp"
        }
    }
}
```

## Available Tools

### Connection Management

- **`initialize_dsr_connection`**: Initialize or reinitialize the DSR connection
- **`check_dsr_connection`**: Check DSR connection status and return diagnostic information

### Node Operations

- **`get_all_nodes`**: Retrieve all nodes from the DSR graph with basic information
- **`get_nodes_by_type`**: Filter nodes by their type (e.g., robot, person, room)
- **`get_node_details`**: Get comprehensive information about a specific node including attributes and edges

### Graph Analysis

- **`get_node_edges`**: Retrieve all edges connected to a specific node
- **`get_edge_details`**: Get detailed information about a specific edge between two nodes

### Edge Management

- **`create_edge`**: Create new relationships between nodes
- **`delete_edge`**: Remove existing edges from the graph

## Example Interactions

### Check Connection Status
```python
# Through MCP client
result = await client.call_tool("check_dsr_connection")
print(result)  # Shows connection status, agent ID, and root node information
```

### Find All Robots
```python
# Get all robot nodes
robots = await client.call_tool("get_nodes_by_type", {"node_type": "robot"})
```

### Analyze Node Relationships
```python
# Get detailed information about a specific node
node_details = await client.call_tool("get_node_details", {"node_identifier": "123"})
```

## API Response Format

All tools return standardized responses with the following structure:

### Success Response
```json
{
    "success": true,
    "message": "Operation completed successfully",
    "data": {
        // Additional response data
    }
}
```

### Error Response
```json
{
    "success": false,
    "error": "Error description",
    "details": {
        // Additional error details
    }
}
```

## Dependencies

- **fastmcp**: MCP server framework (>= 2.2.7)
- **pydsr**: Python DSR library for graph operations
- **Python**: 3.7+ required

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Support

For issues, questions, or contributions, please refer to the project's issue tracker or contact the development team.
