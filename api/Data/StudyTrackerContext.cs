using Microsoft.EntityFrameworkCore;
using StudyTracker.Api.Models;
using StudyTracker.Api.Models.Localization;

namespace StudyTracker.Api.Data;

public class StudyTrackerContext : DbContext
{
    public StudyTrackerContext(DbContextOptions<StudyTrackerContext> options)
        : base(options)
    {
    }

    public DbSet<StudyVertical> Verticals { get; set; } = null!;
    public DbSet<StudyTask> Tasks { get; set; } = null!;
    public DbSet<Course> Courses { get; set; } = null!;
    public DbSet<CourseModule> Modules { get; set; } = null!;
    public DbSet<Lesson> Lessons { get; set; } = null!;
    public DbSet<Problem> Problems { get; set; } = null!;
    public DbSet<LessonResource> LessonResources { get; set; } = null!;

    // Knowledge Atlas DbSets
    public DbSet<KnowledgeDomain> KnowledgeDomains { get; set; } = null!;
    public DbSet<KnowledgeConcept> KnowledgeConcepts { get; set; } = null!;
    public DbSet<DomainConceptConnection> DomainConceptConnections { get; set; } = null!;
    public DbSet<ConceptPrerequisite> ConceptPrerequisites { get; set; } = null!;
    public DbSet<ConceptRelation> ConceptRelations { get; set; } = null!;
    public DbSet<ConceptNextLesson> ConceptNextLessons { get; set; } = null!;

    // Reading Map DbSets (Panel B: Progress / Reading Map)
    public DbSet<ReadingMapItem> ReadingMapItems { get; set; } = null!;
    public DbSet<ReadingActivityLog> ReadingActivityLogs { get; set; } = null!;
    public DbSet<KnowledgeThread> KnowledgeThreads { get; set; } = null!;

    // Concept Chapter DbSets (Panel D: Concept Chapter Reader)
    public DbSet<LessonCodeComparison> LessonCodeComparisons { get; set; } = null!;
    public DbSet<LessonDiagram> LessonDiagrams { get; set; } = null!;
    public DbSet<LessonNote> LessonNotes { get; set; } = null!;

    // Phase 2 Additive Bridge DbSets
    public DbSet<CourseDomainLink> CourseDomainLinks { get; set; } = null!;
    public DbSet<LessonConceptLink> LessonConceptLinks { get; set; } = null!;
    public DbSet<LessonRelation> LessonRelations { get; set; } = null!;
    public DbSet<StudyTaskContentLink> StudyTaskContentLinks { get; set; } = null!;
    public DbSet<LearningActivity> LearningActivities { get; set; } = null!;
    public DbSet<KnowledgeThreadStep> KnowledgeThreadSteps { get; set; } = null!;
    public DbSet<MigrationReconciliation> MigrationReconciliations { get; set; } = null!;
    public DbSet<AppUser> Users { get; set; } = null!;
    public DbSet<MfaChallenge> MfaChallenges { get; set; } = null!;
    public DbSet<ChatConversation> ChatConversations { get; set; } = null!;
    public DbSet<ChatMessage> ChatMessages { get; set; } = null!;

    // Localization Lab
    public DbSet<LocalizationProject> LocalizationProjects { get; set; } = null!;
    public DbSet<LocalizationLocale> LocalizationLocales { get; set; } = null!;
    public DbSet<LocalizationString> LocalizationStrings { get; set; } = null!;
    public DbSet<LocalizationTranslation> LocalizationTranslations { get; set; } = null!;
    public DbSet<WorkflowStep> LocalizationWorkflowSteps { get; set; } = null!;
    public DbSet<BuildSnapshot> LocalizationBuildSnapshots { get; set; } = null!;
    public DbSet<BuildSnapshotLocaleCount> LocalizationBuildSnapshotLocaleCounts { get; set; } = null!;
    public DbSet<Vendor> LocalizationVendors { get; set; } = null!;
    public DbSet<MarketplaceJob> LocalizationMarketplaceJobs { get; set; } = null!;
    public DbSet<MarketplaceBid> LocalizationMarketplaceBids { get; set; } = null!;
    public DbSet<LedgerEntry> LocalizationLedgerEntries { get; set; } = null!;
    public DbSet<ProviderHealthSnapshot> LocalizationProviderHealth { get; set; } = null!;

    // MCQ Dynamic Architecture DbSets
    public DbSet<McqQuestion> McqQuestions { get; set; } = null!;
    public DbSet<McqOption> McqOptions { get; set; } = null!;
    public DbSet<McqPresentation> McqPresentations { get; set; } = null!;
    public DbSet<McqAttempt> McqAttempts { get; set; } = null!;

    // Sessions & per-learner state
    public DbSet<UserSession> UserSessions { get; set; } = null!;
    public DbSet<UserLessonProgress> UserLessonProgress { get; set; } = null!;
    public DbSet<UserProblemProgress> UserProblemProgress { get; set; } = null!;
    public DbSet<UserExerciseDraft> UserExerciseDrafts { get; set; } = null!;
    public DbSet<UserExerciseAttempt> UserExerciseAttempts { get; set; } = null!;

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        base.OnModelCreating(modelBuilder);

