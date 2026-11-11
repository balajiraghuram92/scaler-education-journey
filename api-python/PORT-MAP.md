# PORT-MAP — C# file to Python module map

One section per phase; parallel phases edit different sections. Status values:
`done`, `done (unverified)` (ported, but no check has been executed against it yet),
`partial` (with reason), `blocked` (with reason), `todo`.

Round 1 corrections: nothing has been installed, imported or run yet, so every
ported row below is `done (unverified)`, not `done`.

## P0 — Scaffold, configuration, parity tooling

### Files

| C# path | Python path | Status | Notes |
|---|---|---|---|
| api/Program.cs (middleware, health, router registration, DI) | api-python/app/main.py, app/settings.py, app/db.py, app/errors.py, app/cli.py (placeholder), app/routers/* (empty) | done (unverified) | Inline routes belong to P3, CLI modes to P7 |
| api/Options/AuthOptions.cs | api-python/app/settings.py (AuthSettings) | done (unverified) | |
| api/Options/BudgetOptions.cs | api-python/app/settings.py (BudgetSettings) | done (unverified) | Used by P5 |
| api/Options/EmailOptions.cs | api-python/app/settings.py (EmailSettings) | done (unverified) | Used by P2 |
| api/Options/ExerciseExecutionOptions.cs | api-python/app/settings.py (ExerciseExecutionSettings) | done (unverified) | Used by P4 |
| api/Options/GoogleTranslateOptions.cs | api-python/app/settings.py (GoogleTranslateSettings) | done (unverified) | Used by P6 |
| api/Options/JwtOptions.cs | api-python/app/settings.py (JwtSettings) | done (unverified) | Legacy aliases |
| api/Options/LlamaApiOptions.cs | api-python/app/settings.py (LlamaApiSettings) | done (unverified) | Used by P5 |
| api/Options/SmtpOptions.cs | api-python/app/settings.py (SmtpSettings) | done (unverified) | Used by P2; User/Pass aliases handled |

### Routes

| Method | Path | C# handler | Auth | Status | Notes |
|---|---|---|---|---|---|
| GET | /health/live | Program.cs HealthLiveCheck | no | done (unverified) | |
| GET | /health/ready | Program.cs HealthReadyCheck | no | done (unverified) | Pending-migration detail simplified, see Findings |
| GET | /health | Program.cs HealthCheck | no | done (unverified) | |
| GET | / | Program.cs root | no | done (unverified) | |

## P1 — Entities

### Files

| C# path | Python path | Status | Notes |
|---|---|---|---|
| api/Data/StudyTrackerContext.cs | api-python/app/models/__init__.py + per-entity modules (Fluent config folded into models) | done (unverified) | Fluent wins over attributes |
| api/Models/AppUser.cs | api-python/app/models/app_user.py | done (unverified) | |
| api/Models/ChatConversation.cs | api-python/app/models/chat_conversation.py | done (unverified) | |
| api/Models/ChatMessage.cs | api-python/app/models/chat_message.py | done (unverified) | |
| api/Models/ConceptNextLesson.cs | api-python/app/models/concept_next_lesson.py | done (unverified) | |
| api/Models/ConceptPrerequisite.cs | api-python/app/models/concept_prerequisite.py | done (unverified) | |
| api/Models/ConceptRelation.cs | api-python/app/models/concept_relation.py | done (unverified) | |
| api/Models/Course.cs | api-python/app/models/course.py | done (unverified) | |
| api/Models/CourseDomainLink.cs | api-python/app/models/course_domain_link.py | done (unverified) | |
| api/Models/CourseModule.cs | api-python/app/models/course_module.py | done (unverified) | |
| api/Models/DomainConceptConnection.cs | api-python/app/models/domain_concept_connection.py | done (unverified) | |
| api/Models/KnowledgeConcept.cs | api-python/app/models/knowledge_concept.py | done (unverified) | |
| api/Models/KnowledgeDomain.cs | api-python/app/models/knowledge_domain.py | done (unverified) | |
| api/Models/KnowledgeThread.cs | api-python/app/models/knowledge_thread.py | done (unverified) | |
| api/Models/KnowledgeThreadStep.cs | api-python/app/models/knowledge_thread_step.py | done (unverified) | |
| api/Models/LearningActivity.cs | api-python/app/models/learning_activity.py | done (unverified) | |
| api/Models/Lesson.cs | api-python/app/models/lesson.py | done (unverified) | |
| api/Models/LessonCodeComparison.cs | api-python/app/models/lesson_code_comparison.py | done (unverified) | |
| api/Models/LessonConceptLink.cs | api-python/app/models/lesson_concept_link.py | done (unverified) | |
| api/Models/LessonDiagram.cs | api-python/app/models/lesson_diagram.py | done (unverified) | |
| api/Models/LessonNote.cs | api-python/app/models/lesson_note.py | done (unverified) | |
| api/Models/LessonRelation.cs | api-python/app/models/lesson_relation.py | done (unverified) | |
| api/Models/LessonResource.cs | api-python/app/models/lesson_resource.py | done (unverified) | |
| api/Models/McqAttempt.cs | api-python/app/models/mcq_attempt.py | done (unverified) | |
| api/Models/McqOption.cs | api-python/app/models/mcq_option.py | done (unverified) | |
| api/Models/McqPresentation.cs | api-python/app/models/mcq_presentation.py | done (unverified) | |
| api/Models/McqQuestion.cs | api-python/app/models/mcq_question.py | done (unverified) | |
| api/Models/MfaChallenge.cs | api-python/app/models/mfa_challenge.py | done (unverified) | |
| api/Models/MigrationReconciliation.cs | api-python/app/models/migration_reconciliation.py | done (unverified) | |
| api/Models/Problem.cs | api-python/app/models/problem.py | done (unverified) | |
| api/Models/ReadingActivityLog.cs | api-python/app/models/reading_activity_log.py | done (unverified) | |
| api/Models/ReadingMapItem.cs | api-python/app/models/reading_map_item.py | done (unverified) | |
| api/Models/StudyTask.cs | api-python/app/models/study_task.py | done (unverified) | |
| api/Models/StudyTaskContentLink.cs | api-python/app/models/study_task_content_link.py | done (unverified) | |
| api/Models/StudyVertical.cs | api-python/app/models/study_vertical.py | done (unverified) | |
| api/Models/UserExerciseState.cs | api-python/app/models/user_exercise_state.py | done (unverified) | Two classes (Draft, Attempt) in one module, as in C# |
| api/Models/UserLessonProgress.cs | api-python/app/models/user_lesson_progress.py | done (unverified) | |
| api/Models/UserProblemProgress.cs | api-python/app/models/user_problem_progress.py | done (unverified) | |
| api/Models/UserSession.cs | api-python/app/models/user_session.py | done (unverified) | |
| api/Models/Localization/BuildSnapshot.cs | api-python/app/models/localization/build_snapshot.py | done (unverified) | |
| api/Models/Localization/BuildSnapshotLocaleCount.cs | api-python/app/models/localization/build_snapshot_locale_count.py | done (unverified) | |
| api/Models/Localization/EvalCaseResult.cs | api-python/app/models/localization/eval_case_result.py | done (unverified) | No migration for this table yet (Finding 2) |
| api/Models/Localization/EvalGoldenCase.cs | api-python/app/models/localization/eval_golden_case.py | done (unverified) | No migration for this table yet (Finding 2) |
| api/Models/Localization/EvalRun.cs | api-python/app/models/localization/eval_run.py | done (unverified) | No migration for this table yet (Finding 2) |
| api/Models/Localization/GlossaryTerm.cs | api-python/app/models/localization/glossary_term.py | done (unverified) | No migration for this table yet (Finding 2) |
| api/Models/Localization/LedgerEntry.cs | api-python/app/models/localization/ledger_entry.py | done (unverified) | |
| api/Models/Localization/LocalizationLocale.cs | api-python/app/models/localization/localization_locale.py | done (unverified) | |
| api/Models/Localization/LocalizationProject.cs | api-python/app/models/localization/localization_project.py | done (unverified) | |
| api/Models/Localization/LocalizationString.cs | api-python/app/models/localization/localization_string.py | done (unverified) | |
| api/Models/Localization/LocalizationTranslation.cs | api-python/app/models/localization/localization_translation.py | done (unverified) | 3 columns ahead of migrations (Finding 3) |
| api/Models/Localization/MarketplaceBid.cs | api-python/app/models/localization/marketplace_bid.py | done (unverified) | |
| api/Models/Localization/MarketplaceJob.cs | api-python/app/models/localization/marketplace_job.py | done (unverified) | |
| api/Models/Localization/ProviderHealthSnapshot.cs | api-python/app/models/localization/provider_health_snapshot.py | done (unverified) | |
| api/Models/Localization/TranslationCacheEntry.cs | api-python/app/models/localization/translation_cache_entry.py | done (unverified) | No migration for this table yet (Finding 2) |
| api/Models/Localization/Vendor.cs | api-python/app/models/localization/vendor.py | done (unverified) | |
| api/Models/Localization/WorkflowStep.cs | api-python/app/models/localization/workflow_step.py | done (unverified) | |

### Routes

No routes in this phase (entities only).

## P2 — Authentication, sessions, users

### Files

| C# path | Python path | Status | Notes |
|---|---|---|---|
| api/Services/Auth/CurrentUser.cs | api-python/app/services/auth/current_user.py | done (unverified) | Real JWT auth wired into main.py |
| api/Services/Auth/IJwtTokenService.cs | api-python/app/services/auth/i_jwt_token_service.py | done (unverified) | Interface → Protocol |
| api/Services/Auth/IPasswordHasher.cs | api-python/app/services/auth/i_password_hasher.py | done (unverified) | Interface → Protocol; out-params → tuple |
| api/Services/Auth/JwtTokenService.cs | api-python/app/services/auth/jwt_token_service.py | done (unverified) | Claim layout per Finding 4 |
| api/Services/Auth/Pbkdf2PasswordHasher.cs | api-python/app/services/auth/pbkdf2_password_hasher.py | done (unverified) | |
| api/Services/Auth/SessionService.cs | api-python/app/services/auth/session_service.py | done (unverified) | IMemoryCache → module dict with TTL |
| api/Services/Auth/TotpSecretProtector.cs | api-python/app/services/auth/totp_secret_protector.py | done (unverified) | |
| api/Services/Auth/TotpService.cs | api-python/app/services/auth/totp_service.py | done (unverified) | Interface + impl in one module, as in C# |
| api/Services/Email/IEmailNotificationService.cs | api-python/app/services/email/i_email_notification_service.py | done (unverified) | Interface → Protocol |
| api/Services/Email/SmtpEmailNotificationService.cs | api-python/app/services/email/smtp_email_notification_service.py | done (unverified) | SmtpClient → aiosmtplib |
| api/Endpoints/AuthEndpoints.cs | api-python/app/routers/auth_endpoints.py | done (unverified) | Fire-and-forget mail → BackgroundTasks |
| api/Endpoints/MeEndpoints.cs | api-python/app/routers/me_endpoints.py | done (unverified) | Uses LearnerProgressService (P3, this track) |
| api/Endpoints/AdminEndpoints.cs | api-python/app/routers/admin_endpoints.py | done (unverified) | usage/today uses BudgetGuardService (P5, this track) |
| api/Models/AuthDtos.cs | api-python/app/schemas/auth_dtos.py | done (unverified) | |

### Routes

| Method | Path | C# handler | Auth | Status | Notes |
|---|---|---|---|---|---|
| POST | /api/auth/signup | AuthSignup | no (AuthPolicy) | done (unverified) | |
| POST | /api/auth/login | AuthLogin | no (AuthPolicy) | done (unverified) | |
| POST | /api/auth/totp/enroll/start | AuthTotpEnrollStart | challenge | done (unverified) | |
| POST | /api/auth/totp/enroll/confirm | AuthTotpEnrollConfirm | no (AuthPolicy) | done (unverified) | |
| POST | /api/auth/totp/verify | AuthTotpVerify | no (AuthPolicy) | done (unverified) | |
| POST | /api/auth/logout | AuthLogout | cookie | done (unverified) | |
| GET | /api/auth/me | AuthGetCurrentUser | cookie | done (unverified) | |
| POST | /api/auth/refresh | AuthRefresh | refresh cookie (RefreshPolicy) | done (unverified) | |
| GET | /api/auth/sessions | AuthListSessions | yes | done (unverified) | |
| DELETE | /api/auth/sessions/{sessionId} | AuthRevokeSession | yes | done (unverified) | |
| POST | /api/auth/logout-all | AuthLogoutAll | yes | done (unverified) | |
| GET | /api/me/summary | MeSummary | yes | done (unverified) | |
| GET | /api/me/resume | MeResume | yes | done (unverified) | |
| GET | /api/me/lessons/progress | MeLessonProgressList | yes | done (unverified) | |
| POST | /api/me/lessons/{lessonId}/visit | MeRecordLessonVisit | yes | done (unverified) | |
| PUT | /api/me/lessons/{lessonId}/position | MeUpdateLessonPosition | yes | done (unverified) | |
| PUT | /api/me/lessons/{lessonId}/completion | MeSetLessonCompletion | yes | done (unverified) | |
| PUT | /api/me/problems/{problemId}/status | MeSetProblemStatus | yes | done (unverified) | |
| GET | /api/me/mcq-performance | MeMcqPerformance | yes | done (unverified) | |
| GET | /api/me/activity | MeActivity | yes | done (unverified) | |
| GET | /api/admin/users | AdminGetUsers | AdminOnly | done (unverified) | |
| POST | /api/admin/users/{id}/approve | AdminApproveUser | AdminOnly | done (unverified) | |
| POST | /api/admin/users/{id}/reject | AdminRejectUser | AdminOnly | done (unverified) | |
| POST | /api/admin/users/{id}/reset-totp | AdminResetTotp | AdminOnly | done (unverified) | |
| GET | /api/admin/usage/today | AdminGetUsageToday | AdminOnly | done (unverified) | Needs P5 BudgetGuardService at runtime |
| GET | /api/admin/usage/by-user | AdminGetUsageByUser | AdminOnly | done (unverified) | |

## P3 — Curriculum, progress, atlas, MCQs

### Files

| C# path | Python path | Status | Notes |
|---|---|---|---|
| api/Program.cs (inline routes lines 679-1631) | api-python/app/routers/verticals.py, tasks.py, courses.py, lessons.py, problems.py, knowledge_atlas.py, reading_map.py, chapters.py | done (unverified) | Each handler carries Program.cs line number |
| api/Endpoints/V2Endpoints.cs | api-python/app/routers/v2_endpoints.py | done (unverified) | Request records live here, as in C# |
| api/Models/DTOs.cs | api-python/app/schemas/dtos.py | done (unverified) | Class order changed for forward refs |
| api/Services/ProgressService.cs | api-python/app/services/progress_service.py | done (unverified) | Services flush; routers commit |
| api/Services/LearnerProgressService.cs | api-python/app/services/learner_progress_service.py | done (unverified) | Also serves P2 Me routes |
| api/Services/LearningPathQueryService.cs | api-python/app/services/learning_path_query_service.py | done (unverified) | GetAll conceptSlugs quirk kept (Finding 6) |
| api/Services/AtlasQueryService.cs | api-python/app/services/atlas_query_service.py | done (unverified) | Anonymous objects → dicts |
| api/Services/ReadingMapService.cs | api-python/app/services/reading_map_service.py | done (unverified) | Anonymous objects → dicts |
| api/Services/McqService.cs | api-python/app/services/mcq_service.py | done (unverified) | KeyNotFound→KeyError, Argument→ValueError |

### Routes

| Method | Path | C# handler | Auth | Status | Notes |
|---|---|---|---|---|---|
| GET | /api/verticals | GetVerticals | api-key | done (unverified) | |
| GET | /api/verticals/{id} | GetVerticalById | api-key | done (unverified) | |
| POST | /api/verticals | CreateVertical | api-key | done (unverified) | |
| POST | /api/verticals/ingest | IngestVerticalMarkdown | api-key | done (unverified) | |
| PUT | /api/tasks/{id}/toggle | ToggleTask | api-key | done (unverified) | |
| GET | /api/courses | GetCourses | api-key | done (unverified) | |
| GET | /api/courses/{slugOrId} | GetCourseBySlugOrId | api-key | done (unverified) | |
| GET | /api/lessons/{id} | GetLessonById | api-key | done (unverified) | |
| POST | /api/lessons | CreateLesson | api-key | done (unverified) | |
| PUT | /api/lessons/{id} | UpdateLesson | api-key | done (unverified) | |
| PATCH | /api/lessons/{id}/progress | ToggleLessonProgress | yes | done (unverified) | |
| GET | /api/problems/{id} | GetProblemById | api-key | done (unverified) | |
| POST | /api/problems | CreateProblem | api-key | done (unverified) | |
| PATCH | /api/problems/{id}/progress | ToggleProblemProgress | yes | done (unverified) | |
| GET | /api/knowledge-atlas | GetKnowledgeAtlas | api-key | done (unverified) | |
| GET | /api/reading-map | GetReadingMap | api-key | done (unverified) | |
| PATCH | /api/reading-map/items/{id}/toggle | ToggleReadingMapItem | api-key | done (unverified) | |
| POST | /api/reading-map/items | CreateReadingMapItem | api-key | done (unverified) | |
| GET | /api/chapters | GetChaptersList | api-key | done (unverified) | |
| GET | /api/chapters/{slug} | GetChapterBySlug | api-key | done (unverified) | |
| GET | /api/chapters/{v}/{m}/{l} | GetChapterByPath | api-key | done (unverified) | |
| POST | /api/chapters/{id}/notes | CreateChapterNote | conditional | done (unverified) | |
| POST | /api/chapters/map | MapCurriculumChapter | api-key | done (unverified) | |
| GET | /api/v2/learning-paths | V2GetLearningPaths | api-key | done (unverified) | |
| GET | /api/v2/learning-paths/{slug} | V2GetLearningPathBySlug | api-key | done (unverified) | |
| GET | /api/v2/knowledge-atlas | V2GetKnowledgeAtlas | api-key | done (unverified) | |
| GET | /api/v2/reading-map | V2GetReadingMap | api-key | done (unverified) | |
| GET | /api/v2/chapters/{c}/{m}/{l} | V2 chapter reader | api-key | done (unverified) | Needs P4 exercise repository at runtime |
| POST | /api/v2/progress/lesson | V2SetLessonProgress | yes | done (unverified) | Table said api-key; C# has RequireAuthorization |
| POST | /api/v2/progress/problem | V2 problem progress | yes | done (unverified) | Table said api-key; C# has RequireAuthorization |
| POST | /api/v2/progress/task | V2 task progress | yes | done (unverified) | Table said api-key; C# has RequireAuthorization |
| GET | /api/v2/practice-questions/{c}/{m}/{l} | V2 practice questions | api-key | done (unverified) | |
| POST | /api/v2/practice-questions/{id}/attempts | V2 record attempt | api-key | done (unverified) | |
| POST | /api/v2/practice-questions/{id}/retry | V2 retry | api-key | done (unverified) | |

## P4 — Exercise runner

### Files

| C# path | Python path | Status | Notes |
|---|---|---|---|
| api/Services/Exercises/ExerciseExecutionClassifier.cs | api-python/app/services/exercises/exercise_execution_classifier.py | done (unverified) | |
| api/Services/Exercises/ExerciseExecutionExceptions.cs | api-python/app/services/exercises/exercise_execution_exceptions.py | done (unverified) | |
| api/Services/Exercises/ExerciseExecutionModels.cs | api-python/app/services/exercises/exercise_execution_models.py | done (unverified) | Classes → dataclasses |
| api/Services/Exercises/ExerciseManifestModels.cs | api-python/app/services/exercises/exercise_manifest_models.py | done (unverified) | + case-insensitive JSON parsing |
| api/Services/Exercises/ExerciseMetadataService.cs | api-python/app/services/exercises/exercise_metadata_service.py | done (unverified) | |
| api/Services/Exercises/ExerciseProgressService.cs | api-python/app/services/exercises/exercise_progress_service.py | done (unverified) | Records → CamelModels in module |
| api/Services/Exercises/ExerciseRepository.cs | api-python/app/services/exercises/exercise_repository.py | done (unverified) | + get_exercise_repository() singleton (V2 uses it) |
| api/Services/Exercises/ExerciseService.cs | api-python/app/services/exercises/exercise_service.py | done (unverified) | SemaphoreSlim → shared asyncio.Semaphore |
| api/Services/Exercises/ExerciseSolutionService.cs | api-python/app/services/exercises/exercise_solution_service.py | done (unverified) | |
| api/Services/Exercises/ExerciseSubmissionValidator.cs | api-python/app/services/exercises/exercise_submission_validator.py | done (unverified) | |
| api/Services/Exercises/ExerciseWorkspaceBuilder.cs | api-python/app/services/exercises/exercise_workspace_builder.py | done (unverified) | |
| api/Services/Exercises/IExerciseRepository.cs | api-python/app/services/exercises/i_exercise_repository.py | done (unverified) | Interface → Protocol |
| api/Services/Exercises/IExerciseRunner.cs | api-python/app/services/exercises/i_exercise_runner.py | done (unverified) | Interface → Protocol |
| api/Services/Exercises/LocalDockerExerciseRunner.cs | api-python/app/services/exercises/local_docker_exercise_runner.py | done (unverified) | Docker.DotNet → docker-py; flags in module ledger |
| api/Services/Exercises/SurefireResultParser.cs | api-python/app/services/exercises/surefire_result_parser.py | done (unverified) | XDocument → ElementTree + DTD/size guards |
| api/Endpoints/ExerciseEndpoints.cs | api-python/app/routers/exercise_endpoints.py | done (unverified) | ValidationProblem shape reproduced |
| api/Models/ExerciseDtos.cs | api-python/app/schemas/exercise_dtos.py | done (unverified) | |
| api/Models/ExerciseMetadataDtos.cs | api-python/app/schemas/exercise_metadata_dtos.py | done (unverified) | |

### Routes

| Method | Path | C# handler | Auth | Status | Notes |
|---|---|---|---|---|---|
| GET | /api/exercises/{exerciseId} | GetExerciseMetadata | api-key | done (unverified) | |
| GET | /api/exercises/{exerciseId}/solution | GetExerciseSolution | api-key | done (unverified) | |
| POST | /api/exercises/{exerciseId}/run | RunExercise | api-key | done (unverified) | |
| POST | /api/exercises/{exerciseId}/check | CheckExercise | api-key | done (unverified) | |
| GET | /api/exercises/{exerciseId}/workspace | GetExerciseWorkspaceState | yes | done (unverified) | |
| PUT | /api/exercises/{exerciseId}/draft | SaveExerciseDraft | yes | done (unverified) | |

## P5 — Chat, LLM client, budget guard, import

### Files

| C# path | Python path | Status | Notes |
|---|---|---|---|
| api/Services/LlamaApiClient.cs | api-python/app/services/llama_api_client.py | done (unverified) | HttpClient → httpx; no retry/streaming in C# either |
| api/Services/BudgetGuardService.cs | api-python/app/services/budget_guard_service.py | done (unverified) | |
| api/Services/CurriculumImportService.cs | api-python/app/services/curriculum_import_service.py | done (unverified) | Uses P7 NormalizationHelper.generate_slug |
| api/Endpoints/ChatEndpoints.cs | api-python/app/routers/chat_endpoints.py | done (unverified) | Prompt strings verbatim |
| api/Endpoints/ImportEndpoints.cs | api-python/app/routers/import_endpoints.py | done (unverified) | |
| api/Models/ChatDtos.cs | api-python/app/schemas/chat_dtos.py | done (unverified) | Also serves P2 admin usage/by-user |

### Routes

| Method | Path | C# handler | Auth | Status | Notes |
|---|---|---|---|---|---|
| POST | /api/chat/conversations | ChatCreateConversation | yes | done (unverified) | |
| POST | /api/chat/conversations/{id}/messages | ChatSendMessage | yes | done (unverified) | |
| GET | /api/chat/conversations/{id}/messages | ChatGetMessages | yes | done (unverified) | |
| POST | /api/v2/curriculum/import | V2ImportChapter | api-key | done (unverified) | |

## P6 — Localization Lab

### Files

| C# path | Python path | Status | Notes |
|---|---|---|---|
| api/Services/Localization/AutoRoutingService.cs | api-python/app/services/localization/auto_routing_service.py | done (unverified) | Post-LA4 thin AI client |
| api/Services/Localization/CreditLedgerService.cs | api-python/app/services/localization/credit_ledger_service.py | done (unverified) | |
| api/Services/Localization/GoogleTranslateProviderService.cs | api-python/app/services/localization/google_translate_provider_service.py | done (unverified) | HttpClient → httpx; mock shape per Finding 19 |
| api/Services/Localization/IQualityScorer.cs | api-python/app/services/localization/i_quality_scorer.py | done (unverified) | Interface → Protocol; record → dataclass |
| api/Services/Localization/ITranslationProvider.cs | api-python/app/services/localization/i_translation_provider.py | done (unverified) | Interface → Protocol |
| api/Services/Localization/LocalizationAiClient.cs | api-python/app/services/localization/localization_ai_client.py | done (unverified) | New in LA4; records → dataclasses |
| api/Services/Localization/LocalizationDtos.cs | api-python/app/schemas/localization_dtos.py | done (unverified) | Lives in Services in C# |
| api/Services/Localization/LocalizationExceptions.cs | api-python/app/services/localization/localization_exceptions.py | done (unverified) | |
| api/Services/Localization/LocalizationProjectService.cs | api-python/app/services/localization/localization_project_service.py | done (unverified) | |
| api/Services/Localization/LocalizationStringService.cs | api-python/app/services/localization/localization_string_service.py | done (unverified) | |
| api/Services/Localization/MarketplaceService.cs | api-python/app/services/localization/marketplace_service.py | done (unverified) | |
| api/Services/Localization/MtOptimizeService.cs | api-python/app/services/localization/mt_optimize_service.py | done (unverified) | Post-LA4 thin AI client incl. OptimizeDetailedAsync |
| api/Services/Localization/ProviderHealthService.cs | api-python/app/services/localization/provider_health_service.py | done (unverified) | |
| api/Services/Localization/QpsScoringService.cs | api-python/app/services/localization/qps_scoring_service.py | done (unverified) | Post-LA4 thin AI client |
| api/Services/Localization/SnapshotService.cs | api-python/app/services/localization/snapshot_service.py | done (unverified) | |
| api/Services/Localization/VendorPortalService.cs | api-python/app/services/localization/vendor_portal_service.py | done (unverified) | |
| api/Services/Localization/WorkflowService.cs | api-python/app/services/localization/workflow_service.py | done (unverified) | Post-LA4 incl. AI actions + ledger writes |
| api/Options/LocalizationAiOptions.cs | api-python/app/settings.py (LocalizationAiSettings) | done (unverified) | New in LA4; was missing from the P0 table |
| api/Endpoints/Localization/LocalizationEndpoints.cs | api-python/app/routers/localization/localization_endpoints.py | done (unverified) | No-slash paths per Finding 24 |
| api/Endpoints/Localization/MarketplaceEndpoints.cs | api-python/app/routers/localization/marketplace_endpoints.py | done (unverified) | |
| api/Endpoints/Localization/ProviderHealthEndpoints.cs | api-python/app/routers/localization/provider_health_endpoints.py | done (unverified) | |
| api/Endpoints/Localization/VendorPortalEndpoints.cs | api-python/app/routers/localization/vendor_portal_endpoints.py | done (unverified) | |

### Routes

| Method | Path | C# handler | Auth | Status | Notes |
|---|---|---|---|---|---|
| GET | /api/localization/projects | GetProjects | api-key | done (unverified) | |
| GET | /api/localization/projects/{slug} | GetProject | api-key | done (unverified) | |
| GET | /api/localization/projects/{slug}/strings | GetStrings | api-key | done (unverified) | |
| PUT | /api/localization/projects/{slug}/strings/{id}/translations/{locale} | UpdateTranslation | api-key | done (unverified) | |
| GET | /api/localization/projects/{slug}/workflow | GetWorkflow | api-key | done (unverified) | |
| POST | /api/localization/projects/{slug}/workflow/steps | AddWorkflowStep | api-key | done (unverified) | |
| PUT | /api/localization/projects/{slug}/workflow/steps/{stepId} | UpdateWorkflowStep | api-key | done (unverified) | |
| POST | /api/localization/projects/{slug}/workflow/steps/{stepId}/reorder | ReorderWorkflowStep | api-key | done (unverified) | |
| POST | /api/localization/projects/{slug}/workflow/steps/{stepId}/run | RunWorkflowStep | api-key | done (unverified) | 501 when AI unconfigured |
| DELETE | /api/localization/projects/{slug}/workflow/steps/{stepId} | DeleteWorkflowStep | api-key | done (unverified) | |
| GET | /api/localization/projects/{slug}/snapshots | GetSnapshots | api-key | done (unverified) | |
| POST | /api/localization/projects/{slug}/snapshots | CutSnapshot | api-key | done (unverified) | |
| GET | /api/localization/projects/{slug}/marketplace | GetOverview | api-key | done (unverified) | |
| POST | /api/localization/projects/{slug}/marketplace/{locale}/post | PostToMarketplace | api-key | done (unverified) | |
| GET | /api/localization/marketplace/jobs/{jobId}/bids | GetBids | api-key | done (unverified) | |
| POST | /api/localization/marketplace/jobs/{jobId}/bids/{bidId}/award | AwardBid | api-key | done (unverified) | |
| POST | /api/localization/marketplace/jobs/{jobId}/approve | ApproveSubmission | api-key | done (unverified) | |
| POST | /api/localization/marketplace/jobs/{jobId}/send-back | SendBackForRevision | api-key | done (unverified) | |
| GET | /api/localization/provider-health | GetHealth | api-key | done (unverified) | |
| POST | /api/localization/provider-health/{provider}/simulate-outage | SimulateOutage | api-key | done (unverified) | |
| POST | /api/localization/provider-health/{provider}/resolve | ResolveOutage | api-key | done (unverified) | |
| GET | /api/localization/vendor/roster | GetRoster | api-key | done (unverified) | |
| GET | /api/localization/vendor/{vendorId}/open-jobs | GetOpenJobs | api-key | done (unverified) | |
| POST | /api/localization/vendor/{vendorId}/jobs/{jobId}/bids | SubmitBid | api-key | done (unverified) | |
| GET | /api/localization/vendor/{vendorId}/awarded-jobs | GetAwardedJobs | api-key | done (unverified) | |
| GET | /api/localization/vendor/jobs/{jobId}/strings | GetJobStrings | api-key | done (unverified) | |
| PUT | /api/localization/vendor/jobs/{jobId}/strings/{stringId} | UpdateJobString | api-key | done (unverified) | |
| POST | /api/localization/vendor/jobs/{jobId}/submit | SubmitJob | api-key | done (unverified) | |

## P7 — Seeders, CLI modes, reconciliation

### Files

| C# path | Python path | Status | Notes |
|---|---|---|---|
| api/Data/DbSeeder.cs | api-python/app/seed/db_seeder.py | done (unverified) | |
| api/Data/ChapterSeedData.cs | api-python/app/seed/chapter_seed_data.py | done (unverified) | Content retyped (CRLF kept) |
| api/Data/ContentCurriculumSeedData.cs | api-python/app/seed/content_curriculum_seed_data.py | done (unverified) | Reads api/Data/Content/* in place |
| api/Data/FdeCurriculumSeedData.cs | api-python/app/seed/fde_curriculum_seed_data.py (+ data JSON via extract_seed_data.py) | done (unverified) | Logic ported; JSON needs converter run |
| api/Data/FdeSeedData.cs | api-python/app/seed/fde_seed_data.py | done (unverified) | |
| api/Data/JavaVerticalSeedData.cs | api-python/app/seed/java_vertical_seed_data.py (+ data JSON via extract_seed_data.py) | done (unverified) | Logic ported; JSON needs converter run |
| api/Data/KnowledgeAtlasSeedData.cs | api-python/app/seed/knowledge_atlas_seed_data.py | done (unverified) | |
| api/Data/LocalizationSeedData.cs | api-python/app/seed/localization_seed_data.py | done (unverified) | Glossary insert kept (no table: Finding 2) |
| api/Data/LocalizationSeedTranslations.cs | api-python/app/seed/localization_seed_translations.py | done (unverified) | |
| api/Data/McqMigrationSeedData.cs | api-python/app/seed/mcq_migration_seed_data.py | done (unverified) | Reads mcq-migration-data.json in place |
| api/Data/PythonCurriculumSeedData.cs | api-python/app/seed/python_curriculum_seed_data.py | done (unverified) | |
| api/Data/ReadingMapSeedData.cs | api-python/app/seed/reading_map_seed_data.py | done (unverified) | |
| api/Program.cs (CLI modes --migrate, --seed-reference-data, --seed-admin, --reconcile-content) | api-python/app/cli.py | done (unverified) | --migrate checks schema via P1 check |
| api/Services/Reconciliation/AtlasReadingReconciler.cs | api-python/app/services/reconciliation/atlas_reading_reconciler.py | done (unverified) | Multi-separator split ported |
| api/Services/Reconciliation/AzureLabsReconciler.cs | api-python/app/services/reconciliation/azure_labs_reconciler.py | done (unverified) | Verified-only apply (Finding 13) |
| api/Services/Reconciliation/FdeReconciler.cs | api-python/app/services/reconciliation/fde_reconciler.py | done (unverified) | Verified-only apply (Finding 13) |
| api/Services/Reconciliation/JavaReconciler.cs | api-python/app/services/reconciliation/java_reconciler.py | done (unverified) | |
| api/Services/Reconciliation/NormalizationHelper.cs | api-python/app/services/reconciliation/normalization_helper.py | done (unverified) | Also used by P5 import service |
| api/Services/Reconciliation/ReconciliationEngine.cs | api-python/app/services/reconciliation/reconciliation_engine.py | done (unverified) | Commits per scope |
| api/Services/Reconciliation/ReconciliationModels.cs | api-python/app/services/reconciliation/reconciliation_models.py | done (unverified) | DetailsJson byte-compatible |

### Routes

No routes in this phase (CLI + seeders only).

## P8 — Full parity sweep and reading guide

Done by agent-2-python-port-b: all 154 file rows and 102 route rows are `done (unverified)`
(5 ignored files carry reasons); `tools/parity_routes.txt` covers every route
(the full parity run itself is NOT RUN — shell unavailable, see PROGRESS.md);
`README.md` is the C#→Python reading guide. Final report in PROGRESS.md.

## Ignored files (not ported)

| C# path | Reason |
|---|---|
| api/Program.cs.orig | Backup copy of Program.cs |
| api/Services/Auth/JwtTokenService.cs.orig | Backup copy |
| api/Services/Auth/TotpSecretProtector.cs.orig | Backup copy |
| api/Services/LlamaApiClient.cs.orig | Backup copy |
| api/Migrations/** | Schema owned by EF Core; Python never migrates |

## Findings

| # | Phase | Description |
|---|---|---|
| 1 | P0 | /health/ready in Python reports applied migration count from __EFMigrationsHistory but cannot list pending migrations (no migration model in Python). Pending list is treated as empty when the DB connects. Parity on the unhealthy/pending shape is not asserted. |
| 2 | P1 | Five C# entities have no EF migration: GlossaryTerm, TranslationCacheEntry, EvalGoldenCase, EvalRun, EvalCaseResult (no CreateTable in api/Migrations/*, absent from StudyTrackerContextModelSnapshot.cs). Ported as-is; schema-parity test excludes them by name. The C# app itself would fail querying these tables. |
| 3 | P1 | LocalizationTranslation declares raw_mt_text, raw_mt_qps_score, comet_kiwi_score but the migration/snapshot (lines 1499-1553) lacks those columns. Ported as-is; schema-parity test excludes them by name. |
| 4 | P2 | Raw JWT claim names (nameid/email/role/unique_name/status/na_sid + nbf/iat/exp/iss/aud) follow JwtSecurityTokenHandler's outbound map; nameid is corroborated by ai-agent/auth.py which reads .NET-issued tokens. The Python validator additionally accepts sub and full ClaimTypes URIs. Confirm against one live .NET token when the shell is available. |
| 5 | P2 | Datetime JSON uses the System.Text.Json shape (...Z, 7-digit fraction when nonzero, implemented in schemas/base.py DotNetDateTime). Postgres timestamptz has microsecond precision; the 7th digit is always 0, matching .NET output for DB-sourced values. |
| 6 | P3 | LearningPathQueryService.GetAllLearningPathsAsync does not Include ConceptLinks, so conceptSlugs is always [] there (BySlug returns real data). Ported as-is. |
| 7 | P3 | ChapterSummaryDto.VerticalSlug receives the vertical NAME in Program.cs (line ~1401: `c.Vertical?.Name`). Ported as-is. |
| 8 | P3 | Malformed bodies (wrong JSON types, empty body where C# would NRE) return FastAPI 422 in Python vs 400/500 in C#. Well-formed and missing-field inputs match (request DTOs default like C# binding). Parity checks use well-formed inputs. |
| 9 | P4 | Length caps (MaxOutputBytes truncation, 4096-char diagnostic cut) count C# UTF-16 code units; the port counts Python code points. Identical for ASCII/BMP output; astral characters differ. |
| 10 | P4 | Junction (non-symlink reparse point) detection on Windows uses GetFileAttributesW in the port; C# uses FileInfo.Attributes. Same outcome; Linux containers only see symlinks. |
| 11 | P5 | Chat system prompt uses \n line endings (StringBuilder.AppendLine on the Linux API container). A Windows-hosted .NET dev server would emit \r\n; parity targets the container. |
| 12 | P5 | Money settings are Decimal in the port (C# decimal); JSON keeps scale (2.00, 6-place costs). |
| 13 | P7 | FDE/Azure reconcilers write MigrationReconciliation.Status = "Proposed" for unmapped tasks, which the ck_migration_reconciliation_status check constraint rejects — so APPLY fails on a real database whenever anything is unmapped (the C# tests only pass because EF InMemory ignores constraints). Ported as-is; a test pins the IntegrityError. |
| 14 | P7 | LocalizationSeedData.SeedGlossaryTerms inserts into localization_glossary_terms, which has no migration (see Finding 2): full seeding fails on a real database in C# too. Ported as-is. |
| 15 | P6 | BUILD-PROMPT §3.3 says a boundary reorder throws InvalidOperationException; C# throws WorkflowStepBoundaryException (400 "Boundary error."). Ported C#. |
| 16 | P6 | BUILD-PROMPT §3.8 says awarded-jobs are Awarded or InProgress; C# also returns NeedsRevision, SubmittedForReview and Approved. Ported C#. |
| 17 | P6 | BUILD-PROMPT §3.8 says submit-for-review with unfilled rows throws InvalidOperationException; C# throws InvalidJobStateException (409). Ported C#. |
| 18 | P6 | BUILD-PROMPT §3.7 says approve advances every translation to Approved; C# advances only rows with non-empty TargetText. Ported C#. |
| 19 | P6 | BUILD-PROMPT §3.6 mock prefix is "[MOCK-DE] "; C# emits "[MOCK-DE-DE] " (full locale upper-cased). Ported C#. |
| 20 | P6 | marketplace-flow §3 shows NeedsRevision going back to InProgress; C# keeps "NeedsRevision" until the vendor edits a string, which flips it to InProgress. Ported C#. |
| 21 | P6 | WorkflowServiceTests.RunStep_Phase3Actions_StillSurfaceNotImplemented encodes pre-LA4 behavior: post-LA4 the AI call happens only per-string, so on a project with no translations the actions return "0 strings …" instead of throwing NotImplementedException. Translated verbatim; fails against post-LA4 code in both stacks (the 501 path is covered by Phase3Actions_NotConfigured_ThrowNotImplemented). |
| 22 | P6 | ArgumentException details embed .NET's Message suffix (" (Parameter 'x')"); the port reproduces those suffixes verbatim in its ValueErrors so problem bodies match. |
| 23 | P6 | The translated RunMtOptimize/ScoreQps/AutoTranslate tests need the pending LA1 migration (glossary table + raw_mt columns, Findings 2-3); they fail on the migrated scratch DB exactly as those paths fail in C# until the reviewer generates it. |
| 24 | P6 | C# group routes registered with "/" (e.g. MapGet("/")) accept the no-trailing-slash form — the shipped frontend calls /api/localization/projects with no slash. Python registers the no-slash form. |
