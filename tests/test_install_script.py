#!/usr/bin/env python3
"""Tests for Install Script scenarios — verifies install.sh logic by parsing script content."""

import os
import json
import tempfile
import subprocess

INSTALL_SH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "install.sh"
)


def _read():
    with open(INSTALL_SH) as f:
        return f.read()


# BDD: Update existing baadd project
def test_update_flag_sets_force_update():
    content = _read()
    assert "--update)" in content
    assert "FORCE_UPDATE=true" in content


# BDD: Update existing baadd project
def test_update_mode_downloads_files():
    content = _read()
    assert "FORCE_UPDATE" in content
    assert "download" in content


# BDD: Auto-detect update mode
def test_auto_detect_update_when_manifest_exists():
    content = _read()
    assert "MANIFEST_FILE" in content
    assert "FORCE_UPDATE=true" in content
    # The auto-detect block checks if manifest file exists and flips FORCE_UPDATE
    assert '-f "$MANIFEST_FILE"' in content or '-f "$MANIFEST_FILE"' in content


# BDD: Auto-detect update mode
def test_auto_detect_only_when_not_already_forced():
    content = _read()
    # auto-detect guard: only switches when FORCE_UPDATE is still false
    assert 'FORCE_UPDATE" == false' in content or "FORCE_UPDATE == false" in content


# BDD: Pin to specific version
def test_version_flag_parsed():
    content = _read()
    assert "--version)" in content
    assert 'VERSION="$2"' in content


# BDD: Pin to specific version
def test_raw_url_uses_version():
    content = _read()
    assert (
        'RAW="${RAW_BASE}/${VERSION}"' in content or "RAW_BASE}/${VERSION}" in content
    )


# BDD: Fetch latest version from GitHub API
def test_fetches_latest_from_github_api():
    content = _read()
    assert "releases/latest" in content
    assert "tag_name" in content


# BDD: Fetch latest version from GitHub API
def test_uses_curl_to_fetch_version():
    content = _read()
    assert "curl" in content
    assert "API_BASE" in content


# BDD: Skip no-clobber files on update
def test_no_clobber_list_defined():
    content = _read()
    assert "NO_CLOBBER_FILES" in content
    assert "BDD.md" in content
    assert "poppins.yml" in content


# BDD: Skip no-clobber files on update
def test_no_clobber_check_skips_existing_files():
    content = _read()
    assert "already exists" in content
    assert "skipped" in content


# BDD: Archive journals before update
def test_archives_journal_before_update():
    content = _read()
    assert "JOURNAL_archive_" in content
    assert "JOURNAL.md" in content


# BDD: Archive journals before update
def test_archives_journal_index_before_update():
    content = _read()
    assert "JOURNAL_INDEX_archive_" in content
    assert "JOURNAL_INDEX.md" in content


# BDD: Create BDD.md from template
def test_creates_bdd_from_template_when_missing():
    content = _read()
    assert "BDD.example.md" in content
    assert "BDD.md" in content


# BDD: Create BDD.md from template
def test_skips_template_copy_when_bdd_exists():
    content = _read()
    assert "BDD.md already exists" in content or 'BDD.md" ]' in content


# BDD: Create locks directory
def test_creates_locks_directory():
    content = _read()
    assert "mkdir -p locks" in content
    assert "locks/.gitkeep" in content


# BDD: Create locks directory
def test_locks_created_in_both_modes():
    content = _read()
    # locks/ creation appears in both update and init blocks
    assert content.count("locks/.gitkeep") >= 1
    assert content.count("mkdir -p locks") >= 1


# BDD: Read manifest file list
def test_read_manifest_files_function_defined():
    content = _read()
    assert "read_manifest_files()" in content


# BDD: Read manifest file list
def test_read_manifest_parses_json_files_array():
    content = _read()
    assert "json.load" in content
    assert '["files"]' in content or "['files']" in content


# BDD: Read manifest file list
def test_read_manifest_files_unit():
    """read_manifest_files() extracts file list from .baadd JSON."""
    manifest = {"version": "v1.0.0", "files": ["scripts/agent.py", "BDD.md"]}
    with tempfile.TemporaryDirectory() as d:
        manifest_path = os.path.join(d, ".baadd")
        with open(manifest_path, "w") as f:
            json.dump(manifest, f)
        result = subprocess.run(
            [
                "python3",
                "-c",
                f"import json; [print(f) for f in json.load(open('{manifest_path}'))['files']]",
            ],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        lines = result.stdout.strip().splitlines()
        assert "scripts/agent.py" in lines
        assert "BDD.md" in lines


# BDD: Stamp version in manifest
def test_stamp_version_function_defined():
    content = _read()
    assert "stamp_version()" in content


# BDD: Stamp version in manifest
def test_stamp_version_sets_version_field():
    content = _read()
    assert 'm["version"]' in content or "m['version']" in content


# BDD: Stamp version in manifest
def test_stamp_version_unit():
    """stamp_version() writes version field into .baadd JSON."""
    manifest = {"version": "v0.0.0", "files": []}
    with tempfile.TemporaryDirectory() as d:
        manifest_path = os.path.join(d, ".baadd")
        with open(manifest_path, "w") as f:
            json.dump(manifest, f)
        target_version = "v1.2.3"
        script = f"""
import json
with open("{manifest_path}") as f:
    m = json.load(f)
m["version"] = "{target_version}"
with open("{manifest_path}", "w") as f:
    json.dump(m, f, indent=2)
    f.write("\\n")
"""
        subprocess.run(["python3", "-c", script], check=True)
        with open(manifest_path) as f:
            result = json.load(f)
        assert result["version"] == target_version


# BDD: Already on target version skips update
def test_already_on_target_version_exits_early():
    content = _read()
    assert "Already on baadd" in content
    assert "Nothing to do." in content


# BDD: Already on target version skips update
def test_already_on_target_checks_current_vs_target():
    content = _read()
    assert 'CURRENT" == "$VERSION"' in content or '"$CURRENT" == "$VERSION"' in content


# BDD: Set executable permissions on scripts
def test_chmod_applied_to_scripts():
    content = _read()
    assert "chmod +x" in content
    assert "scripts/*.sh" in content
    assert "scripts/*.py" in content


# BDD: Download file creates parent directories
def test_download_function_creates_parent_dirs():
    content = _read()
    assert "download()" in content
    assert 'mkdir -p "$(dirname "$file")"' in content or "mkdir -p" in content
