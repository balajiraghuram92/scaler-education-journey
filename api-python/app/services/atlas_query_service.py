"""Ported from api/Services/AtlasQueryService.cs."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..models.concept_prerequisite import ConceptPrerequisite
from ..models.concept_relation import ConceptRelation
from ..models.domain_concept_connection import DomainConceptConnection
from ..models.knowledge_concept import KnowledgeConcept
from ..models.knowledge_domain import KnowledgeDomain


class AtlasQueryService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_knowledge_atlas(self) -> dict:
        domains = (
            await self._session.execute(
                select(KnowledgeDomain)
                .options(
                    selectinload(KnowledgeDomain.concept_connections).selectinload(
                        DomainConceptConnection.concept
                    )
                )
                .order_by(KnowledgeDomain.order_index)
            )
        ).scalars().all()

        concepts = (
            await self._session.execute(
                select(KnowledgeConcept)
                .options(
                    selectinload(KnowledgeConcept.domain_connections),
                    selectinload(KnowledgeConcept.prerequisites).selectinload(
                        ConceptPrerequisite.prerequisite_concept
                    ),
                    selectinload(KnowledgeConcept.outgoing_relations).selectinload(
                        ConceptRelation.target_concept
                    ),
                    selectinload(KnowledgeConcept.next_lessons),
                )
                .order_by(KnowledgeConcept.order_index)
            )
        ).scalars().all()

        connections = [
            {
                "from": domain.slug,
                "to": link.concept.slug,
                "relevanceWeight": link.relevance_weight,
                "isPrimary": link.is_primary,
            }
            for domain in domains
            for link in domain.concept_connections
            if link.concept is not None
        ]

        return {
            "domains": [
                {
                    "id": domain.id,
                    "slug": domain.slug,
                    "name": domain.name,
                    "code": domain.code,
                    "description": domain.description,
                    "icon": domain.icon,
                    "colorHex": domain.color_hex,
                    "orderIndex": domain.order_index,
                    "conceptCount": len(domain.concept_connections),
                }
                for domain in domains
            ],
            "concepts": [
                {
                    "id": concept.id,
                    "slug": concept.slug,
                    "title": concept.title,
                    "subLabel": concept.sub_label,
                    "summary": concept.summary,
                    "difficulty": concept.difficulty,
                    "icon": concept.icon,
                    "estimatedHours": concept.estimated_hours,
                    "orderIndex": concept.order_index,
                    "domainIds": [dc.domain_id for dc in concept.domain_connections],
                    "prerequisites": [
                        {
                            "name": p.prerequisite_concept.title
                            if p.prerequisite_concept is not None
                            else "Prerequisite",
                            "prerequisiteConceptId": p.prerequisite_concept_id,
                            "status": p.status,
                        }
                        for p in concept.prerequisites
                    ],
                    "outgoingRelations": [
                        {
                            "targetConceptId": r.target_concept_id,
                            "targetTitle": r.target_concept.title
                            if r.target_concept is not None
                            else "Related Concept",
                            "targetSlug": r.target_concept.slug
                            if r.target_concept is not None
                            else "",
                            "relationshipType": r.relationship_type,
                        }
                        for r in concept.outgoing_relations
                    ],
                    "nextLessons": [
                        {
                            "lessonId": nl.lesson_id,
                            "lessonSlug": nl.lesson_slug,
                            "lessonTitle": nl.lesson_title,
                            "moduleName": nl.module_name,
                        }
                        for nl in sorted(concept.next_lessons, key=lambda x: x.order_index)
                    ],
                }
                for concept in concepts
            ],
            "connections": connections,
        }