        // 1. Verticals & Tasks (Preserving Quoted PascalCase table & column names)
        modelBuilder.Entity<StudyVertical>(entity =>
        {
            entity.ToTable("Verticals");
            entity.HasKey(v => v.Id);
            entity.Property(v => v.Id).HasColumnName("Id");
            entity.Property(v => v.Name).HasColumnName("Name");
            entity.Property(v => v.Description).HasColumnName("Description");
            entity.Property(v => v.CanonicalVerticalId).HasColumnName("canonical_vertical_id");
            entity.Property(v => v.ArchivedAt).HasColumnName("archived_at");
            entity.Property(v => v.UpdatedAt).HasColumnName("updated_at").HasDefaultValueSql("now()");

            entity.HasIndex(v => v.Name).IsUnique();
            entity.HasIndex(v => v.CanonicalVerticalId).HasDatabaseName("ix_verticals_canonical_vertical_id");

            entity.HasOne(v => v.CanonicalVertical)
                .WithMany(v => v.Aliases)
                .HasForeignKey(v => v.CanonicalVerticalId)
                .OnDelete(DeleteBehavior.Restrict);
        });

        modelBuilder.Entity<StudyTask>(entity =>
        {
            entity.ToTable("Tasks");
            entity.HasKey(t => t.Id);
            entity.Property(t => t.Id).HasColumnName("Id");
            entity.Property(t => t.VerticalId).HasColumnName("VerticalId");
            entity.Property(t => t.Title).HasColumnName("Title");
            entity.Property(t => t.IsCompleted).HasColumnName("IsCompleted");
            entity.Property(t => t.Module).HasColumnName("Module");
            entity.Property(t => t.UpdatedAt).HasColumnName("updated_at").HasDefaultValueSql("now()");

            entity.HasOne(t => t.Vertical)
                .WithMany(v => v.Tasks)
                .HasForeignKey(t => t.VerticalId)
                .OnDelete(DeleteBehavior.Cascade);
        });

        // 2. Courses
        modelBuilder.Entity<Course>(entity =>
        {
            entity.ToTable("courses", t =>
            {
                t.HasCheckConstraint("ck_courses_path_type", "path_type IN ('Course', 'Certification', 'Project')");
            });
            entity.HasIndex(c => c.Slug).IsUnique();
            entity.Property(c => c.PathType).HasDefaultValue("Course");
            entity.Property(c => c.IsPublished).HasDefaultValue(true);
        });

        // 3. Course Modules
        modelBuilder.Entity<CourseModule>(entity =>
        {
            entity.ToTable("course_modules");
            entity.HasIndex(m => new { m.CourseId, m.Slug }).IsUnique();
            entity.HasOne(m => m.Course)
                .WithMany(c => c.Modules)
                .HasForeignKey(m => m.CourseId)
                .OnDelete(DeleteBehavior.Cascade);
        });

        // 4. Lessons
        modelBuilder.Entity<Lesson>(entity =>
        {
            entity.ToTable("lessons", t =>
            {
                t.HasCheckConstraint("ck_lessons_content_status", "content_status IN ('Outline', 'Draft', 'Published', 'Archived')");
            });
            entity.HasIndex(l => new { l.ModuleId, l.Slug }).IsUnique();
            entity.Property(l => l.ContentStatus).HasDefaultValue("Published");
            entity.HasOne(l => l.Module)
                .WithMany(m => m.Lessons)
                .HasForeignKey(l => l.ModuleId)
                .OnDelete(DeleteBehavior.Cascade);
        });

        // 5. Problems
        modelBuilder.Entity<Problem>(entity =>
        {
            entity.ToTable("problems");
            entity.HasIndex(p => new { p.LessonId, p.Slug }).IsUnique();
            entity.HasOne(p => p.Lesson)
                .WithMany(l => l.Problems)
                .HasForeignKey(p => p.LessonId)
                .OnDelete(DeleteBehavior.Cascade);
        });

        // 6. Lesson Resources
        modelBuilder.Entity<LessonResource>(entity =>
        {
            entity.ToTable("lesson_resources");
            entity.HasIndex(r => r.LessonId);
            entity.HasOne(r => r.Lesson)
                .WithMany(l => l.Resources)
                .HasForeignKey(r => r.LessonId)
                .OnDelete(DeleteBehavior.Cascade);
        });

        // 7. Knowledge Domains
        modelBuilder.Entity<KnowledgeDomain>(entity =>
        {
            entity.ToTable("knowledge_domains");
            entity.HasIndex(d => d.Slug).IsUnique();
            entity.HasIndex(d => d.Code).IsUnique();
        });

        // 8. Knowledge Concepts
        modelBuilder.Entity<KnowledgeConcept>(entity =>
        {
            entity.ToTable("knowledge_concepts");
            entity.HasIndex(c => c.Slug).IsUnique();
        });

        // 9. Domain-Concept Connections
        modelBuilder.Entity<DomainConceptConnection>(entity =>
        {
            entity.ToTable("domain_concept_connections");
            entity.HasIndex(dc => new { dc.DomainId, dc.ConceptId }).IsUnique();
            entity.HasOne(dc => dc.Domain)
                .WithMany(d => d.ConceptConnections)
                .HasForeignKey(dc => dc.DomainId)
                .OnDelete(DeleteBehavior.Cascade);
            entity.HasOne(dc => dc.Concept)
                .WithMany(c => c.DomainConnections)
                .HasForeignKey(dc => dc.ConceptId)
                .OnDelete(DeleteBehavior.Cascade);
        });

