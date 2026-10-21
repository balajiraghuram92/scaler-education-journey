using System.Text.Json;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Logging.Abstractions;
using StudyTracker.Api.Data;
using StudyTracker.Api.Models;
using StudyTracker.Api.Options;
using StudyTracker.Api.Services;
using StudyTracker.Api.Services.Exercises;
using Xunit;

namespace StudyTracker.Api.Tests.Exercises;

public class PythonExerciseTests
{
    private static ExerciseDefinition PythonDefinition(string root)
    {
        var manifest = new ExerciseManifest
        {
            Id = "py-test-exercise",
            Language = "python",
            Runtime = new ExerciseRuntimeManifest { Profile = "python-pytest", TimeoutSeconds = 20 },
            Files = new List<ExerciseFileManifest>
            {
                new() { Id = "impl", Path = "pkg/impl.py", DisplayName = "impl.py", Editable = true },
                new() { Id = "models", Path = "pkg/models.py", DisplayName = "models.py", Editable = false }
            },
            TestSuite = new ExerciseTestSuiteManifest { Path = "tests" },
            Evidence = new List<ExerciseEvidenceManifest>
            {
                new() { Id = "adds", Label = "Adds numbers", TestMethod = "test_adds" },
                new() { Id = "rejects", Label = "Rejects bad input", TestMethod = "test_rejects" }
            }
        };

        return new ExerciseDefinition
        {
            Manifest = manifest,
            ManifestPath = Path.Combine(root, "exercise.json"),
            ExerciseRoot = root,
            EditableFiles = manifest.Files.Where(f => f.Editable).ToDictionary(f => f.Path, StringComparer.Ordinal),
            EvidenceByTestMethod = manifest.Evidence.ToDictionary(e => e.TestMethod, StringComparer.Ordinal)
        };
    }

