using System;
using System.Collections.Generic;
using System.ComponentModel.DataAnnotations.Schema;

namespace StudyTracker.Api.Models;

[Table("knowledge_threads")]
public class KnowledgeThread
{
    [Column("Id")]
    public int Id { get; set; }

    [Column("Domain")]
    public string Domain { get; set; } = string.Empty; // Java, Backend, Cloud

    [Column("RawPath")]
    public string RawPath { get; set; } = string.Empty; // Java → concurrency → virtual threads → structured concurrency

    [Column("OrderIndex")]
    public int OrderIndex { get; set; }

    public ICollection<KnowledgeThreadStep> Steps { get; set; } = new List<KnowledgeThreadStep>();
}
