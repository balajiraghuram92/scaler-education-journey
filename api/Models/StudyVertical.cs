namespace StudyTracker.Api.Models;

public class StudyVertical
{
    public int Id { get; set; }
    public string Name { get; set; } = string.Empty;
    public string Description { get; set; } = string.Empty;

    public ICollection<StudyTask> Tasks { get; set; } = new List<StudyTask>();
}
