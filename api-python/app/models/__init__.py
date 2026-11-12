"""All ported entities. Importing this package registers every model on Base.metadata."""

from .app_user import AppUser
from .base import Base
from .chat_conversation import ChatConversation
from .chat_message import ChatMessage
from .concept_next_lesson import ConceptNextLesson
from .concept_prerequisite import ConceptPrerequisite
from .concept_relation import ConceptRelation
from .course import Course
from .course_domain_link import CourseDomainLink
from .course_module import CourseModule
from .domain_concept_connection import DomainConceptConnection
from .knowledge_concept import KnowledgeConcept
from .knowledge_domain import KnowledgeDomain
from .knowledge_thread import KnowledgeThread
from .knowledge_thread_step import KnowledgeThreadStep
from .learning_activity import LearningActivity
from .lesson import Lesson
from .lesson_code_comparison import LessonCodeComparison
from .lesson_concept_link import LessonConceptLink
from .lesson_diagram import LessonDiagram
from .lesson_note import LessonNote
from .lesson_relation import LessonRelation
from .lesson_resource import LessonResource
from .localization import (
    BuildSnapshot,
    BuildSnapshotLocaleCount,
    EvalCaseResult,
    EvalGoldenCase,
    EvalRun,
    GlossaryTerm,
    LedgerEntry,
    LocalizationLocale,
    LocalizationProject,
    LocalizationProviderRate,
    LocalizationString,
    LocalizationTranslation,
    LocalizationUsageCap,
    LocalizationUsageEvent,
    ProviderHealthSnapshot,
    ServiceAgreement,
    TeamAssignment,
    TranslationCacheEntry,
    TranslationJob,
    Vendor,
    WorkflowStep,
)
from .mcq_attempt import McqAttempt
from .mcq_option import McqOption
from .mcq_presentation import McqPresentation
from .mcq_question import McqQuestion
from .mfa_challenge import MfaChallenge
from .migration_reconciliation import MigrationReconciliation
from .problem import Problem
from .reading_activity_log import ReadingActivityLog
from .reading_map_item import ReadingMapItem
from .study_task import StudyTask
from .study_task_content_link import StudyTaskContentLink
from .study_vertical import StudyVertical
from .user_exercise_state import UserExerciseAttempt, UserExerciseDraft
from .user_lesson_progress import UserLessonProgress
from .user_problem_progress import UserProblemProgress
from .user_session import UserSession

__all__ = [
    "AppUser",
    "Base",
    "BuildSnapshot",
    "BuildSnapshotLocaleCount",
    "ChatConversation",
    "ChatMessage",
    "ConceptNextLesson",
    "ConceptPrerequisite",
    "ConceptRelation",
    "Course",
    "CourseDomainLink",
    "CourseModule",
    "DomainConceptConnection",
    "EvalCaseResult",
    "EvalGoldenCase",
    "EvalRun",
    "GlossaryTerm",
    "KnowledgeConcept",
    "KnowledgeDomain",
    "KnowledgeThread",
    "KnowledgeThreadStep",
    "LearningActivity",
    "LedgerEntry",
    "Lesson",
    "LessonCodeComparison",
    "LessonConceptLink",
    "LessonDiagram",
    "LessonNote",
    "LessonRelation",
    "LessonResource",
    "LocalizationLocale",
    "LocalizationProject",
    "LocalizationProviderRate",
    "LocalizationString",
    "LocalizationTranslation",
    "LocalizationUsageCap",
    "LocalizationUsageEvent",
    "McqAttempt",
    "McqOption",
    "McqPresentation",
    "McqQuestion",
    "MfaChallenge",
    "MigrationReconciliation",
    "Problem",
    "ProviderHealthSnapshot",
    "ReadingActivityLog",
    "ReadingMapItem",
    "ServiceAgreement",
    "StudyTask",
    "StudyTaskContentLink",
    "StudyVertical",
    "TeamAssignment",
    "TranslationCacheEntry",
    "TranslationJob",
    "UserExerciseAttempt",
    "UserExerciseDraft",
    "UserLessonProgress",
    "UserProblemProgress",
    "UserSession",
    "Vendor",
    "WorkflowStep",
]
