# CTK Codex SEO Hardening Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Publish a namespaced CTK Codex SEO release whose installer, runtime, credentials, network access, updates, and uninstaller cannot overwrite unrelated state or exfiltrate local data.

**Architecture:** The fork becomes the `ctk-codex-seo` plugin and installs as one self-contained plugin directory through a transaction module that owns every written path through a signed-content manifest. Shared security modules enforce public-only crawling, provider-origin allowlists, secret redaction, restrictive credential permissions, and read-only defaults; CI blocks direct network bypasses and destructive installer regressions.

**Tech Stack:** Python 3.10+, Bash, Codex plugin/skill manifests, pytest, GitHub Actions, pip-tools/pip hash locks, CodeQL.

---

## File Structure

- `.codex-plugin/plugin.json` — CTK plugin identity and capability declaration.
- `scripts/ctk_install.py` — collision preflight, staging, atomic activation, ownership manifest, rollback, and uninstall.
- `install.sh`, `uninstall.sh` — thin argument-forwarding wrappers with no destructive logic.
- `scripts/security_paths.py` — safe root/path/symlink validation and restrictive atomic file writes.
- `scripts/security_network.py` — public crawler and fixed-origin provider clients.
- `scripts/security_redaction.py` — secret registration and diagnostic redaction.
- `scripts/google_auth.py` — Search Console read-only authentication using the security primitives.
- `scripts/seo_pipeline_utils.py` — consumes the shared network policy rather than maintaining a second policy.
- `scripts/migrate_namespace.py` — deterministic repository-only migration helper.
- `tests/test_ctk_installer.py` — transaction, collision, rollback, update, and uninstall ownership tests.
- `tests/test_ctk_credentials.py` — permission, scope, atomicity, and redaction tests.
- `tests/test_ctk_network.py` — SSRF, redirect, DNS-rebinding, provider-origin, and size-limit tests.
- `tests/test_ctk_namespace.py` — plugin, skills, agents, and references are fully namespaced.
- `tests/test_ctk_repo_immutability.py` — audit commands cannot mutate a target repository implicitly.
- `tests/test_ctk_static_policy.py` — prevents direct network clients, shell execution, and credential discovery.
- `.github/workflows/security.yml` — tests, CodeQL, dependency and secret checks.
- `requirements/*.in`, `requirements/*.txt` — profile-specific direct requirements and hashed locks.
- `SECURITY.md`, `docs/INSTALLATION.md`, `docs/THREAT-MODEL.md`, `docs/UPSTREAM.md` — operational contract.

### Task 1: Establish CTK Identity and Complete Namespacing

**Files:**
- Modify: `.codex-plugin/plugin.json`
- Modify: `skills/*/SKILL.md`
- Move: `skills/seo*` to `skills/ctk-seo*`
- Move: `agents/seo-*.toml` to `agents/ctk-seo-*.toml`
- Create: `scripts/migrate_namespace.py`
- Create: `tests/test_ctk_namespace.py`
- Modify: `README.md`

- [ ] **Step 1: Write failing namespace tests**

Test that the plugin name is `ctk-codex-seo`, every skill directory and
frontmatter name starts with `ctk-seo`, every agent filename starts with
`ctk-seo-`, and repository text contains no live routing reference to an
unprefixed specialist.

```python
def test_all_installed_resources_are_namespaced(repo_root):
    manifest = json.loads((repo_root / ".codex-plugin/plugin.json").read_text())
    assert manifest["name"] == "ctk-codex-seo"
    for skill in (repo_root / "skills").iterdir():
        assert skill.name.startswith("ctk-seo")
        assert f"name: {skill.name}" in (skill / "SKILL.md").read_text()
    assert all(p.name.startswith("ctk-seo-") for p in (repo_root / "agents").glob("*.toml"))
```

- [ ] **Step 2: Run the test and confirm it fails**

Run: `python -m pytest tests/test_ctk_namespace.py -q`
Expected: failures naming the upstream `ctk-seo` resources.

- [ ] **Step 3: Add deterministic namespace migration**

Implement a repository migration that maps `ctk-seo` to `ctk-seo` and
`seo-*` to `ctk-seo-*`, rewrites skill frontmatter, agent references, command
examples, script routing tables, plugin metadata, and test fixtures. It must
reject a dirty worktree and support `--check`.

