using System.ComponentModel.DataAnnotations.Schema;
using System.Linq;

namespace StudyTracker.Api.Models;

public class StudyVertical
{
    public int Id { get; set; }
    public string Name { get; set; } = string.Empty;
    public string Description { get; set; } = string.Empty;

    public ICollection<StudyTask> Tasks { get; set; } = new List<StudyTask>();

    [NotMapped]
    public string LayoutMode
    {
        get => Tasks != null && Tasks.Any(t => !string.IsNullOrEmpty(t.Module) && t.Module != "General") ? "Modular" : "Flat";
        set { }
    }
}
