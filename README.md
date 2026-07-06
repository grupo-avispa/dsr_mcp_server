# DSR MCP Server
![License](https://img.shields.io/github/license/grupo-avispa/dsr_mcp_server)
[![Build](https://github.com/grupo-avispa/dsr_mcp_server/actions/workflows/build.yml/badge.svg)](https://github.com/grupo-avispa/dsr_mcp_server/actions/workflows/build.yml)

An MCP (Model Context Protocol) server that provides a comprehensive set of tools to query, manipulate, and analyze Deep State Representation (DSR) graphs. This server enables AI assistants to interact with robot perception and scene understanding data through standardized MCP tools with real-time graph operations and intelligent node relationship management.

### Tools

| Tool Name                 | Description                                                                   | Parameters                                                                                                               |
| ------------------------- | ----------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------ |
| **check_dsr_connection**  | Check DSR connection and return status information                            | —                                                                                                                        |
| **get_all_nodes**         | Retrieve all nodes from the DSR graph                                         | —                                                                                                                        |
| **get_nodes_by_type**     | Filter nodes by their type (e.g., robot, person, room)                        | `node_type: str`                                                                                                         |
| **get_node_details**      | Get detailed information about a specific node including attributes and edges | `node_identifier: str`                                                                                                   |
| **get_all_edges**         | Retrieve all edges from the DSR graph                                         | —                                                                                                                        |
| **insert_node**           | Insert a new node into the DSR graph                                          | `name: str`, `node_type: str`                                                                                            |
| **insert_edge**           | Insert a new edge between two nodes in the DSR graph                          | `origin_id: str`, `destination_id: str`, `edge_type: str`                                                                |
| **insert_edge_attribute** | Insert or update an attribute for an edge in the DSR graph                    | `origin_id: str`, `destination_id: str`, `attribute_name: str`, `attribute_value: str`, `attribute_type: str = 'string'` |
| **update_node**           | Update a node with new attributes in the DSR graph                            | `node_id: str`, `attribute_name: str`, `attribute_value: str`, `attribute_type: str = 'string'`                          |
| **delete_node**           | Delete a node from the DSR graph                                              | `node_id: str`                                                                                                           |
| **delete_edge**           | Delete an edge from the DSR graph                                             | `origin_id: str`, `destination_id: str`, `edge_type: str`                                                                |
| **save_graph**            | Save the current state of the DSR graph to a JSON file                        | Interactive file path selection                                                                                          |

### Resources

Resources provide read-only, efficient access to DSR graph data. They are ideal for querying information without modifying the graph state.

| Resource URI                | Description                                                  | Returns                                                 |
| --------------------------- | ------------------------------------------------------------ | ------------------------------------------------------- |
| **dsr://nodes**             | All nodes in the DSR graph with basic information            | JSON with nodes array, count, and DSR name              |
| **dsr://nodes/type/{type}** | Nodes filtered by type with full details (attributes, edges) | JSON with detailed nodes array, count, and type         |
| **dsr://nodes/{node_id}**   | Detailed information about a specific node                   | JSON with node details, attributes, and connected edges |
| **dsr://edges**             | All edges in the DSR graph                                   | JSON with edges array, count, and DSR name              |

## Environment Variables

| Variable       | Default    | Description                                |
| -------------- | ---------- | ------------------------------------------ |
| `DSR_AGENT_ID` | 42         | Unique agent identifier for DSR connection |
| `DSR_NAME`     | mcp_server | Target DSR graph name to connect to        |
| `SERVER_HOST`  | 127.0.0.1  | Server host address                        |
| `SERVER_PORT`  | 3000       | Server port number                         |

## Installation

### Dependencies

- **[fastmcp](https://github.com/jlowin/fastmcp)**: MCP server framework (>= 2.2.7)
- **[Cortex](https://github.com/grupo-avispa/cortex)**: DSR library for graph operations
- **Python**: 3.12+ required

> **Note:** You must build Cortex inside the virtual environment to ensure compatibility.
```bash
cd dsr_mcp_server
source .venv/bin/activate
cd ${CORTEX_DIR} && make -p build && cd build
cmake .. && make -j$(nproc) && sudo make install
```

### Install with uv (recommended)

Clone the repository and install with uv:

```bash
git clone https://github.com/grupo-avispa/dsr_mcp_server.git
cd dsr_mcp_server
uv sync
```

Or install directly from the repository:

```bash
uv add git+https://github.com/grupo-avispa/dsr_mcp_server.git
```

### Install with pip

Install the package in mode:

```bash
git clone https://github.com/grupo-avispa/dsr_mcp_server.git
cd dsr_mcp_server
python3 -m pip install .
```

Or install directly from the repository:

```bash
python3 -m pip install git+https://github.com/grupo-avispa/dsr_mcp_server.git
```

## Usage

### Running with uv

```bash
uv run dsr_mcp_server
```

### Running with pip installation

```bash
python3 -m dsr_mcp_server
```

The server will start and attempt to initialize the DSR connection automatically using the configured parameters.

### Configuration example for Claude Desktop/Cursor/VSCode

#### Using uv (recommended)

Add this configuration to your application's settings (mcp.json):

```json
{
  "dsr mcp server": {
    "type": "stdio",
    "command": "uv",
    "args": [
      "run",
      "--directory",
      "/path/to/dsr_mcp_server",
      "dsr_mcp_server"
    ],
    "env": {
      "DSR_AGENT_ID": "42",
      "DSR_NAME": "your_dsr_graph_name"
    }
  }
}
```

#### Using pip installation

```json
{
  "dsr mcp server": {
    "type": "stdio",
    "command": "python3",
    "args": [
      "-m",
      "dsr_mcp_server"
    ],
    "env": {
      "DSR_AGENT_ID": "42", 
      "DSR_NAME": "your_dsr_graph_name"
    }
  }
}
```

#### HTTP Server Mode

For HTTP transport integration:

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

## Technical Notes

* Connection to DSR is performed with automatic initialization and connection monitoring.
* Node attributes are filtered to exclude internal rendering properties (color, depth, height, level, etc.) for cleaner output.
* Edge relationships support various types including spatial (near), ownership (has), identity (is), and association (is_with) semantics.
* Graph operations maintain consistency through the DSR library's built-in validation mechanisms.
* All tools return standardized JSON responses with success/error status and detailed information.
* Interactive file selection for graph export operations through MCP elicit mechanism.
* **Resources** provide read-only, idempotent access to DSR graph data with efficient caching and lower overhead compared to tools. Use resources for querying data and tools for modifications.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes following the coding conventions
4. Add tests if applicable
5. Submit a pull request

## Support

For issues, questions, or contributions, please refer to the [project's issue tracker](https://github.com/grupo-avispa/dsr_mcp_server/issues) or contact the development team.
