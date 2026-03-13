"""Knowledge graph manager for graph-based knowledge representation."""

from typing import Any, Dict, List, Optional, Set, Tuple
from pydantic import BaseModel, Field
from datetime import datetime, timezone
from uuid import uuid4
import logging

from app.core.settings import get_settings

settings = get_settings()


class GraphNode(BaseModel):
    """Graph node model."""

    id: str = Field(default_factory=lambda: str(uuid4()))
    labels: List[str] = Field(default_factory=lambda: ["Entity"])
    properties: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class GraphRelationship(BaseModel):
    """Graph relationship model."""

    id: str = Field(default_factory=lambda: str(uuid4()))
    start_node_id: str
    end_node_id: str
    type: str  # Relationship type
    properties: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class GraphPath(BaseModel):
    """Graph path model."""

    nodes: List[GraphNode] = Field(default_factory=list)
    relationships: List[GraphRelationship] = Field(default_factory=list)
    length: int = 0


class EntityExtraction(BaseModel):
    """Entity extraction result."""

    entities: List[Dict[str, Any]] = Field(default_factory=list)
    relationships: List[Dict[str, Any]] = Field(default_factory=list)


class KnowledgeGraphManager:
    """Manager for graph-based knowledge representation.

    This class provides:
    - Node and relationship CRUD
    - Entity extraction
    - Relationship mapping
    - Graph traversal queries
    - Knowledge inference

    Supports multiple backends:
    - In-memory (default, for development)
    - Neo4j
    """

    def __init__(
        self,
        provider: str = "memory",
        config: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize knowledge graph manager.

        Args:
            provider: Graph provider (memory, neo4j).
            config: Provider-specific configuration.
        """
        self.provider = provider
        self.config = config or {}

        self._nodes: Dict[str, GraphNode] = {}
        self._relationships: Dict[str, GraphRelationship] = {}
        self._adjacency: Dict[str, Set[str]] = {}  # node_id -> neighbor_ids
        self._logger = logging.getLogger("knowledge.graph")

        # Initialize provider
        if provider == "neo4j":
            self._init_neo4j()

        self._logger.info(f"Initialized knowledge graph with provider: {provider}")

    def _init_neo4j(self) -> None:
        """Initialize Neo4j driver."""
        try:
            from neo4j import AsyncGraphDatabase

            uri = self.config.get("uri", "bolt://localhost:7687")
            user = self.config.get("user", "neo4j")
            password = self.config.get("password", "password")

            self._neo4j_driver = AsyncGraphDatabase.driver(
                uri,
                auth=(user, password),
            )

            self._logger.info("Neo4j connection established")

        except ImportError:
            raise ImportError("neo4j not installed. Install with: pip install neo4j")
        except Exception as e:
            self._logger.warning(f"Failed to initialize Neo4j: {e}. Falling back to memory store.")
            self.provider = "memory"

    async def create_node(self, node: GraphNode) -> GraphNode:
        """Create a graph node.

        Args:
            node: Node to create.

        Returns:
            GraphNode: Created node.
        """
        if self.provider == "memory":
            self._nodes[node.id] = node
            self._adjacency[node.id] = set()
        elif self.provider == "neo4j":
            await self._neo4j_create_node(node)

        self._logger.debug(f"Created graph node: {node.id}")
        return node

    async def create_relationship(
        self,
        relationship: GraphRelationship,
    ) -> GraphRelationship:
        """Create a graph relationship.

        Args:
            relationship: Relationship to create.

        Returns:
            GraphRelationship: Created relationship.
        """
        if self.provider == "memory":
            self._relationships[relationship.id] = relationship

            # Update adjacency
            if relationship.start_node_id not in self._adjacency:
                self._adjacency[relationship.start_node_id] = set()
            self._adjacency[relationship.start_node_id].add(relationship.end_node_id)

        elif self.provider == "neo4j":
            await self._neo4j_create_relationship(relationship)

        self._logger.debug(
            f"Created relationship: {relationship.start_node_id} -> "
            f"{relationship.end_node_id} ({relationship.type})"
        )
        return relationship

    async def get_node(self, node_id: str) -> Optional[GraphNode]:
        """Get a node by ID.

        Args:
            node_id: Node ID.

        Returns:
            Optional[GraphNode]: Node or None.
        """
        if self.provider == "memory":
            return self._nodes.get(node_id)
        elif self.provider == "neo4j":
            return await self._neo4j_get_node(node_id)
        return None

    async def get_relationship(self, relationship_id: str) -> Optional[GraphRelationship]:
        """Get a relationship by ID.

        Args:
            relationship_id: Relationship ID.

        Returns:
            Optional[GraphRelationship]: Relationship or None.
        """
        if self.provider == "memory":
            return self._relationships.get(relationship_id)
        elif self.provider == "neo4j":
            return await self._neo4j_get_relationship(relationship_id)
        return None

    async def delete_node(self, node_id: str) -> bool:
        """Delete a node.

        Args:
            node_id: Node ID.

        Returns:
            bool: True if deleted.
        """
        if self.provider == "memory":
            if node_id in self._nodes:
                del self._nodes[node_id]

                # Remove from adjacency
                if node_id in self._adjacency:
                    del self._adjacency[node_id]

                # Remove references
                for neighbors in self._adjacency.values():
                    neighbors.discard(node_id)

                # Remove relationships
                rel_ids = [
                    rel_id
                    for rel_id, rel in self._relationships.items()
                    if rel.start_node_id == node_id or rel.end_node_id == node_id
                ]
                for rel_id in rel_ids:
                    del self._relationships[rel_id]

                return True
        elif self.provider == "neo4j":
            return await self._neo4j_delete_node(node_id)

        return False

    async def delete_relationship(self, relationship_id: str) -> bool:
        """Delete a relationship.

        Args:
            relationship_id: Relationship ID.

        Returns:
            bool: True if deleted.
        """
        if self.provider == "memory":
            if relationship_id in self._relationships:
                rel = self._relationships[relationship_id]

                # Update adjacency
                if rel.start_node_id in self._adjacency:
                    self._adjacency[rel.start_node_id].discard(rel.end_node_id)

                del self._relationships[relationship_id]
                return True
        elif self.provider == "neo4j":
            return await self._neo4j_delete_relationship(relationship_id)

        return False

    async def find_paths(
        self,
        start_node_id: str,
        end_node_id: str,
        max_depth: int = 5,
        relationship_types: Optional[List[str]] = None,
    ) -> List[GraphPath]:
        """Find paths between nodes.

        Args:
            start_node_id: Start node ID.
            end_node_id: End node ID.
            max_depth: Maximum path depth.
            relationship_types: Optional relationship type filter.

        Returns:
            List[GraphPath]: Paths found.
        """
        if self.provider == "memory":
            return self._memory_find_paths(
                start_node_id,
                end_node_id,
                max_depth,
                relationship_types,
            )
        elif self.provider == "neo4j":
            return await self._neo4j_find_paths(
                start_node_id,
                end_node_id,
                max_depth,
                relationship_types,
            )

        return []

    async def traverse(
        self,
        start_node_id: str,
        direction: str = "outgoing",
        max_depth: int = 3,
        relationship_types: Optional[List[str]] = None,
    ) -> GraphPath:
        """Traverse graph from a node.

        Args:
            start_node_id: Start node ID.
            direction: Traversal direction (outgoing, incoming, both).
            max_depth: Maximum traversal depth.
            relationship_types: Optional relationship type filter.

        Returns:
            GraphPath: Traversal result.
        """
        if self.provider == "memory":
            return self._memory_traverse(
                start_node_id,
                direction,
                max_depth,
                relationship_types,
            )
        elif self.provider == "neo4j":
            return await self._neo4j_traverse(
                start_node_id,
                direction,
                max_depth,
                relationship_types,
            )

        return GraphPath()

    async def extract_entities(self, text: str) -> EntityExtraction:
        """Extract entities and relationships from text.

        Args:
            text: Text to extract from.

        Returns:
            EntityExtraction: Extracted entities and relationships.
        """
        # Simple rule-based extraction (can be enhanced with NLP/LLM)
        entities = []
        relationships = []

        # Extract potential entities (capitalized words, numbers)
        import re

        # Person names (simple pattern)
        person_pattern = r"\b([A-Z][a-z]+ [A-Z][a-z]+)\b"
        for match in re.finditer(person_pattern, text):
            entities.append({
                "text": match.group(1),
                "type": "Person",
                "start": match.start(),
                "end": match.end(),
            })

        # Organizations (words ending with common suffixes)
        org_pattern = r"\b([A-Z][a-zA-Z]+ (Inc|Corp|LLC|Ltd|Company|Organization))\b"
        for match in re.finditer(org_pattern, text, re.IGNORECASE):
            entities.append({
                "text": match.group(1),
                "type": "Organization",
                "start": match.start(),
                "end": match.end(),
            })

        # Dates
        date_pattern = r"\b(\d{1,2}/\d{1,2}/\d{2,4}|\w+ \d{1,2}, \d{4})\b"
        for match in re.finditer(date_pattern, text):
            entities.append({
                "text": match.group(1),
                "type": "Date",
                "start": match.start(),
                "end": match.end(),
            })

        # Extract relationships based on patterns
        # "X works at Y" pattern
        works_at_pattern = r"([A-Z][a-z]+ [A-Z][a-z]+) works at ([A-Z][a-zA-Z]+)"
        for match in re.finditer(works_at_pattern, text):
            relationships.append({
                "type": "WORKS_AT",
                "source": match.group(1),
                "target": match.group(2),
            })

        # "X is the CEO of Y" pattern
        ceo_pattern = r"([A-Z][a-z]+ [A-Z][a-z]+) is the .* of ([A-Z][a-zA-Z]+)"
        for match in re.finditer(ceo_pattern, text):
            relationships.append({
                "type": "LEADS",
                "source": match.group(1),
                "target": match.group(2),
            })

        return EntityExtraction(entities=entities, relationships=relationships)

    async def create_entities_from_extraction(
        self,
        extraction: EntityExtraction,
    ) -> Tuple[List[GraphNode], List[GraphRelationship]]:
        """Create graph entities from extraction results.

        Args:
            extraction: Entity extraction results.

        Returns:
            Tuple: Created nodes and relationships.
        """
        nodes = []
        relationships = []

        # Create nodes for entities
        entity_map = {}
        for entity_data in extraction.entities:
            node = GraphNode(
                labels=[entity_data.get("type", "Entity")],
                properties={
                    "text": entity_data.get("text"),
                    "start_offset": entity_data.get("start"),
                    "end_offset": entity_data.get("end"),
                },
            )
            await self.create_node(node)
            nodes.append(node)
            entity_map[entity_data.get("text")] = node.id

        # Create relationships
        for rel_data in extraction.relationships:
            source_id = entity_map.get(rel_data.get("source"))
            target_id = entity_map.get(rel_data.get("target"))

            if source_id and target_id:
                relationship = GraphRelationship(
                    start_node_id=source_id,
                    end_node_id=target_id,
                    type=rel_data.get("type", "RELATED_TO"),
                )
                await self.create_relationship(relationship)
                relationships.append(relationship)

        return nodes, relationships

    async def infer_knowledge(self, node_id: str) -> List[Dict[str, Any]]:
        """Infer new knowledge from graph structure.

        Args:
            node_id: Node to infer from.

        Returns:
            List[Dict]: Inferred knowledge.
        """
        inferences = []

        # Get all relationships for the node
        node = await self.get_node(node_id)
        if not node:
            return inferences

        # Find indirect relationships (transitive inference)
        # If A -> B and B -> C, then A -> C (for certain relationship types)
        path = await self.traverse(node_id, max_depth=2)

        for i, rel in enumerate(path.relationships[:-1]):
            next_rel = path.relationships[i + 1]

            # Transitive relationship types
            if rel.type in ["PART_OF", "SUBCLASS_OF", "RELATED_TO"]:
                inferred_type = f"INFERRED_{rel.type}"
                inferences.append({
                    "type": inferred_type,
                    "source": rel.start_node_id,
                    "target": next_rel.end_node_id,
                    "confidence": 0.7,  # Lower confidence for inferred
                    "via": [rel.id, next_rel.id],
                })

        return inferences

    async def get_statistics(self) -> Dict[str, Any]:
        """Get graph statistics.

        Returns:
            Dict: Statistics.
        """
        if self.provider == "memory":
            node_count = len(self._nodes)
            relationship_count = len(self._relationships)

            # Count by labels
            labels_count: Dict[str, int] = {}
            for node in self._nodes.values():
                for label in node.labels:
                    labels_count[label] = labels_count.get(label, 0) + 1

            # Count by relationship type
            rel_types_count: Dict[str, int] = {}
            for rel in self._relationships.values():
                rel_types_count[rel.type] = rel_types_count.get(rel.type, 0) + 1

            return {
                "provider": self.provider,
                "node_count": node_count,
                "relationship_count": relationship_count,
                "nodes_by_label": labels_count,
                "relationships_by_type": rel_types_count,
                "avg_degree": (
                    relationship_count * 2 / node_count if node_count > 0 else 0
                ),
            }

        return {}

    # ========== Memory Implementation Methods ==========

    def _memory_find_paths(
        self,
        start_node_id: str,
        end_node_id: str,
        max_depth: int,
        relationship_types: Optional[List[str]],
    ) -> List[GraphPath]:
        """In-memory path finding using BFS."""
        paths = []

        def bfs(current_id: str, target_id: str, depth: int, path_nodes: List[str], path_rels: List[str]):
            if depth > max_depth:
                return

            if current_id == target_id:
                # Found a path
                nodes = [self._nodes[nid] for nid in path_nodes if nid in self._nodes]
                rels = [self._relationships[rid] for rid in path_rels if rid in self._relationships]
                paths.append(GraphPath(nodes=nodes, relationships=rels, length=len(rels)))
                return

            # Explore neighbors
            neighbors = self._adjacency.get(current_id, set())
            for neighbor_id in neighbors:
                # Find relationship
                rel = next(
                    (
                        r for r in self._relationships.values()
                        if r.start_node_id == current_id and r.end_node_id == neighbor_id
                    ),
                    None,
                )

                if rel and (not relationship_types or rel.type in relationship_types):
                    bfs(
                        neighbor_id,
                        target_id,
                        depth + 1,
                        path_nodes + [neighbor_id],
                        path_rels + [rel.id],
                    )

        bfs(start_node_id, end_node_id, 0, [start_node_id], [])
        return paths

    def _memory_traverse(
        self,
        start_node_id: str,
        direction: str,
        max_depth: int,
        relationship_types: Optional[List[str]],
    ) -> GraphPath:
        """In-memory graph traversal."""
        visited = set()
        nodes = []
        relationships = []

        def dfs(current_id: str, depth: int):
            if depth > max_depth or current_id in visited:
                return

            visited.add(current_id)

            node = self._nodes.get(current_id)
            if node:
                nodes.append(node)

            # Get neighbors based on direction
            if direction in ["outgoing", "both"]:
                neighbors = self._adjacency.get(current_id, set())
                for neighbor_id in neighbors:
                    rel = next(
                        (
                            r for r in self._relationships.values()
                            if r.start_node_id == current_id and r.end_node_id == neighbor_id
                        ),
                        None,
                    )
                    if rel and (not relationship_types or rel.type in relationship_types):
                        relationships.append(rel)
                        dfs(neighbor_id, depth + 1)

            if direction in ["incoming", "both"]:
                for rel in self._relationships.values():
                    if rel.end_node_id == current_id:
                        if relationship_types and rel.type not in relationship_types:
                            continue
                        relationships.append(rel)
                        dfs(rel.start_node_id, depth + 1)

        dfs(start_node_id, 0)
        return GraphPath(nodes=nodes, relationships=relationships, length=len(relationships))

    # ========== Neo4j Implementation Methods ==========

    async def _neo4j_create_node(self, node: GraphNode) -> None:
        """Neo4j node creation."""
        if not hasattr(self, "_neo4j_driver"):
            return

        async with self._neo4j_driver.session() as session:
            labels = ":".join(node.labels)
            properties = {
                **node.properties,
                "created_at": node.created_at.isoformat(),
            }

            await session.run(
                f"""
                CREATE (n:{labels} {{id: $id}})
                SET n += $properties
                """,
                id=node.id,
                properties=properties,
            )

    async def _neo4j_create_relationship(self, relationship: GraphRelationship) -> None:
        """Neo4j relationship creation."""
        if not hasattr(self, "_neo4j_driver"):
            return

        async with self._neo4j_driver.session() as session:
            await session.run(
                f"""
                MATCH (a {{id: $start_id}})
                MATCH (b {{id: $end_id}})
                CREATE (a)-[r:{relationship.type} {{id: $id}}]->(b)
                SET r += $properties
                """,
                start_id=relationship.start_node_id,
                end_id=relationship.end_node_id,
                id=relationship.id,
                properties=relationship.properties,
            )

    async def _neo4j_get_node(self, node_id: str) -> Optional[GraphNode]:
        """Neo4j node retrieval."""
        if not hasattr(self, "_neo4j_driver"):
            return None

        async with self._neo4j_driver.session() as session:
            result = await session.run(
                "MATCH (n {{id: $id}}) RETURN n",
                id=node_id,
            )
            record = await result.single()

            if record:
                node_data = record["n"]
                return GraphNode(
                    id=node_data.get("id"),
                    labels=list(node_data.labels),
                    properties=dict(node_data),
                )

        return None

    async def _neo4j_get_relationship(
        self,
        relationship_id: str,
    ) -> Optional[GraphRelationship]:
        """Neo4j relationship retrieval."""
        if not hasattr(self, "_neo4j_driver"):
            return None

        async with self._neo4j_driver.session() as session:
            result = await session.run(
                "MATCH ()-[r {{id: $id}}]->() RETURN r",
                id=relationship_id,
            )
            record = await result.single()

            if record:
                rel_data = record["r"]
                return GraphRelationship(
                    id=rel_data.get("id"),
                    type=list(rel_data.types)[0],
                    properties=dict(rel_data),
                )

        return None

    async def _neo4j_delete_node(self, node_id: str) -> bool:
        """Neo4j node deletion."""
        if not hasattr(self, "_neo4j_driver"):
            return False

        async with self._neo4j_driver.session() as session:
            await session.run(
                "MATCH (n {id: $id}) DETACH DELETE n",
                id=node_id,
            )
        return True

    async def _neo4j_delete_relationship(self, relationship_id: str) -> bool:
        """Neo4j relationship deletion."""
        if not hasattr(self, "_neo4j_driver"):
            return False

        async with self._neo4j_driver.session() as session:
            await session.run(
                "MATCH ()-[r {id: $id}]->() DELETE r",
                id=relationship_id,
            )
        return True

    async def _neo4j_find_paths(
        self,
        start_node_id: str,
        end_node_id: str,
        max_depth: int,
        relationship_types: Optional[List[str]],
    ) -> List[GraphPath]:
        """Neo4j path finding."""
        if not hasattr(self, "_neo4j_driver"):
            return []

        async with self._neo4j_driver.session() as session:
            type_filter = ""
            if relationship_types:
                types = "|".join(relationship_types)
                type_filter = f"*{types}"

            result = await session.run(
                f"""
                MATCH path = (start {{id: $start_id}})-[r{type_filter}*..{max_depth}]->(end {{id: $end_id}})
                RETURN path
                LIMIT 10
                """,
                start_id=start_node_id,
                end_id=end_node_id,
            )

            paths = []
            async for record in result:
                path_data = record["path"]
                # Convert Neo4j path to GraphPath
                # (simplified - full implementation would extract nodes and relationships)
                paths.append(GraphPath(length=len(path_data.relationships)))

            return paths

    async def _neo4j_traverse(
        self,
        start_node_id: str,
        direction: str,
        max_depth: int,
        relationship_types: Optional[List[str]],
    ) -> GraphPath:
        """Neo4j graph traversal."""
        if not hasattr(self, "_neo4j_driver"):
            return GraphPath()

        async with self._neo4j_driver.session() as session:
            dir_clause = ""
            if direction == "outgoing":
                dir_clause = "-[r]>"
            elif direction == "incoming":
                dir_clause = "<-[r]-"
            else:
                dir_clause = "-[r]-"

            type_filter = ""
            if relationship_types:
                types = "|".join(relationship_types)
                type_filter = f":{types}"

            result = await session.run(
                f"""
                MATCH (start {{id: $start_id}})
                CALL apoc.path.subgraphNodes(start, {{
                    relationshipFilter: "{type_filter}",
                    maxLevel: {max_depth}
                }}) YIELD node
                RETURN node
                """,
                start_id=start_node_id,
            )

            nodes = []
            async for record in result:
                node_data = record["node"]
                nodes.append(
                    GraphNode(
                        id=node_data.get("id"),
                        labels=list(node_data.labels),
                        properties=dict(node_data),
                    )
                )

            return GraphPath(nodes=nodes)
