"""System.Text.Json-compatible dumps for values stored in the database.

C# JsonSerializer.Serialize with default options writes compact JSON (no spaces),
\\uXXXX escapes for non-ASCII, and \\u003C/\\u003E/\\u0026 for <>&. MetadataJson,
FilesJson, SummaryJson and DetailsJson columns must match byte-for-byte, so every
such call site uses this helper instead of plain json.dumps.
"""

from __future__ import annotations

import json


def dumps(obj: object) -> str:
    payload = json.dumps(obj, separators=(",", ":"), ensure_ascii=True)
    return (
        payload.replace("<", "\\u003C")
        .replace(">", "\\u003E")
        .replace("&", "\\u0026")
    )