- [ ] **Step 4: Run migration and update documentation**

Run: `python scripts/migrate_namespace.py`
Expected: all skill/agent paths and references migrate without overwriting an
existing destination.

- [ ] **Step 5: Verify**

Run: `python -m pytest tests/test_ctk_namespace.py tests/test_codex_port_contracts.py -q`
Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add .codex-plugin skills agents scripts/migrate_namespace.py tests/test_ctk_namespace.py README.md
git commit -m "refactor: namespace CTK SEO plugin resources"
```

### Task 2: Replace Destructive Installation with Owned Transactions

**Files:**
- Create: `scripts/security_paths.py`
- Create: `scripts/ctk_install.py`
- Rewrite: `install.sh`
- Rewrite: `uninstall.sh`
- Create: `tests/test_ctk_installer.py`
- Modify: `docs/INSTALLATION.md`

- [ ] **Step 1: Write failing transaction tests**

Cover fresh install, collision-before-write, alternate `CODEX_HOME`, staged
failure rollback, update of a valid CTK-owned install, refusal to update a
missing/corrupt ownership manifest, preservation of modified owned files on
uninstall, symlink rejection, traversal rejection, and byte-for-byte
preservation of unrelated state.

```python
def test_collision_fails_without_any_persistent_write(tmp_path, source_tree):
    codex_home = tmp_path / "codex"
    foreign = codex_home / "plugins" / "ctk-codex-seo"
    foreign.mkdir(parents=True)
    (foreign / "foreign.txt").write_bytes(b"keep-me")
    before = snapshot_tree(codex_home)
    result = install(source_tree, codex_home)
    assert result.code == "collision"
    assert snapshot_tree(codex_home) == before
```

- [ ] **Step 2: Run tests and confirm failures**

Run: `python -m pytest tests/test_ctk_installer.py -q`
Expected: import errors for the new installer modules.

- [ ] **Step 3: Implement safe path primitives**

Provide `resolve_beneath(root, relative)`, `reject_symlink_components(path)`,
`atomic_write(path, data, mode)`, `hash_file(path)`, and
`snapshot_owned_tree(path)`. All functions fail closed on unexpected file
types or roots.

- [ ] **Step 4: Implement installer transaction**

`ctk_install.py install` computes the plan, validates collisions, copies to a
temporary sibling, creates `install-manifest.json` with relative paths and
SHA-256 digests, verifies the stage, rotates an existing valid CTK install to a
rollback sibling, activates with `os.replace`, verifies again, and then removes
only the rollback sibling it created.

- [ ] **Step 5: Implement ownership-aware uninstall**

`ctk_install.py uninstall` validates the manifest and removes only unchanged
owned files. Modified files produce `preserved_modified` records and a nonzero
result unless `--force-owned-modifications` is explicit. It never removes a
shared parent directory.

- [ ] **Step 6: Make shell wrappers thin**

The wrappers resolve their checked-out repository path and execute
`python3 scripts/ctk_install.py`; they contain no `rm`, glob deletion, settings
editing, remote download, or dependency installation.

- [ ] **Step 7: Verify**

Run: `python -m pytest tests/test_ctk_installer.py -q`
Expected: PASS.

- [ ] **Step 8: Commit**

```bash
git add scripts/security_paths.py scripts/ctk_install.py install.sh uninstall.sh tests/test_ctk_installer.py docs/INSTALLATION.md
git commit -m "feat: add owned transactional plugin installation"
```

### Task 3: Enforce Least-Privilege Credential Handling

**Files:**
- Create: `scripts/security_redaction.py`
- Modify: `scripts/google_auth.py`
- Modify: `scripts/gsc_query.py`
- Modify: `scripts/gsc_inspect.py`
- Modify: `skills/ctk-seo-google/SKILL.md`
- Create: `tests/test_ctk_credentials.py`

- [ ] **Step 1: Write failing credential tests**

Verify config directories are `0700`, token/config files are `0600`, writes are
atomic, default OAuth scopes equal only
`https://www.googleapis.com/auth/webmasters.readonly`, exceptions redact access
tokens/client secrets/API keys, and no secret appears beneath cache/report
roots.

- [ ] **Step 2: Run tests and confirm failures**

