import re

with open("info/04-fde-curriculum-tracker.md", "r") as f:
    lines = f.readlines()

print("using StudyTracker.Api.Models;")
print("using System.Collections.Generic;")
print("")
print("namespace StudyTracker.Api.Data;")
print("{")
print("    public static class FdeSeedData")
print("    {")
print("        public static List<StudyTask> GetTasks()")
print("        {")
print("            return new List<StudyTask>")
print("            {")

current_module = "General"

for line in lines:
    line = line.strip()
    match_header = re.match(r"^##\s+(.+)$", line)
    if match_header:
        current_module = match_header.group(1).strip()
        continue
    
    match_task = re.match(r"^- \[([ xX])\]\s+(.+)$", line)
    if match_task:
        is_completed = "true" if match_task.group(1).lower() == "x" else "false"
        title = match_task.group(2).strip().replace('"', '\\"')
        print(f'                new StudyTask {{ Title = "{title}", IsCompleted = {is_completed}, Module = "{current_module}" }},')

print("            };")
print("        }")
print("    }")
print("}")
