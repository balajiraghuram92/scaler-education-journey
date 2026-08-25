using StudyTracker.Api.Services.Exercises;
using Xunit;

namespace StudyTracker.Api.Tests.Exercises;

public class SurefireResultParserTests
{
    [Fact]
    public void Parser_UsesSurefireAndMapsMethodsToStableEvidence()
    {
        var definition = ExerciseTestFactory.CreateDefinition("C:\\exercise");
        var parser = new SurefireResultParser();
        var xml = """
                  <testsuite name="TrustedTest" tests="2" failures="1" errors="0" skipped="0">
                    <testcase name="testOne" classname="TrustedTest" time="0.010" />
                    <testcase name="testTwo" classname="TrustedTest" time="0.020">
                      <failure message="expected value">stack</failure>
                    </testcase>
                  </testsuite>
                  """;

        var result = parser.Parse(xml, definition);

        Assert.Equal(2, result.Total);
        Assert.Equal(1, result.Passed);
        Assert.Equal(1, result.Failed);
        Assert.Equal("one-evidence", result.Tests[0].EvidenceId);
        Assert.Equal("two-evidence", result.Tests[1].EvidenceId);
        Assert.Equal("failed", result.Tests[1].Status);
    }

    [Fact]
    public void Parser_RejectsXmlWithoutTestCases()
    {
        var definition = ExerciseTestFactory.CreateDefinition("C:\\exercise");
        var parser = new SurefireResultParser();

        Assert.Throws<ExerciseInfrastructureException>(() => parser.Parse("<testsuite />", definition));
    }
}