Run: `python -m pytest tests/test_ctk_credentials.py -q`
Expected: failures for broad scopes and permissive token writes.

- [ ] **Step 3: Add redaction and secure writes**

Implement `SecretRedactor.register(value)`, `redact(text)`, and
`safe_exception(exc)`. Use `security_paths.atomic_write(..., mode=0o600)` for
OAuth/config writes and set the containing directory to `0700`.

- [ ] **Step 4: Reduce default Google surface**

The default auth flow requests Search Console read-only only. Indexing, GA4,
Ads, and other services require separate provider-specific configuration.
Remove claims that a service account must be Search Console Owner; request only
the access level required for read operations.

- [ ] **Step 5: Verify**

Run: `python -m pytest tests/test_ctk_credentials.py tests/test_workflow_contracts.py -q`
Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add scripts/security_redaction.py scripts/google_auth.py scripts/gsc_query.py scripts/gsc_inspect.py skills/ctk-seo-google tests/test_ctk_credentials.py
git commit -m "fix: enforce least-privilege SEO credentials"
```

### Task 4: Centralize and Constrain All Network Egress

**Files:**
- Create: `scripts/security_network.py`
- Modify: `scripts/seo_pipeline_utils.py`
- Modify: network-using scripts under `scripts/`
- Create: `tests/test_ctk_network.py`
- Create: `tests/test_ctk_static_policy.py`

- [ ] **Step 1: Write failing network-policy tests**

Test loopback/private/link-local/reserved/multicast/unspecified/IPv4-mapped IPv6
rejection, userinfo and non-HTTP scheme rejection, DNS-rebinding simulation,
redirect-hop validation, browser subresource validation, provider
cross-origin redirect refusal, response-size limits, and timeout defaults.

- [ ] **Step 2: Write static bypass tests**

Parse production Python AST and fail on direct `requests.*`, `urllib.request`,
`http.client`, `socket.create_connection`, `subprocess` calls to `curl`/`wget`,
`shell=True`, or `gh auth token` outside approved security adapters.

- [ ] **Step 3: Run tests and confirm failures**

Run: `python -m pytest tests/test_ctk_network.py tests/test_ctk_static_policy.py -q`
Expected: failures listing existing bypass call sites.

- [ ] **Step 4: Implement shared clients**

Implement `PublicWebClient` with public-address validation on every resolution
and redirect, response-size/redirect/time limits, and a documented user agent.
Implement `ProviderClient(provider, credentials)` with fixed HTTPS origins,
redacted errors, and no cross-origin redirects.

- [ ] **Step 5: Migrate retained core workflows**

Move technical, content, schema, sitemap, performance, GEO, visual, Search
Console, PageSpeed, CrUX, Bing, backlink-free-source, and drift network access
through the shared clients. Disable non-migrated optional vendor workflows by
default with a structured `setup_required` response.

- [ ] **Step 6: Remove ambient credential discovery**

Delete `gh auth token` probing and reads of global Codex MCP settings from core
workflows. Provider setup accepts only explicit config or documented
environment variables.

- [ ] **Step 7: Verify**

Run: `python -m pytest tests/test_ctk_network.py tests/test_ctk_static_policy.py tests/test_security_contracts.py -q`
Expected: PASS.

- [ ] **Step 8: Commit**

```bash
git add scripts tests/test_ctk_network.py tests/test_ctk_static_policy.py
git commit -m "security: constrain SEO network egress"
```

### Task 5: Make Audits Repository-Immutable by Default

**Files:**
- Modify: `scripts/seo_pipeline_utils.py`
- Modify: `scripts/run_skill_workflow.py`
- Modify: `scripts/run_headless_audit.py`
- Modify: `scripts/drift_baseline.py`
- Modify: `scripts/drift_report.py`
- Modify: relevant `skills/ctk-seo*/SKILL.md`
- Create: `tests/test_ctk_repo_immutability.py`

- [ ] **Step 1: Write failing immutability tests**

Run core commands against a fixture Git repository and assert its complete
filesystem snapshot and `git status --porcelain=v1` are unchanged. Verify
artifacts default beneath the XDG cache/state roots and project output requires
`--output`.

- [ ] **Step 2: Run tests and confirm failures**

Run: `python -m pytest tests/test_ctk_repo_immutability.py -q`
Expected: failure where `.ctk-seo-cache` or `.gitignore` is written locally.

- [ ] **Step 3: Implement isolated storage roots**

Add deterministic site identifiers and XDG-aware cache/state helpers. Remove
automatic `.gitignore` editing. Require explicit paths for project-local
reports and a separate `--apply` mode for mutations.

- [ ] **Step 4: Update skill instructions**

Every retained skill states that audit commands are read-only, names the
default artifact location, and requires explicit user authorization before
applying changes.

- [ ] **Step 5: Verify**

Run: `python -m pytest tests/test_ctk_repo_immutability.py tests/test_workflow_contracts.py -q`
Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add scripts skills tests/test_ctk_repo_immutability.py
git commit -m "fix: keep SEO audits repository immutable"
```