        // 10. Concept Prerequisites
        modelBuilder.Entity<ConceptPrerequisite>(entity =>
        {
            entity.ToTable("concept_prerequisites");
            entity.HasIndex(cp => new { cp.ConceptId, cp.PrerequisiteConceptId }).IsUnique();
            entity.HasOne(cp => cp.Concept)
                .WithMany(c => c.Prerequisites)
                .HasForeignKey(cp => cp.ConceptId)
                .OnDelete(DeleteBehavior.Cascade);
            entity.HasOne(cp => cp.PrerequisiteConcept)
                .WithMany(c => c.PrerequisiteFor)
                .HasForeignKey(cp => cp.PrerequisiteConceptId)
                .OnDelete(DeleteBehavior.Restrict);
        });

        // 11. Concept Relations
        modelBuilder.Entity<ConceptRelation>(entity =>
        {
            entity.ToTable("concept_relations");
            entity.HasIndex(cr => new { cr.SourceConceptId, cr.TargetConceptId }).IsUnique();
            entity.HasOne(cr => cr.SourceConcept)
                .WithMany(c => c.OutgoingRelations)
                .HasForeignKey(cr => cr.SourceConceptId)
                .OnDelete(DeleteBehavior.Cascade);
            entity.HasOne(cr => cr.TargetConcept)
                .WithMany(c => c.IncomingRelations)
                .HasForeignKey(cr => cr.TargetConceptId)
                .OnDelete(DeleteBehavior.Restrict);
        });

        // 12. Concept Next Lessons
        modelBuilder.Entity<ConceptNextLesson>(entity =>
        {
            entity.ToTable("concept_next_lessons");
            entity.HasIndex(cnl => cnl.ConceptId);
            entity.HasOne(cnl => cnl.Concept)
                .WithMany(c => c.NextLessons)
                .HasForeignKey(cnl => cnl.ConceptId)
                .OnDelete(DeleteBehavior.Cascade);
            entity.HasOne(cnl => cnl.Lesson)
                .WithMany()
                .HasForeignKey(cnl => cnl.LessonId)
                .OnDelete(DeleteBehavior.SetNull);
        });

        // 13. Reading Map Items
        modelBuilder.Entity<ReadingMapItem>(entity =>
        {
            entity.ToTable("reading_map_items", t =>
            {
                t.HasCheckConstraint("ck_reading_map_status", "status IN ('Planned', 'Reading', 'Completed', 'Revisited', 'Deferred', 'Archived')");
                t.HasCheckConstraint("ck_reading_map_priority", "priority BETWEEN 0 AND 100");
            });
            entity.Property(r => r.Id).HasColumnName("Id");
            entity.Property(r => r.Category).HasColumnName("Category");
            entity.Property(r => r.Title).HasColumnName("Title");
            entity.Property(r => r.SubText).HasColumnName("SubText");
            entity.Property(r => r.OrderIndex).HasColumnName("OrderIndex");
            entity.Property(r => r.IsCompleted).HasColumnName("IsCompleted");
            entity.Property(r => r.CreatedAt).HasColumnName("CreatedAt");
            entity.Property(r => r.UpdatedAt).HasColumnName("UpdatedAt");

            entity.HasIndex(r => r.Category);
            entity.HasIndex(r => new { r.Status, r.ScheduledFor, r.Priority })
                .HasDatabaseName("ix_reading_map_status_schedule");

            entity.HasOne(r => r.Lesson)
                .WithMany(l => l.ReadingMapItems)
                .HasForeignKey(r => r.LessonId)
                .OnDelete(DeleteBehavior.SetNull);

            entity.HasOne(r => r.Task)
                .WithMany()
                .HasForeignKey(r => r.TaskId)
                .OnDelete(DeleteBehavior.SetNull);
        });

        // 14. Reading Activity Logs
        modelBuilder.Entity<ReadingActivityLog>(entity =>
        {
            entity.ToTable("reading_activity_logs");
            entity.Property(a => a.Id).HasColumnName("Id");
            entity.Property(a => a.DayLabel).HasColumnName("DayLabel");
            entity.Property(a => a.ActivityCount).HasColumnName("ActivityCount");
            entity.Property(a => a.OrderIndex).HasColumnName("OrderIndex");
            entity.Property(a => a.LogDate).HasColumnName("LogDate");
            entity.HasIndex(a => a.DayLabel);
        });

        // 15. Knowledge Threads
        modelBuilder.Entity<KnowledgeThread>(entity =>
        {
            entity.ToTable("knowledge_threads");
            entity.Property(k => k.Id).HasColumnName("Id");
            entity.Property(k => k.Domain).HasColumnName("Domain");
            entity.Property(k => k.RawPath).HasColumnName("RawPath");
            entity.Property(k => k.OrderIndex).HasColumnName("OrderIndex");
            entity.HasIndex(k => k.Domain);
        });

        // 16. Lesson Code Comparisons
        modelBuilder.Entity<LessonCodeComparison>(entity =>
        {
            entity.ToTable("lesson_code_comparisons");
            entity.HasIndex(c => c.LessonId);
            entity.HasOne(c => c.Lesson)
                .WithMany(l => l.CodeComparisons)
                .HasForeignKey(c => c.LessonId)
                .OnDelete(DeleteBehavior.Cascade);
        });

