using System;
using System.Collections.Generic;
using System.Linq;
using StudyTracker.Api.Services.Reconciliation;
using Xunit;

namespace StudyTracker.Api.Tests;

public class JavaReconciliationTests
{
    [Fact]
    public void NormalizationHelper_NormalizesTextConsistently()
    {
        var text1 = "  Java   Basics: OOP Principles! ";
        var text2 = "java basics oop principles";

        Assert.Equal(text2, NormalizationHelper.NormalizeText(text1));
    }

    [Fact]
    public void NormalizationHelper_GeneratesSlugCorrectly()
    {
        var text = "Advanced Concurrency & Virtual Threads";
        var slug = NormalizationHelper.GenerateSlug(text);

        Assert.Equal("advanced-concurrency-virtual-threads", slug);
    }

    [Fact]
    public void NormalizationHelper_ComputesSha256ChecksumDeterministically()
    {
        var input = "101|Module 1|Java Foundations|true";
        var hash1 = NormalizationHelper.ComputeSha256Checksum(input);
        var hash2 = NormalizationHelper.ComputeSha256Checksum(input);

        Assert.Equal(hash1, hash2);
        Assert.Equal(64, hash1.Length);
    }

    [Fact]
    public void JavaCandidateClassification_CalculatesExpectedCounts()
    {
        var candidates = new List<MappingCandidate>
        {
            new MappingCandidate { LegacyTaskId = 1, MappingStatus = "Verified", MappingType = "Exact" },
            new MappingCandidate { LegacyTaskId = 2, MappingStatus = "Verified", MappingType = "TitleAndModule" },
            new MappingCandidate { LegacyTaskId = 3, MappingStatus = "Proposed", MappingType = "Manual" }
        };

        var verified = candidates.Count(c => c.MappingStatus == "Verified");
        var proposed = candidates.Count(c => c.MappingStatus == "Proposed");

        Assert.Equal(2, verified);
        Assert.Equal(1, proposed);
    }
}
