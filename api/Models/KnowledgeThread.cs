using System;
using System.ComponentModel.DataAnnotations.Schema;

namespace StudyTracker.Api.Models;

[Table("knowledge_threads")]
public class KnowledgeThread
{
    public int Id { get; set; }
    public string Domain { get; set; } = string.Empty; // Java, Backend, Cloud
    public string RawPath { get; set; } = string.Empty; // Java → concurrency → virtual threads → structured concurrency
    public int OrderIndex { get; set; }
}
