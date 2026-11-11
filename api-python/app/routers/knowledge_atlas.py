"""Ported from api/Program.cs inline routes for /api/knowledge-atlas (lines 1166-1231)."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..db import get_session
from ..models.concept_prerequisite import ConceptPrerequisite
from ..models.concept_relation import ConceptRelation
from ..models.domain_concept_connection import DomainConceptConnection
from ..models.knowledge_concept import KnowledgeConcept
from ..models.knowledge_domain import KnowledgeDomain
from ..schemas.dtos import (
    ConceptPrerequisiteItemDto,
    ConceptSummaryDto,
    DomainSummaryDto,
    KnowledgeAtlasDto,
    KnowledgeConnectionDto,
)

router = APIRouter(tags=["knowledge-atlas"])


@router.get("/api/knowledge-atlas")  # Program.cs line 1166
async def get_knowledge_atlas(session: AsyncSession = Depends(get_session)):
    domains = (
        await session.execute(
            select(KnowledgeDomain).order_by(KnowledgeDomain.order_index)
        )
    ).scalars().all()
    domain_dtos = [
        DomainSummaryDto(
            id=d.id,
            slug=d.slug,
            name=d.name,
            code=d.code,
            description=d.description,
            icon=d.icon,
            color_hex=d.color_hex,
            order_index=d.order_index,
        )
        for d in domains
    ]

    concepts = (
        await session.execute(
            select(KnowledgeConcept)
            .options(
                selectinload(KnowledgeConcept.domain_connections).selectinload(
                    DomainConceptConnection.domain
                ),
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
    concept_dtos = [
        ConceptSummaryDto(
            id=c.id,
            slug=c.slug,
            title=c.title,
            sub_label=c.sub_label,
            summary=c.summary,
            description=c.description,
            difficulty=c.difficulty,
            icon=c.icon,
            estimated_hours=c.estimated_hours,
            order_index=c.order_index,
            connected_domains=[
                dc.domain.slug
                for dc in c.domain_connections
                if dc.domain is not None and dc.domain.slug
            ],
            prerequisites=[
                ConceptPrerequisiteItemDto(
                    name=p.prerequisite_concept.title
                    if p.prerequisite_concept is not None
                    else "Prerequisite",
                    status=p.status,
                )
                for p in c.prerequisites
            ],
            related_lessons=[
                r.target_concept.title if r.target_concept is not None else "Related Concept"
                for r in c.outgoing_relations
            ],
            next_lessons=[
                nl.lesson_title
                for nl in sorted(c.next_lessons, key=lambda x: x.order_index)
            ],
        )
        for c in concepts
    ]

    connections = (
        await session.execute(
            select(DomainConceptConnection)
            .options(
                selectinload(DomainConceptConnection.domain),
                selectinload(DomainConceptConnection.concept),
            )
            .order_by(DomainConceptConnection.order_index)
        )
    ).scalars().all()
    connection_dtos = [
        KnowledgeConnectionDto(
            **{
                "from": dc.domain.slug,
                "to": dc.concept.slug,
                "relevanceWeight": dc.relevance_weight,
                "isPrimary": dc.is_primary,
            }
        )
        for dc in connections
        if dc.domain is not None and dc.concept is not None
    ]

    return KnowledgeAtlasDto(
        domains=domain_dtos, concepts=concept_dtos, connections=connection_dtos
    )