### Task 6: Lock Supply Chain and Add Security CI

**Files:**
- Create: `requirements/core.in`
- Create: `requirements/core.txt`
- Create: `requirements/visual.in`
- Create: `requirements/visual.txt`
- Create: `requirements/reports.in`
- Create: `requirements/reports.txt`
- Modify: `scripts/bootstrap_environment.py`
- Create: `.github/workflows/security.yml`
- Modify: `SECURITY.md`
- Create: `docs/THREAT-MODEL.md`
- Create: `docs/UPSTREAM.md`

- [ ] **Step 1: Add lock verification test**

Test every non-comment lock entry is pinned with `==` and includes
`--hash=sha256:`. Test bootstrap uses `--require-hashes` and installs only the
requested profile.

- [ ] **Step 2: Generate profile locks**

Use `pip-compile --generate-hashes` from reviewed `.in` files. Core excludes
Chromium, OCR, report rendering, and optional vendors.

- [ ] **Step 3: Update bootstrap**

Default to `core`; add repeatable `--profile visual` and `--profile reports`.
Never install browsers or optional groups without their explicit profile.

- [ ] **Step 4: Add CI**

Run tests on macOS and Linux with supported Python versions; add CodeQL,
dependency review where available, `pip-audit`, `bandit`, secret scanning,
plugin validation, lock verification, and static policy tests. CI must not use
production credentials.

- [ ] **Step 5: Document security operations**

Document egress origins, local read/write roots, credentials, disclosure,
upstream review, and release signing/checksums. Replace all remote-shell
installation examples with clone/inspect/pinned-checkout instructions.

- [ ] **Step 6: Verify**

Run: `python -m pytest tests/test_ctk_supply_chain.py -q`
Expected: PASS.

- [ ] **Step 7: Commit**

```bash
git add requirements scripts/bootstrap_environment.py .github/workflows/security.yml SECURITY.md docs tests/test_ctk_supply_chain.py
git commit -m "build: lock dependencies and add security gates"
```

### Task 7: Full Compatibility, Adversarial Audit, and Release

**Files:**
- Modify: `README.md`
- Modify: `CHANGELOG.md`
- Create: `docs/SECURITY-AUDIT.md`
- Create: release tag and GitHub release after verification

- [ ] **Step 1: Run full tests**

Run: `python -m pytest tests/ -q`
Expected: all retained and new tests pass.

- [ ] **Step 2: Validate plugin and skills**

Run the Codex plugin validator and skill quick validator against every
`skills/ctk-seo*` directory.
Expected: all manifests and skill packages valid.

- [ ] **Step 3: Exercise isolated lifecycle**

Install into a temporary `CODEX_HOME`, run a credential-free audit against a
controlled public fixture, update the install, inject a failed update, and
uninstall. Compare unrelated-state hashes before and after.
Expected: identical unrelated-state hashes.

- [ ] **Step 4: Audit the final diff**

Review every new network call, subprocess, credential read/write, installer
path mutation, workflow permission, and dependency. Record evidence and
remaining limitations in `docs/SECURITY-AUDIT.md`.

- [ ] **Step 5: Update release documentation**

Document the core installation, read-only Search Console setup, supported
egress, optional profiles, uninstall behavior, and upstream relationship.

- [ ] **Step 6: Push and verify CI**

Push `main`, watch all checks to completion, and fix any failure before
releasing.

- [ ] **Step 7: Publish pinned CTK release**

Create a signed tag when signing is available, publish checksums/SBOM, and
create a GitHub release. Do not publish if CI or audit gates are incomplete.
