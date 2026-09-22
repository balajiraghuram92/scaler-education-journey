namespace StudyTracker.Api.Options;

public sealed class ExerciseExecutionOptions
{
    public const string SectionName = "ExerciseExecution";

    public string ExercisesRoot { get; set; } = string.Empty;

    public string WorkspaceRoot { get; set; } = string.Empty;

    public string RunnerImage { get; set; } = "neuralascent-java-runner:dev";

    public Dictionary<string, string> RunnerImagesByProfile { get; set; } = new(StringComparer.OrdinalIgnoreCase);

    public string DockerEndpoint { get; set; } = "unix:///var/run/docker.sock";

    public string MavenCacheVolume { get; set; } = "neuralascent-maven-cache";

    public int MaxConcurrentExecutions { get; set; } = 2;

    public int MaxFileBytes { get; set; } = 131_072;

    public int MaxSubmissionBytes { get; set; } = 262_144;

    public int MaxOutputBytes { get; set; } = 65_536;

    public int MaxExecutionSeconds { get; set; } = 240;

    public int ExecutionStartupGraceSeconds { get; set; } = 15;

    public long MemoryLimitBytes { get; set; } = 1_610_612_736;

    public long NanoCpus { get; set; } = 1_000_000_000;

    public long PidsLimit { get; set; } = 128;

    public int ContainerCleanupGraceSeconds { get; set; } = 5;
}
