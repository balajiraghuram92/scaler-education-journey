using Microsoft.Extensions.Options;
using StudyTracker.Api.Models;
using StudyTracker.Api.Services.Exercises;
using Xunit;

namespace StudyTracker.Api.Tests.Exercises;

public class ExerciseSubmissionValidatorTests
{
    [Fact]
    public void Validator_AcceptsExactlyTheEditableManifestFiles()
    {
        var definition = ExerciseTestFactory.CreateDefinition("C:\\exercise");
        var validator = new ExerciseSubmissionValidator(Microsoft.Extensions.Options.Options.Create(ExerciseTestFactory.Options()));

        var submitted = validator.Validate(definition, ExerciseTestFactory.ValidSubmission());

        Assert.Equal(2, submitted.Count);
    }

    [Theory]
    [InlineData("pom.xml")]
    [InlineData("tests/src/test/java/TrustedTest.java")]
    [InlineData("../pom.xml")]
    [InlineData("src/main/java/Unknown.java")]
    public void Validator_RejectsTrustedOrUnsafePaths(string path)
    {
        var definition = ExerciseTestFactory.CreateDefinition("C:\\exercise");
        var validator = new ExerciseSubmissionValidator(Microsoft.Extensions.Options.Options.Create(ExerciseTestFactory.Options()));
        var request = new ExerciseSubmissionRequest(new List<ExerciseFileSubmission>
        {
            new(path, "not allowed"),
            new("src/main/java/Two.java", "class Two {}")
        });

        Assert.Throws<ExerciseSubmissionValidationException>((Action)(() => validator.Validate(definition, request)));
    }

    [Fact]
    public void Validator_RejectsMissingEditableFile()
    {
        var definition = ExerciseTestFactory.CreateDefinition("C:\\exercise");
        var validator = new ExerciseSubmissionValidator(Microsoft.Extensions.Options.Options.Create(ExerciseTestFactory.Options()));
        var request = new ExerciseSubmissionRequest(new List<ExerciseFileSubmission>
        {
            new("src/main/java/One.java", "class One {}")
        });

        var exception = Assert.Throws<ExerciseSubmissionValidationException>((Action)(() => validator.Validate(definition, request)));

        Assert.Contains(exception.Errors, error => error.Contains("Two.java", StringComparison.Ordinal));
    }
}