        // 17. Lesson Diagrams
        modelBuilder.Entity<LessonDiagram>(entity =>
        {
            entity.ToTable("lesson_diagrams");
            entity.HasIndex(d => d.LessonId);
            entity.HasOne(d => d.Lesson)
                .WithMany(l => l.Diagrams)
                .HasForeignKey(d => d.LessonId)
                .OnDelete(DeleteBehavior.Cascade);
        });

        // 18. Lesson Notes
        modelBuilder.Entity<LessonNote>(entity =>
        {
            entity.ToTable("lesson_notes");
            entity.HasIndex(n => new { n.LessonId, n.NoteType });
            entity.HasIndex(n => new { n.UserId, n.LessonId })
                .HasDatabaseName("ix_lesson_notes_user_lesson");
            entity.HasOne(n => n.Lesson)
                .WithMany(l => l.Notes)
                .HasForeignKey(n => n.LessonId)
                .OnDelete(DeleteBehavior.Cascade);
            entity.HasOne(n => n.User)
                .WithMany()
                .HasForeignKey(n => n.UserId)
                .OnDelete(DeleteBehavior.Cascade);
        });

        // ============================================================================
        // 19. Phase 2 Bridge Schema Configurations
        // ============================================================================

        // CourseDomainLink (Composite PK)
        modelBuilder.Entity<CourseDomainLink>(entity =>
        {
            entity.ToTable("course_domain_links");
            entity.HasKey(cd => new { cd.CourseId, cd.DomainId });
            entity.HasOne(cd => cd.Course)
                .WithMany(c => c.DomainLinks)
                .HasForeignKey(cd => cd.CourseId)
                .OnDelete(DeleteBehavior.Cascade);
            entity.HasOne(cd => cd.Domain)
                .WithMany(d => d.CourseLinks)
                .HasForeignKey(cd => cd.DomainId)
                .OnDelete(DeleteBehavior.Cascade);
            entity.HasIndex(cd => new { cd.DomainId, cd.OrderIndex })
                .HasDatabaseName("ix_course_domain_links_domain_id");
        });

        // LessonConceptLink (Composite PK & Check Constraint)
        modelBuilder.Entity<LessonConceptLink>(entity =>
        {
            entity.ToTable("lesson_concept_links", t =>
            {
                t.HasCheckConstraint("ck_lesson_concept_relationship", "relationship_type IN ('Primary', 'Related', 'PrerequisiteContext')");
            });
            entity.HasKey(lc => new { lc.LessonId, lc.ConceptId, lc.RelationshipType });
            entity.HasOne(lc => lc.Lesson)
                .WithMany(l => l.ConceptLinks)
                .HasForeignKey(lc => lc.LessonId)
                .OnDelete(DeleteBehavior.Cascade);
            entity.HasOne(lc => lc.Concept)
                .WithMany(c => c.LessonLinks)
                .HasForeignKey(lc => lc.ConceptId)
                .OnDelete(DeleteBehavior.Cascade);
            entity.HasIndex(lc => new { lc.ConceptId, lc.RelationshipType, lc.OrderIndex })
                .HasDatabaseName("ix_lesson_concept_links_concept");
        });

        // LessonRelation
        modelBuilder.Entity<LessonRelation>(entity =>
        {
            entity.ToTable("lesson_relations", t =>
            {
                t.HasCheckConstraint("ck_lesson_relation_type", "relationship_type IN ('Prerequisite', 'Related', 'Next')");
                t.HasCheckConstraint("ck_lesson_relation_resolution", "resolution_status IN ('Unresolved', 'Resolved', 'External')");
                t.HasCheckConstraint("ck_lesson_relation_target", "target_lesson_id IS NOT NULL OR length(trim(target_title)) > 0");
            });
            entity.HasKey(lr => lr.Id);
            entity.HasOne(lr => lr.SourceLesson)
                .WithMany(l => l.OutgoingRelations)
                .HasForeignKey(lr => lr.SourceLessonId)
                .OnDelete(DeleteBehavior.Cascade);
            entity.HasOne(lr => lr.TargetLesson)
                .WithMany(l => l.IncomingRelations)
                .HasForeignKey(lr => lr.TargetLessonId)
                .OnDelete(DeleteBehavior.SetNull);
            entity.HasIndex(lr => new { lr.SourceLessonId, lr.RelationshipType, lr.TargetTitle })
                .IsUnique()
                .HasDatabaseName("ux_lesson_relations_identity");
            entity.HasIndex(lr => lr.TargetLessonId)
                .HasDatabaseName("ix_lesson_relations_target_lesson");
        });

        // StudyTaskContentLink (Exclusive Arc Check & Restrict delete on Lesson/Problem)
        modelBuilder.Entity<StudyTaskContentLink>(entity =>
        {
            entity.ToTable("study_task_content_links", t =>
            {
                t.HasCheckConstraint("ck_task_content_exactly_one_target", "num_nonnulls(lesson_id, problem_id) = 1");
                t.HasCheckConstraint("ck_task_content_mapping_type", "mapping_type IN ('Exact', 'TitleAndModule', 'Manual', 'DuplicateAlias')");
                t.HasCheckConstraint("ck_task_content_mapping_status", "mapping_status IN ('Proposed', 'Verified', 'Rejected')");
                t.HasCheckConstraint("ck_task_content_confidence", "confidence >= 0 AND confidence <= 1");
            });
            entity.HasKey(tc => tc.TaskId);
            entity.HasOne(tc => tc.Task)
                .WithOne(t => t.ContentLink)
                .HasForeignKey<StudyTaskContentLink>(tc => tc.TaskId)
                .OnDelete(DeleteBehavior.Cascade);
            entity.HasOne(tc => tc.Lesson)
                .WithMany(l => l.LegacyTaskLinks)
                .HasForeignKey(tc => tc.LessonId)
                .OnDelete(DeleteBehavior.Restrict);
            entity.HasOne(tc => tc.Problem)
                .WithMany(p => p.LegacyTaskLinks)
                .HasForeignKey(tc => tc.ProblemId)
                .OnDelete(DeleteBehavior.Restrict);
            entity.HasIndex(tc => tc.LessonId)
                .HasDatabaseName("ix_task_content_links_lesson");
            entity.HasIndex(tc => tc.ProblemId)
                .HasDatabaseName("ix_task_content_links_problem");
        });

