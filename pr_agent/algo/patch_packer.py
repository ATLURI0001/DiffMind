"""Unified diff hunk parser, line-offset mapper, and token-budgeted patch packer."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

_HUNK_HEADER_RE = re.compile(
    r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@(.*)$"
)

_LOCKFILE_PATTERNS = (
    "package-lock.json",
    "yarn.lock",
    "pnpm-lock.yaml",
    "uv.lock",
    "poetry.lock",
    "cargo.lock",
    "go.sum",
)

_SECURITY_HINTS = ("auth", "security", "crypto", "token", "secret", "rbac", "permission", "oauth", "jwt")


@dataclass(frozen=True)
class DiffLine:
    kind: str  # "add", "del", "context"
    content: str
    old_lineno: int | None
    new_lineno: int | None


@dataclass
class DiffHunk:
    old_start: int
    old_count: int
    new_start: int
    new_count: int
    section_header: str = ""
    lines: list[DiffLine] = field(default_factory=list)

    @property
    def added_count(self) -> int:
        return sum(1 for ln in self.lines if ln.kind == "add")

    @property
    def deleted_count(self) -> int:
        return sum(1 for ln in self.lines if ln.kind == "del")


@dataclass(frozen=True)
class PatchFile:
    filename: str
    patch: str
    token_count: int
    added_lines: int = 0
    deleted_lines: int = 0


def parse_unified_diff_hunks(patch_text: str) -> list[DiffHunk]:
    """Parse a Git unified diff patch into structured hunks with exact old/new line numbers."""
    if not isinstance(patch_text, str) or not patch_text.strip():
        return []

    hunks: list[DiffHunk] = []
    current: DiffHunk | None = None
    old_line = 0
    new_line = 0

    for raw_line in patch_text.splitlines():
        header_match = _HUNK_HEADER_RE.match(raw_line)
        if header_match:
            old_start = int(header_match.group(1))
            old_count = int(header_match.group(2)) if header_match.group(2) is not None else 1
            new_start = int(header_match.group(3))
            new_count = int(header_match.group(4)) if header_match.group(4) is not None else 1
            section = header_match.group(5).strip()

            current = DiffHunk(
                old_start=old_start,
                old_count=old_count,
                new_start=new_start,
                new_count=new_count,
                section_header=section,
            )
            hunks.append(current)
            old_line = old_start
            new_line = new_start
            continue

        if current is None:
            continue

        if raw_line.startswith("\\ No newline at end of file"):
            continue
        if raw_line.startswith("+"):
            current.lines.append(
                DiffLine(kind="add", content=raw_line[1:], old_lineno=None, new_lineno=new_line)
            )
            new_line += 1
        elif raw_line.startswith("-"):
            current.lines.append(
                DiffLine(kind="del", content=raw_line[1:], old_lineno=old_line, new_lineno=None)
            )
            old_line += 1
        elif raw_line.startswith(" "):
            current.lines.append(
                DiffLine(kind="context", content=raw_line[1:], old_lineno=old_line, new_lineno=new_line)
            )
            old_line += 1
            new_line += 1

    return hunks


def map_old_line_to_new(hunks: list[DiffHunk], old_line: int) -> int | None:
    """Translate a 1-based pre-patch line number to its post-patch line number.

    Returns None if the line was deleted inside a hunk.
    """
    if not isinstance(old_line, int) or old_line < 1:
        return None

    cumulative_delta = 0
    for hunk in sorted(hunks, key=lambda h: h.old_start):
        hunk_end = hunk.old_start + max(0, hunk.old_count) - 1
        if old_line < hunk.old_start:
            return old_line + cumulative_delta
        if hunk.old_count > 0 and hunk.old_start <= old_line <= hunk_end:
            for ln in hunk.lines:
                if ln.old_lineno == old_line:
                    return ln.new_lineno  # None if deleted, exact int if context
            return None
        cumulative_delta += hunk.new_count - hunk.old_count

    return old_line + cumulative_delta


def score_patch_priority(file: PatchFile) -> float:
    """Compute review priority score for a changed file based on risk surface and change density."""
    path_lower = file.filename.lower().replace("\\", "/")
    basename = path_lower.rsplit("/", 1)[-1]

    if basename in _LOCKFILE_PATTERNS or path_lower.endswith(".min.js") or path_lower.endswith(".snap"):
        tier_weight = 0.1
    elif any(hint in path_lower for hint in _SECURITY_HINTS):
        tier_weight = 3.0
    elif "/tests/" in f"/{path_lower}" or basename.startswith("test_") or basename.endswith("_test.py"):
        tier_weight = 0.8
    elif path_lower.endswith((".md", ".txt", ".rst")):
        tier_weight = 0.5
    else:
        tier_weight = 1.5

    churn = max(1, file.added_lines + file.deleted_lines)
    density = churn / max(1, file.token_count)
    return round(tier_weight * (1.0 + density), 4)


def pack_patches_to_budget(files: list[PatchFile], max_tokens: int) -> dict[str, Any]:
    """Pack highest-priority whole file patches within an LLM context token budget."""
    if not isinstance(max_tokens, int) or max_tokens <= 0:
        raise ValueError("max_tokens must be a positive integer")
    if not files:
        return {
            "included": [],
            "excluded": [],
            "tokens_used": 0,
            "max_tokens": max_tokens,
            "utilization_pct": 0.0,
        }

    ranked = sorted(
        files,
        key=lambda f: (-score_patch_priority(f), f.token_count, f.filename),
    )

    included: list[dict[str, Any]] = []
    excluded: list[dict[str, Any]] = []
    used = 0

    for f in ranked:
        tokens = max(0, int(f.token_count))
        prio = score_patch_priority(f)
        if used + tokens <= max_tokens:
            used += tokens
            included.append({"filename": f.filename, "tokens": tokens, "priority": prio})
        else:
            excluded.append({"filename": f.filename, "tokens": tokens, "priority": prio})

    return {
        "included": included,
        "excluded": excluded,
        "tokens_used": used,
        "max_tokens": max_tokens,
        "utilization_pct": round((used / max_tokens) * 100.0, 2),
    }
