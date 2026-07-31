from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL_NAME = re.compile(r"^name:\s*(\S+)\s*$", re.MULTILINE)


def test_plugin_identity_is_ctk_namespaced() -> None:
    manifest = json.loads((ROOT / ".codex-plugin" / "plugin.json").read_text())
    assert manifest["name"] == "ctk-codex-seo"
    assert manifest["author"]["name"] == "CTK Advisors"
    assert manifest["repository"] == "https://github.com/ctkadvisors/codex-seo"


def test_all_skill_and_agent_resources_are_ctk_namespaced() -> None:
    skill_dirs = sorted(path for path in (ROOT / "skills").iterdir() if path.is_dir())
    assert len(skill_dirs) >= 20
    for skill_dir in skill_dirs:
        assert skill_dir.name.startswith("ctk-seo")
        skill_text = (skill_dir / "SKILL.md").read_text()
        match = SKILL_NAME.search(skill_text)
        assert match, f"missing skill name in {skill_dir}"
        assert match.group(1) == skill_dir.name

    agents = sorted((ROOT / "agents").glob("*.toml"))
    assert agents
    assert all(agent.name.startswith("ctk-seo-") for agent in agents)


def test_runtime_routing_has_no_unprefixed_specialist_keys() -> None:
    workflow = (ROOT / "scripts" / "run_skill_workflow.py").read_text()
    unprefixed = re.findall(r"""["'](seo(?:-[a-z0-9-]+)?)["']""", workflow)
    assert unprefixed == []