        // LearningActivity
        modelBuilder.Entity<LearningActivity>(entity =>
        {
            entity.ToTable("learning_activity", t =>
            {
                t.HasCheckConstraint("ck_learning_activity_event_type",
                    "event_type IN ('LessonCompleted', 'LessonReopened', 'ProblemCompleted', 'ProblemReopened', 'TaskCompleted', 'TaskReopened', 'ReadingScheduled', 'ReadingDeferred', 'ReadingRevisited', 'NoteCreated', 'ChapterImported', 'LessonOpened', 'McqAnswered', 'ProblemAttempted', 'SolutionRevealed', 'ExerciseRun')");
            });
            entity.HasKey(la => la.Id);
            entity.HasOne(la => la.User)
                .WithMany()
                .HasForeignKey(la => la.UserId)
                .OnDelete(DeleteBehavior.Cascade);
            entity.HasIndex(la => new { la.UserId, la.OccurredAt })
                .HasDatabaseName("ix_learning_activity_user");
            entity.HasOne(la => la.Lesson)
                .WithMany()
                .HasForeignKey(la => la.LessonId)
                .OnDelete(DeleteBehavior.SetNull);
            entity.HasOne(la => la.Problem)
                .WithMany()
                .HasForeignKey(la => la.ProblemId)
                .OnDelete(DeleteBehavior.SetNull);
            entity.HasOne(la => la.Task)
                .WithMany()
                .HasForeignKey(la => la.TaskId)
                .OnDelete(DeleteBehavior.SetNull);
            entity.HasOne(la => la.ReadingMapItem)
                .WithMany()
                .HasForeignKey(la => la.ReadingMapItemId)
                .OnDelete(DeleteBehavior.SetNull);
            entity.HasIndex(la => new { la.CorrelationId, la.EventType })
                .IsUnique()
                .HasDatabaseName("ux_learning_activity_correlation_event");
            entity.HasIndex(la => la.OccurredAt)
                .HasDatabaseName("ix_learning_activity_occurred_at");
            entity.HasIndex(la => new { la.LessonId, la.OccurredAt })
                .HasDatabaseName("ix_learning_activity_lesson");
        });

        // KnowledgeThreadStep (Composite PK)
        modelBuilder.Entity<KnowledgeThreadStep>(entity =>
        {
            entity.ToTable("knowledge_thread_steps", t =>
            {
                t.HasCheckConstraint("ck_knowledge_thread_step_label", "length(trim(label)) > 0");
            });
            entity.HasKey(kts => new { kts.ThreadId, kts.OrderIndex });
            entity.HasOne(kts => kts.Thread)
                .WithMany(kt => kt.Steps)
                .HasForeignKey(kts => kts.ThreadId)
                .OnDelete(DeleteBehavior.Cascade);
            entity.HasOne(kts => kts.Concept)
                .WithMany(kc => kc.ThreadSteps)
                .HasForeignKey(kts => kts.ConceptId)
                .OnDelete(DeleteBehavior.SetNull);
            entity.HasOne(kts => kts.Lesson)
                .WithMany()
                .HasForeignKey(kts => kts.LessonId)
                .OnDelete(DeleteBehavior.SetNull);
            entity.HasIndex(kts => kts.ConceptId)
                .HasDatabaseName("ix_knowledge_thread_steps_concept");
        });

        // MigrationReconciliation
        modelBuilder.Entity<MigrationReconciliation>(entity =>
        {
            entity.ToTable("migration_reconciliation", t =>
            {
                t.HasCheckConstraint("ck_migration_reconciliation_status", "status IN ('Discovered', 'Mapped', 'Applied', 'Verified', 'Conflict', 'Skipped')");
            });
            entity.HasKey(mr => mr.Id);
            entity.HasIndex(mr => new { mr.MigrationKey, mr.SourceType, mr.SourceId })
                .IsUnique()
                .HasDatabaseName("ux_migration_reconciliation_identity");
            entity.HasIndex(mr => new { mr.MigrationKey, mr.Status })
                .HasDatabaseName("ix_migration_reconciliation_status");
        });

        // 20. Users (Authentication & Authorization)
        modelBuilder.Entity<AppUser>(entity =>
        {
            entity.ToTable("app_users", t =>
            {
                t.HasCheckConstraint("ck_app_users_role", "role IN ('User', 'Admin')");
                t.HasCheckConstraint("ck_app_users_status", "status IN ('PendingApproval', 'Approved', 'Rejected', 'Disabled')");
            });
            entity.HasKey(u => u.Id);
            entity.HasIndex(u => u.Email)
                .IsUnique()
                .HasDatabaseName("ix_app_users_email");
            entity.HasOne(u => u.DecidedByUser)
                .WithMany()
                .HasForeignKey(u => u.DecidedByUserId)
                .OnDelete(DeleteBehavior.Restrict);
        });

