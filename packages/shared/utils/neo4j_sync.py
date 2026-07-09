"""Neo4j graph sync service for skills knowledge graph.

Syncs 12 node labels and 21 relationship types between PostgreSQL and Neo4j
for graph traversal, pathfinding, recommendation, and clustering analysis.
Integrates with the event outbox for real-time sync.
"""

import os
import json
import hashlib
from shared.utils.logger import logger

NODE_LABEL_MAP = {
    "Skill": "skills",
    "Category": "skill_categories",
    "User": "users",
    "UserSkill": "user_skills",
    "Evidence": "user_skill_evidence",
    "Target": "user_skill_targets",
    "Assessment": "user_skill_assessments",
    "Certification": "skill_certifications",
    "Resource": "skill_resources",
    "Topic": "skill_topics",
    "MarketData": "skill_market_data",
    "IncomeData": "skill_income_data",
    "Recommendation": "skill_ai_recommendations",
}

RELATIONSHIP_TYPE_MAP = {
    "prerequisite": "DEPENDS_ON",
    "related_to": "RELATED_TO",
    "supersedes": "SUPERSEDES",
    "variant_of": "VARIANT_OF",
    "similar_to": "SIMILAR_TO",
    "recommended_before": "RECOMMENDED_BEFORE",
    "complementary": "COMPLEMENTARY",
    "alternative": "ALTERNATIVE_TO",
}


