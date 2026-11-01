using System;

namespace StudyTracker.Api.Data;

/// <summary>
/// Seeds the Python Engineering course from files under Data/Content/python.
/// The file format and update rules are described on <see cref="ContentCurriculumSeedData"/>.
/// </summary>
public static class PythonCurriculumSeedData
{
    public static void Seed(StudyTrackerContext db, string? contentRoot = null)
    {
        var root = contentRoot ?? ResolveContentRoot();
        if (root == null)
        {
            Console.WriteLine("[WARN] Python curriculum content folder (Data/Content/python) was not found. Skipping Python seeding.");
            return;
        }

        ContentCurriculumSeedData.Seed(db, root);
    }

    public static string? ResolveContentRoot() => ContentCurriculumSeedData.ResolveContentRoot("python");
}
