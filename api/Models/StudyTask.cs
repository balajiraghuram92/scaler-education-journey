namespace StudyTracker.Api.Models;

public class StudyTask
{
    public int Id { get; set; }
    public int VerticalId { get; set; }
    public string Title { get; set; } = string.Empty;
    public bool IsCompleted { get; set; }

    public StudyVertical? Vertical { get; set; }
}
