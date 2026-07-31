# Troubleshooting

## Skill Not Loading

Verify the canonical skill exists:

```bash
codex plugin list --json
```

Confirm `ctk-codex-seo@ctk-advisors` is enabled, then start a new Codex thread.

## Runtime Not Ready

```bash
python scripts/bootstrap_environment.py --json
```

If Playwright Chromium fails, core workflows can still run. Visual and PDF workflows remain limited until browser installation succeeds.

The bootstrap accepts binary wheels only and verifies hashes from
`requirements/core.txt`. Use the returned `python` path for subsequent commands.
Optional visual, Google API, report, and OCR packages require an explicit,
separately reviewed installation.

## Credentials Missing

Use Codex paths for new setup:

- Google: `~/.config/ctk-codex-seo/google-api.json`
- Backlinks: `~/.config/ctk-codex-seo/backlinks-api.json`
- DataForSEO budgets: `~/.config/ctk-codex-seo/dataforseo-costs.json`

Legacy `~/.config/claude-seo/` files are read as fallback only.

## Headless Workflow Fails

Run a narrow workflow first:

```bash
python scripts/run_skill_workflow.py --skill ctk-seo-technical https://example.com --json
```

For optional MCP/API workflows, `setup_required` is a valid result when credentials or MCP servers are absent.

## Reinstall

```bash
git clone https://github.com/ctkadvisors/codex-seo.git
cd codex-seo
./install.sh
```