        // 21. MFA Challenges (TOTP Second Factor)
        modelBuilder.Entity<MfaChallenge>(entity =>
        {
            entity.ToTable("mfa_challenges", t =>
            {
                t.HasCheckConstraint("ck_mfa_challenges_purpose", "purpose IN ('Enrollment', 'Login')");
            });
            entity.HasKey(c => c.Id);
            entity.HasIndex(c => c.UserId)
                .HasDatabaseName("ix_mfa_challenges_user_id");
            entity.HasIndex(c => c.ExpiresAt)
                .HasDatabaseName("ix_mfa_challenges_expires_at");
            entity.HasOne(c => c.User)
                .WithMany()
                .HasForeignKey(c => c.UserId)
                .OnDelete(DeleteBehavior.Cascade);
        });

        // 22. Chat Conversations
        modelBuilder.Entity<ChatConversation>(entity =>
        {
            entity.ToTable("chat_conversations");
            entity.HasKey(c => c.Id);
            entity.HasIndex(c => c.UserId)
                .HasDatabaseName("ix_chat_conversations_user_id");
            entity.HasIndex(c => c.LessonId)
                .HasDatabaseName("ix_chat_conversations_lesson_id");
            entity.HasIndex(c => c.UpdatedAt)
                .HasDatabaseName("ix_chat_conversations_updated_at");

            entity.HasOne(c => c.User)
                .WithMany()
                .HasForeignKey(c => c.UserId)
                .OnDelete(DeleteBehavior.Cascade);

            entity.HasOne(c => c.Lesson)
                .WithMany()
                .HasForeignKey(c => c.LessonId)
                .OnDelete(DeleteBehavior.SetNull);
        });

        // 23. Chat Messages
        modelBuilder.Entity<ChatMessage>(entity =>
        {
            entity.ToTable("chat_messages", t =>
            {
                t.HasCheckConstraint("ck_chat_messages_role", "role IN ('system', 'user', 'assistant')");
            });
            entity.HasKey(m => m.Id);
            entity.HasIndex(m => m.ConversationId)
                .HasDatabaseName("ix_chat_messages_conversation_id");
            entity.HasIndex(m => m.CreatedAt)
                .HasDatabaseName("ix_chat_messages_created_at");
            entity.HasIndex(m => m.ClientRequestId)
                .HasDatabaseName("ix_chat_messages_client_request_id");

            entity.HasOne(m => m.Conversation)
                .WithMany(c => c.Messages)
                .HasForeignKey(m => m.ConversationId)
                .OnDelete(DeleteBehavior.Cascade);
        });

        // 24. Localization Lab
        modelBuilder.Entity<LocalizationProject>(entity =>
        {
            entity.ToTable("localization_projects");
            entity.HasKey(p => p.Id);
            entity.HasIndex(p => p.Slug)
                .IsUnique()
                .HasDatabaseName("ix_localization_projects_slug");
        });

        modelBuilder.Entity<LocalizationLocale>(entity =>
        {
            entity.ToTable("localization_locales");
            entity.HasKey(l => l.Id);
            entity.HasIndex(l => l.ProjectId)
                .HasDatabaseName("ix_localization_locales_project_id");
            entity.HasOne(l => l.Project)
                .WithMany(p => p.Locales)
                .HasForeignKey(l => l.ProjectId)
                .OnDelete(DeleteBehavior.Cascade);
        });

        modelBuilder.Entity<LocalizationString>(entity =>
        {
            entity.ToTable("localization_strings");
            entity.HasKey(s => s.Id);
            entity.HasIndex(s => s.ProjectId)
                .HasDatabaseName("ix_localization_strings_project_id");
            entity.HasOne(s => s.Project)
                .WithMany(p => p.Strings)
                .HasForeignKey(s => s.ProjectId)
                .OnDelete(DeleteBehavior.Cascade);
        });

        modelBuilder.Entity<LocalizationTranslation>(entity =>
        {
            entity.ToTable("localization_translations");
            entity.HasKey(t => t.Id);
            entity.HasIndex(t => new { t.StringId, t.LocaleCode })
                .IsUnique()
                .HasDatabaseName("ix_localization_translations_string_id_locale_code");
            entity.HasOne(t => t.String)
                .WithMany(s => s.Translations)
                .HasForeignKey(t => t.StringId)
                .OnDelete(DeleteBehavior.Cascade);
        });

        modelBuilder.Entity<WorkflowStep>(entity =>
        {
            entity.ToTable("localization_workflow_steps");
            entity.HasKey(w => w.Id);
            entity.HasIndex(w => w.ProjectId)
                .HasDatabaseName("ix_localization_workflow_steps_project_id");
            entity.HasOne(w => w.Project)
                .WithMany(p => p.WorkflowSteps)
                .HasForeignKey(w => w.ProjectId)
                .OnDelete(DeleteBehavior.Cascade);
        });

        modelBuilder.Entity<BuildSnapshot>(entity =>
        {
            entity.ToTable("localization_build_snapshots");
            entity.HasKey(b => b.Id);
            entity.HasIndex(b => b.ProjectId)
                .HasDatabaseName("ix_localization_build_snapshots_project_id");
            entity.HasOne(b => b.Project)
                .WithMany(p => p.BuildSnapshots)
                .HasForeignKey(b => b.ProjectId)
                .OnDelete(DeleteBehavior.Cascade);
        });

