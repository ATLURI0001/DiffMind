from unidiff import PatchSet
from unidiff.errors import UnidiffParseError

from pr_agent.algo.git_patch_processing import to_hunk_only_patch as _to_hunk_only_patch
from pr_agent.algo.types import EDIT_TYPE, FilePatchInfo
from pr_agent.log import get_logger


def to_hunk_only_patch(patch_str: str) -> str:
    """Keep the existing provider-layer import path for callers."""
    return _to_hunk_only_patch(patch_str)


def _strip_prefix(path: str | None) -> str | None:
    if path is None:
        return None
    if path.startswith(("a/", "b/")):
        return path[2:]
    return path


def parse_unified_diff(diff_text: str | None) -> list[FilePatchInfo]:
    """Parse a unified diff into FilePatchInfo objects (patch + metadata only).

    base_file / head_file are left empty here; the provider fills them from the
    working tree and by reverse-applying the patch. Binary files are skipped.
    """
    if not diff_text or not isinstance(diff_text, str) or not diff_text.strip():
        return []
    # Normalize CRLF/CR line endings so trailing '\r' does not corrupt filenames or fake renames
    normalized_diff = diff_text.replace("\r\n", "\n").replace("\r", "\n")
    patch_set = PatchSet(normalized_diff)
    files: list[FilePatchInfo] = []
    for pf in patch_set:
        if pf.is_binary_file:
            get_logger().info(f"Skipping binary file in diff: {pf.path}")
            continue
        if pf.is_added_file:
            edit_type = EDIT_TYPE.ADDED
        elif pf.is_removed_file:
            edit_type = EDIT_TYPE.DELETED
        elif pf.is_rename:
            edit_type = EDIT_TYPE.RENAMED
        else:
            edit_type = EDIT_TYPE.MODIFIED

        if pf.is_removed_file:  # target is /dev/null: use source path as the name
            filename = _strip_prefix(pf.source_file)
        else:
            filename = _strip_prefix(pf.target_file)
        old_filename = _strip_prefix(pf.source_file) if pf.is_rename else None

        files.append(
            FilePatchInfo(
                base_file="",
                head_file="",
                patch=str(pf),
                filename=filename,
                edit_type=edit_type,
                old_filename=old_filename,
            )
        )
    return files


def reconstruct_base_file(head_file_str: str | None, patch_str: str | None) -> str:
    """Reverse-apply a single-file unified diff to head (new) content to recover
    base (original) content. Returns "" if the patch does not cleanly apply."""
    if not isinstance(head_file_str, str) or not patch_str or not isinstance(patch_str, str) or not patch_str.strip():
        return ""
    try:
        patch_set = PatchSet(patch_str.replace("\r\n", "\n").replace("\r", "\n"))
    except UnidiffParseError as e:
        get_logger().info(f"Could not parse patch for base reconstruction: {e}")
        return ""
    if len(patch_set) != 1:
        return ""

    head_lines = head_file_str.splitlines()
    base_lines: list[str] = []
    head_idx = 0  # 0-based cursor into head_lines
    base_eof_no_newline = False
    head_eof_no_newline = False
    base_had_eof_line_in_last_hunk = False

    for hunk in patch_set[0]:
        # Track EOF newline state only for the final hunk if it covers EOF.
        base_eof_no_newline = False
        head_eof_no_newline = False
        base_had_eof_line_in_last_hunk = False
        last_op: str | None = None

        # 1-based -> 0-based. A hunk with no head lines (a pure deletion, as in
        # `git diff -U0`, or a file emptied of all lines) numbers the line *before*
        # the change instead, so its start already is the 0-based insertion point.
        hunk_head_start = hunk.target_start if hunk.target_length == 0 else hunk.target_start - 1
        if hunk_head_start < head_idx or hunk_head_start > len(head_lines):
            return ""  # out-of-order / out-of-bounds hunk
        base_lines.extend(head_lines[head_idx:hunk_head_start])
        head_idx = hunk_head_start

        for line in hunk:
            if line.line_type == "\\":
                if last_op in ("-", " "):
                    base_eof_no_newline = True
                elif last_op == "+":
                    head_eof_no_newline = True
                continue
            value = line.value.rstrip("\r\n")
            if line.is_context:
                if head_idx >= len(head_lines) or head_lines[head_idx] != value:
                    return ""
                base_lines.append(head_lines[head_idx])
                head_idx += 1
                last_op = " "
                base_had_eof_line_in_last_hunk = True
            elif line.is_added:  # present only in head: verify + skip
                if head_idx >= len(head_lines) or head_lines[head_idx] != value:
                    return ""
                head_idx += 1
                last_op = "+"
            elif line.is_removed:  # present only in base: emit, don't consume head
                base_lines.append(value)
                last_op = "-"
                base_had_eof_line_in_last_hunk = True

    trailing_head_untouched = head_idx < len(head_lines)
    base_lines.extend(head_lines[head_idx:])
    # Preserve a trailing newline only when the base actually has content; an
    # empty base (e.g. reversing an add-file patch) must stay "" so downstream
    # extend_patch() correctly treats it as having no original file.
    if not base_lines:
        return ""
    result = "\n".join(base_lines)
    if trailing_head_untouched:
        has_trailing_nl = head_file_str.endswith("\n")
    elif base_eof_no_newline:
        has_trailing_nl = False
    elif head_eof_no_newline and base_had_eof_line_in_last_hunk:
        has_trailing_nl = True
    else:
        has_trailing_nl = head_file_str.endswith("\n")
    if has_trailing_nl:
        result += "\n"
    return result