    private static string PythonRoot()
    {
        var root = Path.Combine(Path.GetTempPath(), "studytracker-py-exercise-tests", Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(Path.Combine(root, "starter", "pkg"));
        Directory.CreateDirectory(Path.Combine(root, "solution", "pkg"));
        Directory.CreateDirectory(Path.Combine(root, "tests", "helpers"));
        File.WriteAllText(Path.Combine(root, "starter", "pkg", "impl.py"), "def add(a, b):\n    raise NotImplementedError\n");
        File.WriteAllText(Path.Combine(root, "starter", "pkg", "models.py"), "LIMIT = 10\n");
        File.WriteAllText(Path.Combine(root, "solution", "pkg", "impl.py"), "def add(a, b):\n    return a + b\n");
        File.WriteAllText(Path.Combine(root, "tests", "test_impl.py"), "def test_adds():\n    pass\n");
        File.WriteAllText(Path.Combine(root, "tests", "conftest.py"), "");
        File.WriteAllText(Path.Combine(root, "tests", "helpers", "data.py"), "X = 1\n");
        return root;
    }

    private static RunnerExecutionResult Run(string? xml, int exitCode, string stdout = "") => new()
    {
        RunId = Guid.NewGuid(),
        ExitCode = exitCode,
        StandardOutput = stdout,
        SurefireXml = xml
    };

    [Fact]
    public async Task WorkspaceBuilder_CopiesProvidedFiles_Submission_AndWholeTestDirectory()
    {
        var root = PythonRoot();
        var workspaceRoot = Path.Combine(Path.GetTempPath(), "studytracker-py-ws", Guid.NewGuid().ToString("N"));
        try
        {
            var builder = new ExerciseWorkspaceBuilder(Microsoft.Extensions.Options.Options.Create(ExerciseTestFactory.Options(workspaceRoot)));
            var submission = new Dictionary<string, ExerciseFileSubmission>
            {
                ["pkg/impl.py"] = new("pkg/impl.py", "def add(a, b):\n    return a + b\n")
            };

            var workspace = await builder.BuildAsync(Guid.NewGuid(), PythonDefinition(root), submission, CancellationToken.None);

            Assert.Equal("LIMIT = 10\n", File.ReadAllText(Path.Combine(workspace.Path, "pkg", "models.py")));
            Assert.Contains("return a + b", File.ReadAllText(Path.Combine(workspace.Path, "pkg", "impl.py")));
            Assert.True(File.Exists(Path.Combine(workspace.Path, "tests", "test_impl.py")));
            Assert.True(File.Exists(Path.Combine(workspace.Path, "tests", "conftest.py")));
            Assert.True(File.Exists(Path.Combine(workspace.Path, "tests", "helpers", "data.py")));
            Assert.False(File.Exists(Path.Combine(workspace.Path, "pom.xml")));
        }
        finally
        {
            ExerciseTestFactory.DeleteRoot(root);
            ExerciseTestFactory.DeleteRoot(workspaceRoot);
        }
    }

    [Fact]
    public void Repository_LoadsPythonManifest_WithTestDirectory()
    {
        var root = PythonRoot();
        try
        {
            File.WriteAllText(Path.Combine(root, "exercise.json"), JsonSerializer.Serialize(PythonDefinition(root).Manifest));
            var repository = new ExerciseRepository(
                Microsoft.Extensions.Options.Options.Create(new ExerciseExecutionOptions { ExercisesRoot = root }),
                NullLogger<ExerciseRepository>.Instance);

            var definition = repository.GetById("py-test-exercise");
            Assert.NotNull(definition);
            Assert.Single(definition!.EditableFiles);
        }
        finally
        {
            ExerciseTestFactory.DeleteRoot(root);
        }
    }

    [Fact]
    public void Repository_RejectsPythonManifest_WithoutTests()
    {
        var root = PythonRoot();
        try
        {
            Directory.Delete(Path.Combine(root, "tests"), recursive: true);
            File.WriteAllText(Path.Combine(root, "exercise.json"), JsonSerializer.Serialize(PythonDefinition(root).Manifest));
            Assert.Throws<InvalidOperationException>(() => new ExerciseRepository(
                Microsoft.Extensions.Options.Options.Create(new ExerciseExecutionOptions { ExercisesRoot = root }),
                NullLogger<ExerciseRepository>.Instance));
        }
        finally
        {
            ExerciseTestFactory.DeleteRoot(root);
        }
    }

    [Fact]
    public void Classifier_TreatsCollectionErrors_AsCompilationFailure()
    {
        var classifier = new ExerciseExecutionClassifier(new SurefireResultParser());
        const string xml = """
            <testsuites><testsuite name="pytest" errors="1" failures="0" tests="1">
              <testcase classname="" name="tests.test_impl" time="0.0"><error message="collection failure">SyntaxError: invalid syntax</error></testcase>
            </testsuite></testsuites>
            """;

        var result = classifier.Classify(PythonDefinition(PythonRoot()), Run(xml, 2, "ERROR collecting tests/test_impl.py\nE   SyntaxError: invalid syntax"));

        Assert.Equal(ExerciseExecutionStatus.CompilationFailure, result.Status);
    }

    [Fact]
    public void Classifier_PythonFailures_AreTestFailures_AndParametrizedCasesMapToEvidence()
    {
        var classifier = new ExerciseExecutionClassifier(new SurefireResultParser());
        const string xml = """
            <testsuites><testsuite name="pytest" errors="0" failures="1" tests="3">
              <testcase classname="tests.test_impl" name="test_adds" time="0.01" />
              <testcase classname="tests.test_impl" name="test_rejects[negative]" time="0.01"><failure message="AssertionError: expected ValueError">trace</failure></testcase>
              <testcase classname="tests.test_impl" name="test_rejects[zero]" time="0.01" />
            </testsuite></testsuites>
            """;

        var result = classifier.Classify(PythonDefinition(PythonRoot()), Run(xml, 1));

        Assert.Equal(ExerciseExecutionStatus.TestFailure, result.Status);
        var failed = result.SurefireResult!.Tests.Single(t => t.Status == "failed");
        Assert.Equal("rejects[negative]", failed.EvidenceId);
        Assert.Equal("Rejects bad input [negative]", failed.Label);
        Assert.Contains("expected ValueError", failed.Message);
    }

    [Fact]
    public void Classifier_AllPassing_IsSuccess_AndMissingReportWithSyntaxError_IsCompilationFailure()
    {
        var classifier = new ExerciseExecutionClassifier(new SurefireResultParser());
        const string xml = """
            <testsuites><testsuite tests="2"><testcase name="test_adds" /><testcase name="test_rejects" /></testsuite></testsuites>
            """;

        Assert.Equal(ExerciseExecutionStatus.Success, classifier.Classify(PythonDefinition(PythonRoot()), Run(xml, 0)).Status);
        Assert.Equal(ExerciseExecutionStatus.CompilationFailure,
            classifier.Classify(PythonDefinition(PythonRoot()), Run(null, 2, "  File \"pkg/impl.py\", line 3\nIndentationError: unexpected indent")).Status);
        Assert.Throws<ExerciseInfrastructureException>(() => classifier.Classify(PythonDefinition(PythonRoot()), Run(null, 1, "something odd")));
    }

    [Fact]
    public async Task ProgressService_RecordsRuns_RestoresDraft_AndAutoSolvesOnSuccess()
    {
        using var db = new StudyTrackerContext(new DbContextOptionsBuilder<StudyTrackerContext>()
            .UseInMemoryDatabase($"exercise-progress-{Guid.NewGuid()}").Options);
        var user = new AppUser { Email = "learner@example.com", PasswordHash = "h", PasswordSalt = "s", Status = "Approved" };
        db.Users.Add(user);
        var course = new Course { Slug = "python-engineering", Title = "P", Description = "d" };
        db.Courses.Add(course);
        db.SaveChanges();
        var module = new CourseModule { CourseId = course.Id, Slug = "m", Title = "M", Description = "d", Badge = "M" };
        db.Modules.Add(module);
        db.SaveChanges();
        var lesson = new Lesson { ModuleId = module.Id, Slug = "py-01", Title = "L" };
        db.Lessons.Add(lesson);
        db.SaveChanges();
        var problem = new Problem { LessonId = lesson.Id, Slug = "py-test-exercise", Title = "P", Language = "python" };
        db.Problems.Add(problem);
        db.SaveChanges();

        var learner = new LearnerProgressService(db, NullLogger<LearnerProgressService>.Instance);
        var service = new ExerciseProgressService(db, learner, NullLogger<ExerciseProgressService>.Instance);
        var request = new ExerciseSubmissionRequest(new List<ExerciseFileSubmission> { new("pkg/impl.py", "def add(a, b): return a - b") });

        ExerciseExecutionResponse Response(bool passed, int ok) => new(
            "run", "py-test-exercise", passed ? "success" : "testFailure", passed, 120,
            new ExerciseTestSummaryDto(2, ok, 2 - ok, 0, 0),
            new List<ExerciseEvidenceResultDto>
            {
                new("adds", "Adds numbers", ok >= 1 ? "passed" : "failed", 5, null),
                new("rejects", "Rejects bad input", ok >= 2 ? "passed" : "failed", 5, "boom")
            },
            new ExerciseDiagnosticsDto(null, null));

        await service.RecordRunAsync(user.Id, "py-test-exercise", request, Response(false, 1));
        var afterFail = await service.GetStateAsync(user.Id, "py-test-exercise");
        Assert.Equal(1, afterFail.AttemptCount);
        Assert.False(afterFail.Solved);
        Assert.Equal("def add(a, b): return a - b", afterFail.DraftFiles.Single().Content);
        Assert.DoesNotContain(problem.Id, await learner.GetSolvedProblemIdsAsync(user.Id));

        await service.SaveDraftAsync(user.Id, "py-test-exercise", new[] { new ExerciseDraftFileDto("pkg/impl.py", "def add(a, b): return a + b") });
        Assert.Contains("a + b", (await service.GetStateAsync(user.Id, "py-test-exercise")).DraftFiles.Single().Content);

        await service.RecordRunAsync(user.Id, "py-test-exercise", request, Response(true, 2));
        var afterPass = await service.GetStateAsync(user.Id, "py-test-exercise");
        Assert.True(afterPass.Solved);
        Assert.Equal(2, afterPass.AttemptCount);
        Assert.Equal("success", afterPass.BestAttempt!.Status);
        Assert.Contains(problem.Id, await learner.GetSolvedProblemIdsAsync(user.Id));
        Assert.Contains(await learner.GetActivityAsync(user.Id, 20, null), e => e.EventType == "ExerciseRun");
    }
}
