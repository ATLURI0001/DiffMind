import pytest

from pr_agent.algo.patch_packer import (
    PatchFile,
    map_old_line_to_new,
    pack_patches_to_budget,
    parse_unified_diff_hunks,
    score_patch_priority,
)

SAMPLE_PATCH = """@@ -10,5 +10,7 @@ def process_request():
     ctx_before = True
-    old_val = 1
+    new_val = 2
+    extra_a = 3
+    extra_b = 4
     ctx_after = True
\\ No newline at end of file
@@ -30,3 +32,2 @@ def cleanup():
     keep = True
-    drop = False
     done = True
"""


def test_parse_unified_diff_hunks_and_line_mapping():
    hunks = parse_unified_diff_hunks(SAMPLE_PATCH)
    assert len(hunks) == 2

    h1, h2 = hunks
    assert h1.old_start == 10 and h1.old_count == 5
    assert h1.new_start == 10 and h1.new_count == 7
    assert h1.section_header == "def process_request():"
    assert h1.added_count == 3 and h1.deleted_count == 1

    # Line before hunk 1 stays unchanged
    assert map_old_line_to_new(hunks, 5) == 5
    # Context line at old 10 maps to new 10
    assert map_old_line_to_new(hunks, 10) == 10
    # Deleted line at old 11 maps to None
    assert map_old_line_to_new(hunks, 11) is None
    # Context line at old 12 shifted down by +2 -> new 14
    assert map_old_line_to_new(hunks, 12) == 14
    # Line between hunk 1 and hunk 2 (old 20) shifted by +2 -> new 22
    assert map_old_line_to_new(hunks, 20) == 22
    # Deleted line in hunk 2 (old 31) maps to None
    assert map_old_line_to_new(hunks, 31) is None
    # Line after hunk 2 (old 40): net delta = (+2) + (-1) = +1 -> new 41
    assert map_old_line_to_new(hunks, 40) == 41


def test_pack_patches_prioritizes_security_and_core_over_lockfiles():
    files = [
        PatchFile("package-lock.json", "...", token_count=400, added_lines=200),
        PatchFile("src/auth/jwt_validator.py", "...", token_count=300, added_lines=40),
        PatchFile("src/core/router.py", "...", token_count=350, added_lines=50),
        PatchFile("tests/test_router.py", "...", token_count=200, added_lines=30),
        PatchFile("README.md", "...", token_count=150, added_lines=10),
    ]

    assert score_patch_priority(files[1]) > score_patch_priority(files[2]) > score_patch_priority(files[0])

    packed = pack_patches_to_budget(files, max_tokens=700)
    included_names = [item["filename"] for item in packed["included"]]
    excluded_names = [item["filename"] for item in packed["excluded"]]

    # Security (300) + Core (350) = 650 <= 700; lockfile & tests excluded
    assert included_names == ["src/auth/jwt_validator.py", "src/core/router.py"]
    assert "package-lock.json" in excluded_names
    assert packed["tokens_used"] == 650
    assert packed["utilization_pct"] == pytest.approx(92.86, abs=0.01)

    with pytest.raises(ValueError):
        pack_patches_to_budget(files, max_tokens=0)