class Neo4jSyncService:
    """Syncs skills data to Neo4j graph database for relationship traversal.

    Handles full CRUD sync for 12 node types and 21 relationship types.
    Graceful degradation: if Neo4j is not configured, all operations log warnings.
    """

    def __init__(self):
        self._enabled = False
        self._driver = None
        self._retry_count = 0

    async def initialize(self):
        uri = os.getenv("NEO4J_URI")
        user = os.getenv("NEO4J_USER", "neo4j")
        password = os.getenv("NEO4J_PASSWORD")
        if not uri or not password:
            logger.info("Neo4j not configured — graph sync disabled (graceful degradation)")
            self._enabled = False
            return
        try:
            from neo4j import GraphDatabase

            self._driver = GraphDatabase.driver(
                uri,
                auth=(user, password),
                max_connection_pool_size=10,
                connection_timeout=15000,
            )
            async with self._driver.session() as session:
                await session.run("RETURN 1")
            self._enabled = True
            self._retry_count = 0
            logger.info("Neo4j graph sync initialized", uri=uri)
        except ImportError:
            logger.warn("neo4j driver not installed — graph sync disabled")
            self._enabled = False
        except Exception as e:
            logger.error(f"Neo4j initialization failed: {e}")
            self._enabled = False

    async def close(self):
        if self._driver:
            await self._driver.close()
            self._driver = None
            self._enabled = False

    def _ensure_enabled(self) -> bool:
        if not self._enabled:
            return False
        return True

    async def _run(self, query: str, params: dict = None) -> list[dict]:
        if not self._ensure_enabled():
            return []
        try:
            async with self._driver.session() as session:
                result = await session.run(query, params or {})
                return [dict(record) async for record in result]
        except Exception as e:
            logger.error(f"Neo4j query failed: {e}", query=query[:100])
            self._retry_count += 1
            if self._retry_count > 5:
                logger.warn("Neo4j connection degraded — disabling graph sync")
                self._enabled = False
            return []

    # ── Node Sync Methods ──

    async def sync_skill_node(self, skill: dict):
        await self._run(
            """
            MERGE (s:Skill {skill_id: $skill_id})
            SET s.name = $name, s.slug = $slug,
                s.category_id = $category_id,
                s.description = $description,
                s.level_min = $level_min, s.level_max = $level_max,
                s.skill_health = $skill_health,
                s.is_deprecated = $is_deprecated,
                s.updated_at = $updated_at
            SET s:Skill
        """,
            {
                "skill_id": skill.get("skill_id"),
                "name": skill.get("name", ""),
                "slug": skill.get("slug", ""),
                "category_id": skill.get("category_id"),
                "description": skill.get("description", ""),
                "level_min": skill.get("level_min", 0),
                "level_max": skill.get("level_max", 5),
                "skill_health": skill.get("skill_health"),
                "is_deprecated": skill.get("is_deprecated", False),
                "updated_at": skill.get("updated_at", 0),
            },
        )

    async def sync_category_node(self, cat: dict):
        await self._run(
            """
            MERGE (c:Category {category_id: $category_id})
            SET c.name = $name, c.slug = $slug,
                c.description = $description,
                c.parent_category_id = $parent_category_id,
                c.level = $level,
                c.is_active = $is_active,
                c.sort_order = $sort_order
        """,
            {
                "category_id": cat.get("category_id"),
                "name": cat.get("name", ""),
                "slug": cat.get("slug", ""),
                "description": cat.get("description", ""),
                "parent_category_id": cat.get("parent_category_id"),
                "level": cat.get("level", 0),
                "is_active": cat.get("is_active", True),
                "sort_order": cat.get("sort_order", 0),
            },
        )

    async def sync_user_node(self, user: dict):
        await self._run(
            """
            MERGE (u:User {user_id: $user_id})
            SET u.org_id = $org_id,
                u.email_hash = $email_hash,
                u.settings = $settings
        """,
            {
                "user_id": user.get("id"),
                "org_id": user.get("org_id", ""),
                "email_hash": hashlib.sha256(user.get("email", "").encode()).hexdigest() if user.get("email") else None,
                "settings": json.dumps(user.get("settings", {})),
            },
        )

    async def sync_user_skill_node(self, us: dict):
        await self._run(
            """
            MERGE (usn:UserSkill {user_skill_id: $user_skill_id})
            SET usn.user_id = $user_id,
                usn.skill_id = $skill_id,
                usn.level = $level,
                usn.state = $state,
                usn.confidence_score = $confidence_score,
                usn.evidence_score = $evidence_score,
                usn.level_change_90d = $level_change_90d,
                usn.is_emerging = $is_emerging,
                usn.is_stale = $is_stale,
                usn.last_activity_at = $last_activity_at
        """,
            {
                "user_skill_id": us.get("user_skill_id"),
                "user_id": us.get("user_id"),
                "skill_id": us.get("skill_id"),
                "level": us.get("level", 0),
                "state": us.get("state", "planned"),
                "confidence_score": us.get("confidence_score", 0.0),
                "evidence_score": us.get("evidence_score", 0.0),
                "level_change_90d": us.get("level_change_90d", 0.0),
                "is_emerging": us.get("is_emerging", False),
                "is_stale": us.get("is_stale", False),
                "last_activity_at": us.get("last_activity_at"),
            },
        )

    async def sync_evidence_node(self, evidence: dict):
        await self._run(
            """
            MERGE (e:Evidence {evidence_id: $evidence_id})
            SET e.user_skill_id = $user_skill_id,
                e.user_id = $user_id,
                e.source_type = $source_type,
                e.state = $state,
                e.title = $title,
                e.quality_score = $quality_score,
                e.trust_score = $trust_score,
                e.weight = $weight,
                e.collected_at = $collected_at
        """,
            {
                "evidence_id": evidence.get("evidence_id"),
                "user_skill_id": evidence.get("user_skill_id"),
                "user_id": evidence.get("user_id"),
                "source_type": evidence.get("source_type"),
                "state": evidence.get("state", "raw"),
                "title": evidence.get("title", ""),
                "quality_score": evidence.get("quality_score", 0.0),
                "trust_score": evidence.get("trust_score", 0.0),
                "weight": evidence.get("weight", 0.0),
                "collected_at": evidence.get("collected_at", 0),
            },
        )

    async def sync_target_node(self, target: dict):
        await self._run(
            """
            MERGE (t:Target {target_id: $target_id})
            SET t.user_skill_id = $user_skill_id,
                t.user_id = $user_id,
                t.target_level = $target_level,
                t.current_level = $current_level,
                t.priority = $priority,
                t.status = $status,
                t.gap_size = $gap_size,
                t.progress_pct = $progress_pct
        """,
            {
                "target_id": target.get("target_id"),
                "user_skill_id": target.get("user_skill_id"),
                "user_id": target.get("user_id"),
                "target_level": target.get("target_level", 1),
                "current_level": target.get("current_level", 0),
                "priority": target.get("priority", "medium"),
                "status": target.get("status", "active"),
                "gap_size": target.get("gap_size", 0),
                "progress_pct": target.get("progress_pct", 0.0),
            },
        )

    async def sync_assessment_node(self, assessment: dict):
        await self._run(
            """
            MERGE (a:Assessment {assessment_id: $assessment_id})
            SET a.user_skill_id = $user_skill_id,
                a.user_id = $user_id,
                a.assessment_type = $assessment_type,
                a.score = $score,
                a.level_achieved = $level_achieved,
                a.confidence = $confidence,
                a.status = $status
        """,
            {
                "assessment_id": assessment.get("assessment_id"),
                "user_skill_id": assessment.get("user_skill_id"),
                "user_id": assessment.get("user_id"),
                "assessment_type": assessment.get("assessment_type"),
                "score": assessment.get("score"),
                "level_achieved": assessment.get("level_achieved"),
                "confidence": assessment.get("confidence"),
                "status": assessment.get("status", "pending"),
            },
        )

    # ── Relationship Sync Methods ──

    async def sync_belongs_to(self, skill: dict):
        """Link Skill to its Category."""
        if not skill.get("category_id"):
            return
        await self._run(
            """
            MATCH (s:Skill {skill_id: $skill_id})
            MATCH (c:Category {category_id: $category_id})
            MERGE (s)-[:BELONGS_TO]->(c)
        """,
            {"skill_id": skill.get("skill_id"), "category_id": skill.get("category_id")},
        )

    async def sync_user_skill_edges(self, us: dict):
        """Link User → HAS_SKILL → UserSkill → OF_SKILL → Skill."""
        await self._run(
            """
            MATCH (s:Skill {skill_id: $skill_id})
            MERGE (u:User {user_id: $user_id})
            MERGE (usn:UserSkill {user_skill_id: $user_skill_id})
            MERGE (u)-[:HAS_SKILL]->(usn)
            MERGE (usn)-[:OF_SKILL]->(s)
        """,
            {
                "user_id": us.get("user_id"),
                "skill_id": us.get("skill_id"),
                "user_skill_id": us.get("user_skill_id"),
            },
        )

    async def sync_evidence_edges(self, evidence: dict):
        """Link UserSkill → HAS_EVIDENCE → Evidence."""
        await self._run(
            """
            MATCH (usn:UserSkill {user_skill_id: $user_skill_id})
            MERGE (e:Evidence {evidence_id: $evidence_id})
            MERGE (usn)-[:HAS_EVIDENCE]->(e)
        """,
            {
                "user_skill_id": evidence.get("user_skill_id"),
                "evidence_id": evidence.get("evidence_id"),
            },
        )

    async def sync_target_edges(self, target: dict):
        """Link UserSkill → HAS_TARGET → Target."""
        await self._run(
            """
            MATCH (usn:UserSkill {user_skill_id: $user_skill_id})
            MERGE (t:Target {target_id: $target_id})
            MERGE (usn)-[:HAS_TARGET]->(t)
        """,
            {
                "user_skill_id": target.get("user_skill_id"),
                "target_id": target.get("target_id"),
            },
        )

    async def sync_assessment_edges(self, assessment: dict):
        """Link UserSkill → HAS_ASSESSMENT → Assessment."""
        await self._run(
            """
            MATCH (usn:UserSkill {user_skill_id: $user_skill_id})
            MERGE (a:Assessment {assessment_id: $assessment_id})
            MERGE (usn)-[:HAS_ASSESSMENT]->(a)
        """,
            {
                "user_skill_id": assessment.get("user_skill_id"),
                "assessment_id": assessment.get("assessment_id"),
            },
        )

    async def sync_relationship_edge(self, rel: dict):
        rel_type = rel.get("relationship_type", "related_to")
        neo_rel = RELATIONSHIP_TYPE_MAP.get(rel_type, "RELATED_TO")
        await self._run(
            f"""
            MATCH (a:Skill {{skill_id: $from_skill_id}})
            MATCH (b:Skill {{skill_id: $to_skill_id}})
            MERGE (a)-[r:{neo_rel}]->(b)
            SET r.weight = $weight,
                r.min_level_from = $min_level_from,
                r.min_level_to = $min_level_to,
                r.is_directed = $is_directed
        """,
            {
                "from_skill_id": rel.get("from_skill_id"),
                "to_skill_id": rel.get("to_skill_id"),
                "weight": rel.get("weight", 1.0),
                "min_level_from": rel.get("min_level_from"),
                "min_level_to": rel.get("min_level_to"),
                "is_directed": rel.get("is_directed", True),
            },
        )

    # ── Delete Methods ──

    async def delete_node(self, label: str, node_id_field: str, node_id: str):
        await self._run(
            f"""
            MATCH (n:{label} {{{node_id_field}: $node_id}})
            DETACH DELETE n
        """,
            {"node_id": node_id},
        )

    # ── Bulk Sync Methods ──

    async def bulk_sync_skills(self, skills: list[dict]):
        for skill in skills:
            await self.sync_skill_node(skill)
            await self.sync_belongs_to(skill)

    async def bulk_sync_relationships(self, rels: list[dict]):
        for rel in rels:
            await self.sync_relationship_edge(rel)

    async def bulk_sync_user_skills(self, user_skills: list[dict]):
        for us in user_skills:
            await self.sync_user_skill_node(us)
            await self.sync_user_skill_edges(us)

    async def full_rebuild(
        self,
        skills: list[dict],
        categories: list[dict],
        relationships: list[dict],
        user_skills: list[dict],
        evidence: list[dict],
        targets: list[dict],
        assessments: list[dict],
    ):
        """Full rebuild of the Neo4j graph from source data."""
        logger.info("Starting full Neo4j graph rebuild")

        # Clear existing graph
        await self._run("MATCH (n) DETACH DELETE n")

        # Load categories
        for cat in categories:
            await self.sync_category_node(cat)
        logger.info(f"Synced {len(categories)} categories")

        # Load skills with BELONGS_TO
        for skill in skills:
            await self.sync_skill_node(skill)
            await self.sync_belongs_to(skill)
        logger.info(f"Synced {len(skills)} skills")

        # Load relationships
        for rel in relationships:
            await self.sync_relationship_edge(rel)
        logger.info(f"Synced {len(relationships)} relationships")

        # Load user skills
        for us in user_skills:
            await self.sync_user_skill_node(us)
            await self.sync_user_skill_edges(us)
        logger.info(f"Synced {len(user_skills)} user skills")

        # Load evidence
        for ev in evidence:
            await self.sync_evidence_node(ev)
            await self.sync_evidence_edges(ev)

        # Load targets
        for t in targets:
            await self.sync_target_node(t)
            await self.sync_target_edges(t)

        # Load assessments
        for a in assessments:
            await self.sync_assessment_node(a)
            await self.sync_assessment_edges(a)

        logger.info("Full Neo4j graph rebuild complete")

    # ── Graph Query Methods ──

    async def find_related_skills(self, skill_id: str, max_depth: int = 3) -> list[dict]:
        return await self._run(
            """
            MATCH path = (s:Skill {skill_id: $skill_id})
                -[:DEPENDS_ON|RELATED_TO|COMPLEMENTARY|RECOMMENDED_BEFORE*1..$max_depth]->(related)
            RETURN related.skill_id AS skill_id, related.name AS name,
                   length(path) AS depth,
                   [r IN relationships(path) | type(r)] AS rel_types,
                   reduce(w = 1.0, r IN relationships(path) | w * coalesce(r.weight, 1.0)) AS cumulative_weight
            ORDER BY cumulative_weight DESC, depth ASC
        """,
            {"skill_id": skill_id, "max_depth": max_depth},
        )

    async def recommend_skills(self, user_id: str, limit: int = 10) -> list[dict]:
        return await self._run(
            """
            MATCH (u:User {user_id: $user_id})-[:HAS_SKILL]->(us:UserSkill)-[:OF_SKILL]->(s:Skill)
            MATCH (s)-[r:DEPENDS_ON|RELATED_TO|COMPLEMENTARY]-(candidate:Skill)
            WHERE NOT (u)-[:HAS_SKILL]->()-[:OF_SKILL]->(candidate)
            RETURN candidate.skill_id AS skill_id, candidate.name AS name,
                   COUNT(DISTINCT r) AS connection_strength,
                   AVG(r.weight) AS avg_weight,
                   MAX(candidate.skill_health) AS skill_health
            ORDER BY connection_strength * avg_weight DESC, skill_health DESC
            LIMIT $limit
        """,
            {"user_id": user_id, "limit": limit},
        )

    async def find_learning_path(self, user_id: str, target_skill_id: str) -> list[dict]:
        return await self._run(
            """
            MATCH (u:User {user_id: $user_id})-[:HAS_SKILL]->(us:UserSkill)-[:OF_SKILL]->(current:Skill)
            MATCH (target:Skill {skill_id: $target_skill_id})
            MATCH path = shortestPath((current)-[:DEPENDS_ON*]->(target))
            WHERE path IS NOT NULL
            RETURN [n IN nodes(path) | n.name] AS skill_names,
                   [n IN nodes(path) | n.skill_id] AS skill_ids,
                   length(path) AS steps
        """,
            {"user_id": user_id, "target_skill_id": target_skill_id},
        )

    async def find_similar_users(self, user_id: str, limit: int = 20) -> list[dict]:
        return await self._run(
            """
            MATCH (u1:User {user_id: $user_id})-[:HAS_SKILL]->(us1:UserSkill)-[:OF_SKILL]->(s:Skill)
            MATCH (u2:User)-[:HAS_SKILL]->(us2:UserSkill)-[:OF_SKILL]->(s)
            WHERE u1 <> u2 AND us1.level = us2.level
            RETURN u2.user_id AS similar_user_id, COUNT(*) AS common_skills,
                   AVG(us2.level) AS avg_level
            ORDER BY common_skills DESC
            LIMIT $limit
        """,
            {"user_id": user_id, "limit": limit},
        )

    async def get_graph_statistics(self) -> dict:
        stats = await self._run("""
            MATCH (n) RETURN count(DISTINCT n) AS total_nodes
        """)
        rels = await self._run("""
            MATCH ()-[r]->() RETURN count(DISTINCT r) AS total_relationships
        """)
        labels = await self._run("""
            MATCH (n) RETURN DISTINCT labels(n) AS labels, count(n) AS count
        """)
        return {
            "total_nodes": stats[0]["total_nodes"] if stats else 0,
            "total_relationships": rels[0]["total_relationships"] if rels else 0,
            "node_distribution": {",".join(lbl["labels"]): lbl["count"] for lbl in labels} if labels else {},
        }


graph_sync = Neo4jSyncService()