        modelBuilder.Entity<BuildSnapshotLocaleCount>(entity =>
        {
            entity.ToTable("localization_build_snapshot_locale_counts");
            entity.HasKey(c => c.Id);
            entity.HasIndex(c => c.BuildSnapshotId)
                .HasDatabaseName("ix_localization_build_snapshot_locale_counts_snapshot_id");
            entity.HasOne(c => c.BuildSnapshot)
                .WithMany(b => b.LocaleCounts)
                .HasForeignKey(c => c.BuildSnapshotId)
                .OnDelete(DeleteBehavior.Cascade);
        });

        modelBuilder.Entity<Vendor>(entity =>
        {
            entity.ToTable("localization_vendors");
            entity.HasKey(v => v.Id);
            entity.Property(v => v.Rating)
                .HasPrecision(3, 1);
        });

        modelBuilder.Entity<MarketplaceJob>(entity =>
        {
            entity.ToTable("localization_marketplace_jobs");
            entity.HasKey(j => j.Id);
            entity.HasIndex(j => j.ProjectId)
                .HasDatabaseName("ix_localization_marketplace_jobs_project_id");
            entity.HasIndex(j => j.AwardedVendorId)
                .HasDatabaseName("ix_localization_marketplace_jobs_vendor_id");
            entity.Property(j => j.SuggestedPriceLow)
                .HasPrecision(10, 2);
            entity.Property(j => j.SuggestedPriceHigh)
                .HasPrecision(10, 2);
            entity.HasOne(j => j.Project)
                .WithMany(p => p.MarketplaceJobs)
                .HasForeignKey(j => j.ProjectId)
                .OnDelete(DeleteBehavior.Cascade);
            entity.HasOne(j => j.AwardedVendor)
                .WithMany(v => v.AwardedJobs)
                .HasForeignKey(j => j.AwardedVendorId)
                .OnDelete(DeleteBehavior.SetNull);
        });

        modelBuilder.Entity<MarketplaceBid>(entity =>
        {
            entity.ToTable("localization_marketplace_bids");
            entity.HasKey(b => b.Id);
            entity.HasIndex(b => b.MarketplaceJobId)
                .HasDatabaseName("ix_localization_marketplace_bids_job_id");
            entity.HasIndex(b => b.VendorId)
                .HasDatabaseName("ix_localization_marketplace_bids_vendor_id");
            entity.Property(b => b.ProposedPrice)
                .HasPrecision(10, 2);
            entity.HasOne(b => b.MarketplaceJob)
                .WithMany(j => j.Bids)
                .HasForeignKey(b => b.MarketplaceJobId)
                .OnDelete(DeleteBehavior.Cascade);
            entity.HasOne(b => b.Vendor)
                .WithMany(v => v.Bids)
                .HasForeignKey(b => b.VendorId)
                .OnDelete(DeleteBehavior.Cascade);
        });

        modelBuilder.Entity<LedgerEntry>(entity =>
        {
            entity.ToTable("localization_ledger_entries");
            entity.HasKey(l => l.Id);
            entity.HasIndex(l => l.ProjectId)
                .HasDatabaseName("ix_localization_ledger_entries_project_id");
            entity.HasIndex(l => l.RelatedMarketplaceJobId)
                .HasDatabaseName("ix_localization_ledger_entries_job_id");
            entity.Property(l => l.Amount)
                .HasPrecision(10, 2);
            entity.HasOne(l => l.Project)
                .WithMany(p => p.LedgerEntries)
                .HasForeignKey(l => l.ProjectId)
                .OnDelete(DeleteBehavior.Cascade);
            entity.HasOne(l => l.RelatedMarketplaceJob)
                .WithMany()
                .HasForeignKey(l => l.RelatedMarketplaceJobId)
                .OnDelete(DeleteBehavior.SetNull);
        });

        modelBuilder.Entity<ProviderHealthSnapshot>(entity =>
        {
            entity.ToTable("localization_provider_health");
            entity.HasKey(p => p.Id);
            entity.Property(p => p.ErrorRatePercent)
                .HasPrecision(5, 2);
        });

        // 25. MCQ Dynamic Architecture
        modelBuilder.Entity<McqQuestion>(entity =>
        {
            entity.ToTable("mcq_questions");
            entity.HasKey(q => q.Id);

            entity.HasIndex(q => q.LegacyKey)
                .IsUnique()
                .HasDatabaseName("ux_mcq_questions_legacy_key");

            entity.HasIndex(q => q.LessonId)
                .HasDatabaseName("ix_mcq_questions_lesson_id");

            entity.Property(q => q.IsActive)
                .HasDefaultValue(true);

            entity.Property(q => q.Category)
                .HasDefaultValue("Assignment");

            entity.HasOne(q => q.Lesson)
                .WithMany()
                .HasForeignKey(q => q.LessonId)
                .OnDelete(DeleteBehavior.Cascade);
        });

        modelBuilder.Entity<McqOption>(entity =>
        {
            entity.ToTable("mcq_options");
            entity.HasKey(o => o.Id);

            entity.HasIndex(o => o.QuestionId)
                .HasDatabaseName("ix_mcq_options_question_id");

            entity.HasOne(o => o.Question)
                .WithMany(q => q.Options)
                .HasForeignKey(o => o.QuestionId)
                .OnDelete(DeleteBehavior.Cascade);
        });

