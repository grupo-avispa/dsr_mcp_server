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

"""DSR client wrapper for graph operations."""

from typing import Optional, Dict, Any, List
from fastmcp.utilities.logging import get_logger
from pydsr import DSRGraph, Node, Edge, Attribute

from .config import DSRConfig


class DSRClient:
    """
    DSR client for managing graph operations.

    This class provides a high-level interface for interacting with
    the DSR graph, handling connection management and common operations.
    """

    def __init__(self):
        """Initialize the DSR client."""
        self.dsr_graph: Optional[DSRGraph] = None
        self.logger = get_logger(__name__)
        self.config = DSRConfig()

    def initialize(self) -> bool:
        """
        Initialize DSR connection.

        Returns:
            bool: True if connection successful, False otherwise.
        """
        try:
            self.dsr_graph = DSRGraph(
                0, self.config.DSR_NAME, self.config.AGENT_ID
            )
            return True
        except (ImportError, RuntimeError, ConnectionError) as e:
            self.logger.error(f'Error initializing DSR: {e}')
            return False

    def check_connection(self) -> Dict[str, Any]:
        """
        Check DSR connection status.

        Returns:
            Dict[str, Any]: Connection status information.
        """
        if self.dsr_graph is None:
            return {
                'connected': False,
                'message': 'DSR not initialized',
                'agent_id': self.config.AGENT_ID,
                'dsr_name': self.config.DSR_NAME
            }

        try:
            # Try to get root node to test connection
            root_node = self.dsr_graph.get_node_root()
            return {
                'connected': True,
                'message': 'DSR connection active',
                'agent_id': self.config.AGENT_ID,
                'dsr_name': self.config.DSR_NAME,
                'root_node_id': root_node.id if root_node else None
            }
        except (AttributeError, RuntimeError) as e:
            return {
                'connected': False,
                'message': f'DSR connection error: {str(e)}',
                'agent_id': self.config.AGENT_ID,
                'dsr_name': self.config.DSR_NAME
            }

    def is_connected(self) -> bool:
        """
        Check if DSR is connected.

        Returns:
            bool: True if connected, False otherwise.
        """
        return self.dsr_graph is not None

    def get_all_nodes(self) -> List[Any]:
        """
        Get all nodes from the DSR graph.

        Returns:
            List[Any]: List of all nodes in the graph.

        Raises:
            RuntimeError: If DSR is not initialized or connection fails.
        """
        if not self.is_connected():
            raise RuntimeError('DSR not initialized')

        assert self.dsr_graph is not None
        try:
            return list(self.dsr_graph.get_nodes())
        except (AttributeError, RuntimeError) as e:
            raise RuntimeError(f'Error retrieving nodes: {str(e)}') from e

    def get_nodes_by_type(self, node_type: str) -> List[Any]:
        """
        Get nodes filtered by type.

        Args:
            node_type (str): The type of nodes to retrieve.

        Returns:
            List[Any]: List of nodes of the specified type.

        Raises:
            RuntimeError: If DSR is not initialized or operation fails.
        """
        if not self.is_connected():
            raise RuntimeError('DSR not initialized')

        assert self.dsr_graph is not None
        try:
            return list(self.dsr_graph.get_nodes_by_type(node_type))
        except (AttributeError, RuntimeError) as e:
            raise RuntimeError(
                f'Error retrieving nodes by type: {str(e)}'
            ) from e

    def get_node_by_id(self, node_id: int) -> Optional[Any]:
        """
        Get a node by its ID.

        Args:
            node_id (int): The ID of the node to retrieve.

        Returns:
            Optional[Any]: The node if found, None otherwise.

        Raises:
            RuntimeError: If DSR is not initialized.
        """
        if not self.is_connected():
            raise RuntimeError('DSR not initialized')

        assert self.dsr_graph is not None
        return self.dsr_graph.get_node(node_id)

    def get_node_attributes(self, node: Any) -> Dict[str, Dict[str, str]]:
        """
        Retrieve all attributes of a node.

        Args:
            node (Node): Node object from DSRGraph.

        Returns:
            Dict[str, Dict[str, str]]: Dictionary of attribute names and
            their details (value, type, timestamp).
        """
        attributes: Dict[str, Dict[str, str]] = {}
        if hasattr(node, 'attrs'):
            for attr_name in node.attrs:
                if attr_name in self.config.EXCLUDED_NODE_ATTRIBUTES:
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

    def get_node_edges(self, node: Any) -> List[Dict[str, Any]]:
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
                edges = self._get_node_edges_fallback(node, e)

        # Additionally, use DSRGraph to get incoming edges to this node
        if self.dsr_graph is not None:
            try:
                # Get edges that point to this node (incoming edges)
                incoming_edges = self.dsr_graph.get_edges_to_id(node.id)
                for edge in incoming_edges:
                    # Check if this edge is already in our list to avoid
                    # duplicates
                    edge_exists = any(
                        e.get('from') == str(edge.origin) and
                        e.get('to') == str(edge.destination) and
                        e.get('type') == str(edge.type)
                        for e in edges if 'error' not in e
                    )

                    if not edge_exists:
                        incoming_edge_attrs = self._get_edge_attributes(edge)
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

    def _get_node_edges_fallback(
        self,
        node: Any,
        original_error: Exception
    ) -> List[Dict[str, Any]]:
        """
        Fallback method to get node edges when primary method fails.

        Args:
            node (Node): The node to get edges for.
            original_error (Exception): The original error that occurred.

        Returns:
            List[Dict[str, Any]]: List of edges or error information.
        """
        if hasattr(node, 'get_edges'):
            try:
                edges = []
                for edge in node.get_edges():
                    fallback_edge_attrs = self._get_edge_attributes(edge)
                    edges.append({
                        'origin': str(edge.origin),
                        'destination': str(edge.destination),
                        'type': str(edge.type),
                        'attributes': fallback_edge_attrs,
                    })
                return edges
            except (AttributeError, RuntimeError):
                return [{'error': f'Could not access edges: {original_error}'}]
        else:
            return [{'error': f'Could not access edges: {original_error}'}]

    def _get_edge_attributes(self, edge: Any) -> Dict[str, Dict[str, str]]:
        """
        Get attributes from an edge.

        Args:
            edge (Edge): The edge to get attributes from.

        Returns:
            Dict[str, Dict[str, str]]: Dictionary of edge attributes.
        """
        edge_attrs: Dict[str, Dict[str, str]] = {}
        if hasattr(edge, 'attrs'):
            for attr_name in edge.attrs:
                try:
                    edge_attrs[attr_name] = {
                        'value': str(edge.attrs[attr_name].value),
                        'type': type(edge.attrs[attr_name].value).__name__,
                    }
                except (AttributeError, KeyError, TypeError):
                    edge_attrs[attr_name] = {
                        'error': 'Could not access'
                    }
        return edge_attrs

    def get_all_edges(self) -> List[Dict[str, Any]]:
        """
        Get all edges from the DSR graph.

        Returns:
            List[Dict[str, Any]]: List of all edges with basic information.

        Raises:
            RuntimeError: If DSR is not initialized or operation fails.
        """
        if not self.is_connected():
            raise RuntimeError('DSR not initialized')

        assert self.dsr_graph is not None
        try:
            edges_data = []
            for node in self.dsr_graph.get_nodes():
                for destination_id, edge_type in self.dsr_graph.get_edges(
                    node.id
                ):
                    edges_data.append({
                        'origin': str(node.id),
                        'destination': str(destination_id),
                        'type': edge_type
                    })
            return edges_data
        except (AttributeError, RuntimeError, TypeError) as e:
            raise RuntimeError(f'Error retrieving edges: {str(e)}') from e

    def insert_node(self, name: str, node_type: str) -> int:
        """
        Insert a new node into the DSR graph.

        Args:
            name (str): The name of the node.
            node_type (str): The type of the node.

        Returns:
            int: The ID of the inserted node.

        Raises:
            RuntimeError: If DSR is not initialized or insertion fails.
        """
        if not self.is_connected():
            raise RuntimeError('DSR not initialized')

        assert self.dsr_graph is not None
        try:
            node = Node(self.config.AGENT_ID, node_type, name)
            node_id = self.dsr_graph.insert_node(node)
            return node_id
        except (AttributeError, RuntimeError, ValueError) as e:
            raise RuntimeError(f'Error inserting node: {str(e)}') from e

    def insert_edge(
        self,
        origin_id: int,
        destination_id: int,
        edge_type: str
    ) -> bool:
        """
        Insert a new edge between two nodes.

        Args:
            origin_id (int): ID of the origin node.
            destination_id (int): ID of the destination node.
            edge_type (str): Type of the edge.

        Returns:
            bool: True if edge was inserted successfully.

        Raises:
            RuntimeError: If DSR is not initialized or insertion fails.
        """
        if not self.is_connected():
            raise RuntimeError('DSR not initialized')

        assert self.dsr_graph is not None
        try:
            edge = Edge(destination_id, origin_id,
                        edge_type, self.config.AGENT_ID)
            return self.dsr_graph.insert_or_assign_edge(edge)
        except (AttributeError, RuntimeError, ValueError) as e:
            raise RuntimeError(f'Error inserting edge: {str(e)}') from e

    def insert_edge_attribute(
        self,
        origin_id: int,
        destination_id: int,
        attribute_name: str,
        attribute_value: Any
    ) -> bool:
        """
        Insert or update an attribute for an edge.

        Args:
            origin_id (int): ID of the origin node.
            destination_id (int): ID of the destination node.
            attribute_name (str): Name of the attribute.
            attribute_value (Any): Value of the attribute.

        Returns:
            bool: True if attribute was inserted successfully.

        Raises:
            RuntimeError: If DSR is not initialized or insertion fails.
        """
        if not self.is_connected():
            raise RuntimeError('DSR not initialized')

        assert self.dsr_graph is not None
        try:
            return self.dsr_graph.insert_edge_attribute(
                origin_id, destination_id, attribute_name, attribute_value
            )
        except (AttributeError, RuntimeError, ValueError) as e:
            raise RuntimeError(
                f'Error inserting edge attribute: {str(e)}') from e

    def update_node(
        self,
        node_id: int,
        attribute_name: str,
        attribute_value: Any
    ) -> bool:
        """
        Update a node with a new attribute.

        Args:
            node_id (int): ID of the node to update.
            attribute_name (str): Name of the attribute.
            attribute_value (Any): Value of the attribute.

        Returns:
            bool: True if node was updated successfully.

        Raises:
            RuntimeError: If DSR is not initialized, node not found, or
                         update fails.
        """
        if not self.is_connected():
            raise RuntimeError('DSR not initialized')

        assert self.dsr_graph is not None
        try:
            # Get the existing node
            node = self.dsr_graph.get_node(node_id)
            if node is None:
                raise RuntimeError(f'Node {node_id} not found')

            # Create DSR Attribute and add it to the node
            attribute = Attribute(attribute_value, self.config.AGENT_ID)
            node.attrs[attribute_name] = attribute

            # Update the node in the graph
            return self.dsr_graph.update_node(node)
        except (AttributeError, RuntimeError, ValueError) as e:
            raise RuntimeError(f'Error updating node: {str(e)}') from e

    def delete_node(self, node_id: int) -> bool:
        """
        Delete a node from the DSR graph.

        Args:
            node_id (int): ID of the node to delete.

        Returns:
            bool: True if node was deleted successfully.

        Raises:
            RuntimeError: If DSR is not initialized or deletion fails.
        """
        if not self.is_connected():
            raise RuntimeError('DSR not initialized')

        assert self.dsr_graph is not None
        try:
            return self.dsr_graph.delete_node(node_id)
        except (AttributeError, RuntimeError, ValueError) as e:
            raise RuntimeError(f'Error deleting node: {str(e)}') from e

    def delete_edge(
        self,
        origin_id: int,
        destination_id: int,
        edge_type: str
    ) -> bool:
        """
        Delete an edge from the DSR graph.

        Args:
            origin_id (int): ID of the origin node.
            destination_id (int): ID of the destination node.
            edge_type (str): Type of the edge.

        Returns:
            bool: True if edge was deleted successfully.

        Raises:
            RuntimeError: If DSR is not initialized or deletion fails.
        """
        if not self.is_connected():
            raise RuntimeError('DSR not initialized')

        assert self.dsr_graph is not None
        try:
            return self.dsr_graph.delete_edge(
                origin_id, destination_id, edge_type
            )
        except (AttributeError, RuntimeError, ValueError) as e:
            raise RuntimeError(f'Error deleting edge: {str(e)}') from e

    def save_graph(self, file_path: str) -> None:
        """
        Save the current state of the DSR graph to a JSON file.

        Args:
            file_path (str): Path where to save the graph.

        Raises:
            RuntimeError: If DSR is not initialized or save fails.
        """
        if not self.is_connected():
            raise RuntimeError('DSR not initialized')

        assert self.dsr_graph is not None
        try:
            self.dsr_graph.write_to_json_file(file_path, skip_atts=[])
        except (AttributeError, RuntimeError, ValueError) as e:
            raise RuntimeError(
                f'Error saving DSR graph to JSON: {str(e)}') from e
