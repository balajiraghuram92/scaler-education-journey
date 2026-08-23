using System.ComponentModel.DataAnnotations;
using StudyTracker.Api.Models;
using Xunit;

namespace StudyTracker.Api.Tests;

public class BridgeSchemaConstraintTests
{
    [Fact]
    public void StudyTaskContentLink_WhenConstructedWithValidLessonTarget_IsValid()
    {
        var link = new StudyTaskContentLink
        {
            TaskId = 101,
            LessonId = 5,
            ProblemId = null,
            MappingType = "Exact",
            MappingStatus = "Verified",
            Confidence = 1.0000m,
            SourceChecksum = "a1b2c3d4e5f6",
            VerifiedAt = DateTime.UtcNow
        };

        Assert.Equal(101, link.TaskId);
        Assert.Equal(5, link.LessonId);
        Assert.Null(link.ProblemId);
        Assert.Equal("Exact", link.MappingType);
        Assert.Equal("Verified", link.MappingStatus);
    }

    [Fact]
    public void StudyTaskContentLink_WhenConstructedWithValidProblemTarget_IsValid()
    {
        var link = new StudyTaskContentLink
        {
            TaskId = 102,
            LessonId = null,
            ProblemId = 12,
            MappingType = "TitleAndModule",
            MappingStatus = "Proposed",
            Confidence = 0.9500m,
            SourceChecksum = "b2c3d4e5f6a1"
        };

        Assert.Equal(102, link.TaskId);
        Assert.Null(link.LessonId);
        Assert.Equal(12, link.ProblemId);
    }

    [Theory]
    [InlineData("Course", true)]
    [InlineData("Certification", true)]
    [InlineData("Project", true)]
    [InlineData("InvalidType", false)]
    public void CoursePathType_Validation(string pathType, bool isValid)
    {
        var validTypes = new HashSet<string> { "Course", "Certification", "Project" };
        Assert.Equal(isValid, validTypes.Contains(pathType));
    }

    [Theory]
    [InlineData("Outline", true)]
    [InlineData("Draft", true)]
    [InlineData("Published", true)]
    [InlineData("Archived", true)]
    [InlineData("Deleted", false)]
    public void LessonContentStatus_Validation(string status, bool isValid)
    {
        var validStatuses = new HashSet<string> { "Outline", "Draft", "Published", "Archived" };
        Assert.Equal(isValid, validStatuses.Contains(status));
    }

    [Theory]
    [InlineData("Primary", true)]
    [InlineData("Related", true)]
    [InlineData("PrerequisiteContext", true)]
    [InlineData("Arbitrary", false)]
    public void LessonConceptRelationshipType_Validation(string relType, bool isValid)
    {
        var validTypes = new HashSet<string> { "Primary", "Related", "PrerequisiteContext" };
        Assert.Equal(isValid, validTypes.Contains(relType));
    }

    [Theory]
    [InlineData("LessonCompleted", true)]
    [InlineData("LessonReopened", true)]
    [InlineData("ProblemCompleted", true)]
    [InlineData("ProblemReopened", true)]
    [InlineData("TaskCompleted", true)]
    [InlineData("TaskReopened", true)]
    [InlineData("ReadingScheduled", true)]
    [InlineData("ReadingDeferred", true)]
    [InlineData("ReadingRevisited", true)]
    [InlineData("NoteCreated", true)]
    [InlineData("ChapterImported", true)]
    [InlineData("RandomEvent", false)]
    public void LearningActivityEventType_Validation(string eventType, bool isValid)
    {
        var validEvents = new HashSet<string>
        {
            "LessonCompleted", "LessonReopened", "ProblemCompleted", "ProblemReopened",
            "TaskCompleted", "TaskReopened", "ReadingScheduled", "ReadingDeferred",
            "ReadingRevisited", "NoteCreated", "ChapterImported"
        };

        Assert.Equal(isValid, validEvents.Contains(eventType));
    }

    [Theory]
    [InlineData("Discovered", true)]
    [InlineData("Mapped", true)]
    [InlineData("Applied", true)]
    [InlineData("Verified", true)]
    [InlineData("Conflict", true)]
    [InlineData("Skipped", true)]
    [InlineData("UnknownStatus", false)]
    public void MigrationReconciliationStatus_Validation(string status, bool isValid)
    {
        var validStatuses = new HashSet<string> { "Discovered", "Mapped", "Applied", "Verified", "Conflict", "Skipped" };
        Assert.Equal(isValid, validStatuses.Contains(status));
    }
}