        modelBuilder.Entity<McqPresentation>(entity =>
        {
            entity.ToTable("mcq_presentations");
            entity.HasKey(p => p.Id);

            entity.HasIndex(p => p.UserId)
                .HasDatabaseName("ix_mcq_presentations_user_id");

            entity.HasIndex(p => p.QuestionId)
                .HasDatabaseName("ix_mcq_presentations_question_id");

            entity.HasOne(p => p.Question)
                .WithMany(q => q.Presentations)
                .HasForeignKey(p => p.QuestionId)
                .OnDelete(DeleteBehavior.Cascade);

            entity.HasOne(p => p.User)
                .WithMany()
                .HasForeignKey(p => p.UserId)
                .OnDelete(DeleteBehavior.SetNull);
        });

        modelBuilder.Entity<McqAttempt>(entity =>
        {
            entity.ToTable("mcq_attempts");
            entity.HasKey(a => a.Id);

            entity.HasIndex(a => a.PresentationId)
                .IsUnique()
                .HasDatabaseName("ux_mcq_attempts_presentation_id");

            entity.HasOne(a => a.Presentation)
                .WithOne(p => p.Attempt)
                .HasForeignKey<McqAttempt>(a => a.PresentationId)
                .OnDelete(DeleteBehavior.Cascade);
        });

        // 26. Sessions & per-learner state
        modelBuilder.Entity<UserSession>(entity =>
        {
            entity.ToTable("user_sessions");
            entity.HasKey(s => s.Id);
            entity.HasIndex(s => s.RefreshTokenHash)
                .IsUnique()
                .HasDatabaseName("ux_user_sessions_refresh_token_hash");
            entity.HasIndex(s => s.PreviousRefreshTokenHash)
                .HasDatabaseName("ix_user_sessions_previous_refresh_token_hash");
            entity.HasIndex(s => new { s.UserId, s.RevokedAt })
                .HasDatabaseName("ix_user_sessions_user_active");
            entity.HasOne(s => s.User)
                .WithMany()
                .HasForeignKey(s => s.UserId)
                .OnDelete(DeleteBehavior.Cascade);
        });

        modelBuilder.Entity<UserLessonProgress>(entity =>
        {
            entity.ToTable("user_lesson_progress", t =>
            {
                t.HasCheckConstraint("ck_user_lesson_progress_status", "status IN ('InProgress', 'Completed')");
                t.HasCheckConstraint("ck_user_lesson_progress_scroll", "scroll_percent >= 0 AND scroll_percent <= 100");
            });
            entity.HasKey(p => p.Id);
            entity.HasIndex(p => new { p.UserId, p.LessonId })
                .IsUnique()
                .HasDatabaseName("ux_user_lesson_progress_user_lesson");
            entity.HasIndex(p => new { p.UserId, p.LastOpenedAt })
                .HasDatabaseName("ix_user_lesson_progress_user_recent");
            entity.HasOne(p => p.User)
                .WithMany()
                .HasForeignKey(p => p.UserId)
                .OnDelete(DeleteBehavior.Cascade);
            entity.HasOne(p => p.Lesson)
                .WithMany()
                .HasForeignKey(p => p.LessonId)
                .OnDelete(DeleteBehavior.Cascade);
        });

        modelBuilder.Entity<UserExerciseDraft>(entity =>
        {
            entity.ToTable("user_exercise_drafts");
            entity.HasKey(d => d.Id);
            entity.HasIndex(d => new { d.UserId, d.ExerciseId })
                .IsUnique()
                .HasDatabaseName("ux_user_exercise_drafts_user_exercise");
            entity.HasOne(d => d.User)
                .WithMany()
                .HasForeignKey(d => d.UserId)
                .OnDelete(DeleteBehavior.Cascade);
        });

        modelBuilder.Entity<UserExerciseAttempt>(entity =>
        {
            entity.ToTable("user_exercise_attempts", t =>
            {
                t.HasCheckConstraint("ck_user_exercise_attempts_status", "status IN ('success', 'testFailure', 'compilationFailure', 'timeout')");
            });
            entity.HasKey(a => a.Id);
            entity.HasIndex(a => new { a.UserId, a.ExerciseId, a.SubmittedAt })
                .HasDatabaseName("ix_user_exercise_attempts_user_exercise_time");
            entity.HasOne(a => a.User)
                .WithMany()
                .HasForeignKey(a => a.UserId)
                .OnDelete(DeleteBehavior.Cascade);
        });

        modelBuilder.Entity<UserProblemProgress>(entity =>
        {
            entity.ToTable("user_problem_progress", t =>
            {
                t.HasCheckConstraint("ck_user_problem_progress_status", "status IN ('NotStarted', 'Attempted', 'Solved')");
            });
            entity.HasKey(p => p.Id);
            entity.HasIndex(p => new { p.UserId, p.ProblemId })
                .IsUnique()
                .HasDatabaseName("ux_user_problem_progress_user_problem");
            entity.HasOne(p => p.User)
                .WithMany()
                .HasForeignKey(p => p.UserId)
                .OnDelete(DeleteBehavior.Cascade);
            entity.HasOne(p => p.Problem)
                .WithMany()
                .HasForeignKey(p => p.ProblemId)
                .OnDelete(DeleteBehavior.Cascade);
        });
    }
}
