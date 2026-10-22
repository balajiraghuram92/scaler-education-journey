using System.Globalization;
using System.Xml;
using System.Xml.Linq;

namespace StudyTracker.Api.Services.Exercises;

public sealed class SurefireResultParser
{
    public ParsedSurefireResult Parse(string xml, ExerciseDefinition definition)
    {
        if (string.IsNullOrWhiteSpace(xml))
        {
            throw new ExerciseInfrastructureException("Surefire XML was empty.");
        }

        try
        {
            var settings = new XmlReaderSettings
            {
                DtdProcessing = DtdProcessing.Prohibit,
                XmlResolver = null,
                MaxCharactersInDocument = 1_000_000
            };

            using var stringReader = new StringReader(xml);
            using var reader = XmlReader.Create(stringReader, settings);
            var document = XDocument.Load(reader, LoadOptions.None);
            var testCases = document
                .Descendants("testcase")
                .Select(testCase => ParseTestCase(testCase, definition))
                .ToList();

            if (testCases.Count == 0)
            {
                throw new ExerciseInfrastructureException("Surefire XML did not contain any test cases.");
            }

            return new ParsedSurefireResult
            {
                Total = testCases.Count,
                Passed = testCases.Count(test => test.Status == "passed"),
                Failed = testCases.Count(test => test.Status == "failed"),
                Errors = testCases.Count(test => test.Status == "error"),
                Skipped = testCases.Count(test => test.Status == "skipped"),
                Tests = testCases
            };
        }
        catch (ExerciseInfrastructureException)
        {
            throw;
        }
        catch (Exception ex) when (ex is XmlException or InvalidOperationException)
        {
            throw new ExerciseInfrastructureException("Surefire XML could not be parsed.", ex);
        }
    }

    private static ParsedSurefireTest ParseTestCase(XElement testCase, ExerciseDefinition definition)
    {
        var method = testCase.Attribute("name")?.Value ?? string.Empty;
        var evidence = definition.EvidenceByTestMethod.TryGetValue(method, out var mappedEvidence)
            ? mappedEvidence
            : null;

        // pytest parametrized cases are reported as "test_name[case]": map them to the
        // function's evidence and keep the case id visible in the label.
        string? caseSuffix = null;
        var bracket = method.IndexOf('[');
        if (evidence is null && bracket > 0 && method.EndsWith(']') &&
            definition.EvidenceByTestMethod.TryGetValue(method[..bracket], out var parametrizedEvidence))
        {
            evidence = parametrizedEvidence;
            caseSuffix = method[bracket..];
        }

        var failure = testCase.Element("failure");
        var error = testCase.Element("error");
        var skipped = testCase.Element("skipped");
        var status = failure is not null
            ? "failed"
            : error is not null
                ? "error"
                : skipped is not null
                    ? "skipped"
                    : "passed";
        var diagnostic = failure ?? error;

        return new ParsedSurefireTest
        {
            TestMethod = method,
            EvidenceId = evidence is null ? null : caseSuffix is null ? evidence.Id : evidence.Id + caseSuffix,
            Label = evidence is null ? null : caseSuffix is null ? evidence.Label : $"{evidence.Label} {caseSuffix}",
            Status = status,
            Duration = ParseDuration(testCase.Attribute("time")?.Value),
            Message = diagnostic is null ? null : Truncate(diagnostic.Attribute("message")?.Value ?? diagnostic.Value)
        };
    }

    private static TimeSpan ParseDuration(string? value)
    {
        return double.TryParse(value, NumberStyles.Float, CultureInfo.InvariantCulture, out var seconds) && seconds >= 0
            ? TimeSpan.FromSeconds(seconds)
            : TimeSpan.Zero;
    }

    private static string? Truncate(string? value)
    {
        if (string.IsNullOrEmpty(value) || value.Length <= 4096)
        {
            return value;
        }

        return value[..4096] + "\n[diagnostic truncated]";
    }
}
