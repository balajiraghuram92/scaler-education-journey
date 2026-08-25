using StudyTracker.Api.Services.Exercises;
using Xunit;

namespace StudyTracker.Api.Tests.Exercises;

public class ExerciseExecutionClassifierTests
{
    [Fact]
    public void Classifier_ReturnsTestFailureWhenSurefireReportsFailure()
    {
        var classifier = new ExerciseExecutionClassifier(new SurefireResultParser());
        var result = classifier.Classify(
            ExerciseTestFactory.CreateDefinition("C:\\exercise"),
            new RunnerExecutionResult
            {
                RunId = Guid.NewGuid(),
                ExitCode = 1,
                SurefireXml = "<testsuite><testcase name=\"testOne\"><failure message=\"bad\" /></testcase></testsuite>"
            });

        Assert.Equal(ExerciseExecutionStatus.TestFailure, result.Status);
    }

    [Fact]
    public void Classifier_ReturnsCompilationFailureFromCompilerDiagnosticsWithoutSurefire()
    {
        var classifier = new ExerciseExecutionClassifier(new SurefireResultParser());
        var result = classifier.Classify(
            ExerciseTestFactory.CreateDefinition("C:\\exercise"),
            new RunnerExecutionResult
            {
                RunId = Guid.NewGuid(),
                ExitCode = 1,
                StandardError = "[ERROR] COMPILATION ERROR"
            });

        Assert.Equal(ExerciseExecutionStatus.CompilationFailure, result.Status);
    }

    [Fact]
    public void Classifier_ReturnsTimeoutBeforeLookingForReports()
    {
        var classifier = new ExerciseExecutionClassifier(new SurefireResultParser());
        var result = classifier.Classify(
            ExerciseTestFactory.CreateDefinition("C:\\exercise"),
            new RunnerExecutionResult
            {
                RunId = Guid.NewGuid(),
                ExitCode = 137,
                TimedOut = true
            });

        Assert.Equal(ExerciseExecutionStatus.Timeout, result.Status);
    }

    [Fact]
    public void Classifier_ThrowsInfrastructureFailureWhenNoAuthoritativeResultExists()
    {
        var classifier = new ExerciseExecutionClassifier(new SurefireResultParser());

        Assert.Throws<ExerciseInfrastructureException>(() => classifier.Classify(
            ExerciseTestFactory.CreateDefinition("C:\\exercise"),
            new RunnerExecutionResult
            {
                RunId = Guid.NewGuid(),
                ExitCode = 1,
                StandardError = "network unavailable"
            }));
    }
}
