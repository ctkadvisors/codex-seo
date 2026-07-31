<p align="center">
  <img src="screenshots/cover-image.webp" alt="Codex SEO: SEO audit skill suite for Codex" width="100%">
</p>

<h2 align="center">
  <a href="https://www.youtube.com/watch?v=39FE6_oRcYY">Watch on YouTube</a>
</h2>

# Codex SEO - SEO Audit Skill Suite for Codex

Codex-first SEO analysis suite with 1 orchestrator skill, 26 specialist workflows, 24 TOML agent profiles, MCP/API extensions, deterministic headless runners, and premium audit report generation.

[![CI](https://github.com/AgriciDaniel/codex-seo/actions/workflows/runners-ci.yml/badge.svg)](https://github.com/AgriciDaniel/codex-seo/actions/workflows/runners-ci.yml)
[![Release](https://img.shields.io/github/v/release/AgriciDaniel/codex-seo?label=Release)](https://github.com/AgriciDaniel/codex-seo/releases)
[![Codex Skill](https://img.shields.io/badge/Codex-Skill_Suite-blue)](https://github.com/openai/codex)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](pyproject.toml)
[![Workflows](https://img.shields.io/badge/SEO_Workflows-26-orange)](docs/COMMANDS.md)

Codex SEO is a Codex-native port of [`AgriciDaniel/claude-seo`](https://github.com/AgriciDaniel/claude-seo), synchronized to upstream `main` at `a9cf338` and adapted for Codex skills, Codex plugins, TOML agents, shared cache artifacts, and repeatable local/API execution.

It covers technical SEO, on-page analysis, content quality, E-E-A-T, schema markup, image optimization, sitemap architecture, Core Web Vitals, GEO/AEO for AI search, backlinks, local SEO, maps intelligence, Google APIs, semantic clustering, SXO, drift monitoring, e-commerce SEO, hreflang, FLOW prompts, DataForSEO, Firecrawl, and Gemini/nanobanana image workflows.

## Contents

- [Status](#status)
- [Install](#install)
- [Quick Start](#quick-start)
- [Visual Overview](#visual-overview)
- [Commands](#commands)
- [Features](#features)
- [Extensions](#extensions)
- [Headless/API Usage](#headlessapi-usage)
- [Architecture](#architecture)
- [Verification](#verification)
- [Requirements](#requirements)
- [Credentials And Cache](#credentials-and-cache)
- [Security](#security)
- [Uninstall](#uninstall)
- [Contributing](#contributing)
- [Related Projects](#related-projects)
- [Credits](#credits)
- [Attribution](#attribution)

## Status

- Repository visibility: public.
- Hardened fork: [`ctkadvisors/codex-seo`](https://github.com/ctkadvisors/codex-seo).
- Latest local validation: 76 tests passing.
- Runtime credentials stay outside the repo under Codex/local config paths.
- Discovery topics: `codex`, `codex-cli`, `codex-skills`, `ctk-seo`, `ai-seo`, `ai-search`, `technical-seo`, `generative-engine-optimization`, `core-web-vitals`, `schema-markup`, `local-seo`, `ecommerce-seo`, `content-strategy`, `google-search-console`, `dataforseo`, `mcp`, `python`, `automation`, `marketing-automation`, `open-source`.

## Install

### Clone, Review, Install

```bash
git clone https://github.com/ctkadvisors/codex-seo.git
cd codex-seo
./install.sh
```

Windows:

```powershell
git clone https://github.com/ctkadvisors/codex-seo.git
cd codex-seo
.\install.ps1
```

The installer creates the owned local marketplace
`~/.codex/marketplaces/ctk-advisors`, registers it through the official Codex
CLI, and enables `ctk-codex-seo`. It does not alter shared skills, agents,
hooks, legacy settings, or unrelated plugins.

### Installer Overrides

```bash
CODEX_HOME=/alternate/codex/home ./install.sh
```

| Variable | Purpose |
|---|---|
| `CODEX_HOME` | Alternate Codex home. Defaults to `~/.codex`. |

## Quick Start

Start a new Codex thread after installation. Then ask naturally or invoke
`$ctk-seo` explicitly:

```text
Do a full SEO check on https://example.com following best practices.
```

```text
Review this page for schema, Core Web Vitals, image SEO, and AI search readiness.
```

```text
Create an SEO strategy and content roadmap for a local dental clinic.
```

Command-style prompts also work:

```text
$ctk-seo audit https://example.com
$ctk-seo technical https://example.com
$ctk-seo schema https://example.com
$ctk-seo dataforseo serp "best seo tools"
```

## Visual Overview

Codex SEO is designed as a Codex-first routing layer: the user can ask naturally, the orchestrator selects the right specialist workflow, and deterministic runners write repeatable artifacts instead of relying on invisible chat-only output.

```mermaid
%%{init: {"theme":"base","themeVariables":{"background":"#05080d","primaryColor":"#07131c","primaryTextColor":"#f5fbff","primaryBorderColor":"#00d7e6","lineColor":"#00d7e6","secondaryColor":"#06222a","tertiaryColor":"#ff9f1c","edgeLabelBackground":"#05080d","fontFamily":"Inter, ui-sans-serif, system-ui, sans-serif"}}}%%
flowchart LR
  user["User prompt<br/>natural language or /ctk-seo"] --> orchestrator["skills/ctk-seo/SKILL.md<br/>main orchestrator"]
  orchestrator --> cache["~/.cache/ctk-codex-seo<br/>shared evidence"]
  orchestrator --> skills["26 specialist<br/>SEO workflows"]
  skills --> agents["24 TOML agents<br/>parallel analysis slices"]
  skills --> scripts["scripts/<br/>deterministic runners"]
  scripts --> output["XDG state directory<br/>Markdown, JSON, HTML, PDF"]
  cache --> skills
  class user,orchestrator accent
  class cache,scripts data
  class output output
  classDef default fill:#07131c,stroke:#00d7e6,color:#f5fbff,stroke-width:1.4px
  classDef accent fill:#10151a,stroke:#ff9f1c,color:#fff7ed,stroke-width:2px
  classDef data fill:#06222a,stroke:#21e6c1,color:#ecfeff,stroke-width:1.5px
  classDef output fill:#15101a,stroke:#ff9f1c,color:#fff7ed,stroke-width:1.8px
```

## Commands

| Prompt | Purpose |
|---|---|
| `$ctk-seo audit <url>` | Full site audit with specialist routing and premium report support |
| `$ctk-seo page <url>` | Deep single-page SEO analysis |
| `$ctk-seo technical <url>` | Crawlability, indexability, security, JavaScript, CWV |
| `$ctk-seo content <url>` | E-E-A-T, helpfulness, readability, AI citation readiness |
| `$ctk-seo schema <url>` | Structured data detection, validation, and JSON-LD generation |
| `$ctk-seo images <url>` | Alt text, image weight, formats, metadata, image SERP opportunities |
| `$ctk-seo sitemap <url>` | XML sitemap discovery, quality gates, generation guidance |
| `$ctk-seo geo <url>` | AI Overviews, ChatGPT, Perplexity, llms.txt, citability |
| `$ctk-seo performance <url>` | Core Web Vitals, Lighthouse-oriented performance signals |
| `$ctk-seo visual <url>` | Screenshots, mobile rendering, above-the-fold analysis |
| `$ctk-seo plan <business-type>` | Strategic SEO roadmap and content plan |
| `$ctk-seo programmatic <url>` | Programmatic SEO risk and scale planning |
| `$ctk-seo competitor-pages <url>` | Comparison and alternatives page opportunities |
| `$ctk-seo hreflang <url>` | International SEO, locale validation, content parity |
| `$ctk-seo local <url>` | Local SEO, GBP signals, NAP, citations, reviews |
| `$ctk-seo maps <command>` | Geo-grid, GBP audit, review intelligence, local maps signals |
| `$ctk-seo google <command>` | GSC, PageSpeed, CrUX, Indexing API, GA4 workflows |
| `$ctk-seo backlinks <url>` | Backlink profile summary and source-tier detection |
| `$ctk-seo cluster <keyword>` | SERP-based topic clustering and hub-spoke planning |
| `$ctk-seo sxo <url>` | Search Experience Optimization, intent/page-type fit |
| `$ctk-seo drift baseline <url>` | Capture an SEO baseline before changes |
| `$ctk-seo drift compare <url>` | Compare current SEO signals against a baseline |
| `$ctk-seo ecommerce <url>` | Product SEO, marketplace visibility, product schema |
| `$ctk-seo flow <stage>` | FLOW framework prompts for Find, Leverage, Optimize, Win |
| `$ctk-seo dataforseo <command>` | Live SERP, keyword, backlink, content, and AI visibility data |
| `$ctk-seo firecrawl <command>` | JS-rendered crawling and site mapping via Firecrawl |
| `$ctk-seo image-gen <use-case>` | OG images, hero images, product visuals, infographics |

Full command details live in [docs/COMMANDS.md](docs/COMMANDS.md).

## Features

### Full Audit Pipeline

- Detects site/business type.
- Runs technical, content, schema, sitemap, performance, visual, GEO, image, and on-page analysis.
- Adds conditional specialists for local, maps, Google APIs, backlinks, clusters, SXO, drift, and e-commerce.
- Writes markdown reports, JSON summaries, cache artifacts, and optional premium HTML/PDF output.

```mermaid
%%{init: {"theme":"base","themeVariables":{"background":"#05080d","primaryColor":"#07131c","primaryTextColor":"#f5fbff","primaryBorderColor":"#00d7e6","lineColor":"#00d7e6","secondaryColor":"#06222a","tertiaryColor":"#ff9f1c","edgeLabelBackground":"#05080d","fontFamily":"Inter, ui-sans-serif, system-ui, sans-serif"}}}%%
flowchart TD
  request["Audit request"] --> detect["Detect site type<br/>business model and context"]
  detect --> core["Core audit specialists"]
  core --> technical["Technical"]
  core --> content["Content"]
  core --> schema["Schema"]
  core --> sitemap["Sitemap"]
  core --> geo["GEO / AI search"]
  core --> images["Images"]
  core --> performance["Performance"]
  core --> visual["Visual"]
  detect --> conditional["Conditional specialists"]
  conditional --> local["Local / Maps"]
  conditional --> backlinks["Backlinks"]
  conditional --> google["Google APIs"]
  conditional --> ecommerce["E-commerce"]
  conditional --> drift["Drift"]
  technical --> report["Unified SEO report"]
  content --> report
  schema --> report
  sitemap --> report
  geo --> report
  images --> report
  performance --> report
  visual --> report
  local --> report
  backlinks --> report
  google --> report
  ecommerce --> report
  drift --> report
  report --> artifacts["SUMMARY.json<br/>FULL-AUDIT-REPORT.md<br/>ACTION-PLAN.md<br/>optional HTML/PDF"]
  class request,detect accent
  class core,conditional data
  class report,artifacts output
  classDef default fill:#07131c,stroke:#00d7e6,color:#f5fbff,stroke-width:1.4px
  classDef accent fill:#10151a,stroke:#ff9f1c,color:#fff7ed,stroke-width:2px
  classDef data fill:#06222a,stroke:#21e6c1,color:#ecfeff,stroke-width:1.5px
  classDef output fill:#15101a,stroke:#ff9f1c,color:#fff7ed,stroke-width:1.8px
```

### Technical SEO

- Robots.txt, sitemap discovery, canonical checks, indexability, URL hygiene.
- Security headers, JavaScript rendering risk, mobile basics, IndexNow.
- Core Web Vitals with INP, LCP, CLS, FCP, TTFB, and PageSpeed/CrUX integrations where available.

### Content, GEO, And SXO

- E-E-A-T and helpful content signals.
- AI citation readiness, answer-first formatting, entity clarity, llms.txt support.
- Search experience analysis: page type, user stories, persona fit, intent mismatch.

### Structured Data

- JSON-LD extraction and validation.
- Schema recommendations for Organization, LocalBusiness, Product, Article, FAQ, Breadcrumb, and related types.
- Generated schema artifacts for downstream use.

### Local, Maps, And E-Commerce SEO

- Local SEO signals, GBP readiness, citations, reviews, NAP consistency.
- Maps intelligence via free sources and DataForSEO when configured.
- Product schema, marketplace endpoints, merchant visibility, and e-commerce template checks.

### Drift Monitoring

- Capture SEO-critical baselines.
- Compare deployments or page changes.
- Track title, meta, headings, canonical, schema, robots, links, and content deltas.

```mermaid
%%{init: {"theme":"base","themeVariables":{"background":"#05080d","primaryColor":"#07131c","primaryTextColor":"#f5fbff","primaryBorderColor":"#00d7e6","lineColor":"#00d7e6","actorBkg":"#07131c","actorBorder":"#00d7e6","actorTextColor":"#f5fbff","actorLineColor":"#21e6c1","signalColor":"#21e6c1","signalTextColor":"#f5fbff","labelBoxBkgColor":"#10151a","labelTextColor":"#f5fbff","noteBkgColor":"#10151a","noteTextColor":"#f5fbff","activationBkgColor":"#06222a","activationBorderColor":"#ff9f1c","fontFamily":"Inter, ui-sans-serif, system-ui, sans-serif"}}}%%
sequenceDiagram
  participant Before as Baseline
  participant Runner as Drift runner
  participant After as Current page
  participant Cache as ~/.cache/ctk-codex-seo
  participant Report as Drift report
  Before->>Runner: Capture titles, metas, canonicals, schema, headings
  Runner->>Cache: Store baseline snapshot
  After->>Runner: Re-check current SEO signals
  Cache->>Runner: Load prior snapshot
  Runner->>Report: Write changed, missing, and regressed signals
```

### Deterministic Runners

- `scripts/run_skill_workflow.py` standardizes output for every user-invokable workflow.
- `scripts/run_api_smoke_suite.py` runs all supported workflows in one pass.
- Setup-required workflows return structured fallback results instead of pretending live data exists.

## Extensions

| Extension | Skill | Setup | Notes |
|---|---|---|---|
| DataForSEO | `ctk-seo-dataforseo`, `ctk-seo-maps`, `ctk-seo-ecommerce`, `ctk-seo-cluster` | `./extensions/dataforseo/install.sh` | Live SERP, keyword, backlinks, on-page, content, business data, AI visibility |
| Google APIs | `ctk-seo-google`, `ctk-seo-performance` | `python scripts/google_auth.py --setup` | PageSpeed, CrUX, GSC, URL Inspection, Indexing API, GA4 |
| Firecrawl | `ctk-seo-firecrawl` | `./extensions/firecrawl/install.sh` | JS-rendered crawl, scrape, site map |
| Banana / Gemini | `ctk-seo-image-gen` | `./extensions/banana/install.sh` | AI image generation through `nanobanana-mcp` |

Optional integrations enrich the same workflow surface. If credentials or MCP servers are missing, wrappers return `setup_required` or `mcp_configured` states with no fabricated live data.

```mermaid
%%{init: {"theme":"base","themeVariables":{"background":"#05080d","primaryColor":"#07131c","primaryTextColor":"#f5fbff","primaryBorderColor":"#00d7e6","lineColor":"#00d7e6","secondaryColor":"#06222a","tertiaryColor":"#ff9f1c","edgeLabelBackground":"#05080d","fontFamily":"Inter, ui-sans-serif, system-ui, sans-serif"}}}%%
flowchart LR
  codex["Codex SEO workflows"] --> local["Local evidence<br/>HTML, robots, sitemaps, screenshots"]
  codex --> dfs["DataForSEO MCP<br/>SERP, keywords, backlinks, maps"]
  codex --> google["Google APIs<br/>GSC, PageSpeed, CrUX, GA4"]
  codex --> firecrawl["Firecrawl MCP<br/>JS crawl and site maps"]
  codex --> banana["Gemini / nanobanana<br/>SEO image assets"]
  local --> artifacts["Reports and ~/.cache/ctk-codex-seo"]
  dfs --> artifacts
  google --> artifacts
  firecrawl --> artifacts
  banana --> artifacts
  class codex accent
  class local,dfs,google,firecrawl,banana data
  class artifacts output
  classDef default fill:#07131c,stroke:#00d7e6,color:#f5fbff,stroke-width:1.4px
  classDef accent fill:#10151a,stroke:#ff9f1c,color:#fff7ed,stroke-width:2px
  classDef data fill:#06222a,stroke:#21e6c1,color:#ecfeff,stroke-width:1.5px
  classDef output fill:#15101a,stroke:#ff9f1c,color:#fff7ed,stroke-width:1.8px
```

Demo readiness:

```bash
python scripts/demo_readiness.py --target https://example.com --live-apis --workflows --json
```

One low-depth DataForSEO proof:

```bash
python scripts/demo_readiness.py --target https://example.com --live-apis --live-serp --serp-keyword "seo tools" --json
```

## Headless/API Usage

Run a single workflow:

```bash
python scripts/run_skill_workflow.py --skill ctk-seo-technical https://example.com --json
python scripts/run_skill_workflow.py --skill ctk-seo-google https://example.com --json
python scripts/run_skill_workflow.py --skill ctk-seo-dataforseo https://example.com --json
```

Run the full smoke suite:

```bash
python scripts/run_api_smoke_suite.py https://example.com --json
```

Verify environment:

```bash
python scripts/verify_environment.py --target https://example.com --json
```

Bootstrap a clean runtime:

```bash
python scripts/bootstrap_environment.py --json
```

Artifacts are written to `~/.local/state/ctk-codex-seo/reports/`. Shared cache
is written to `~/.cache/ctk-codex-seo/`; neither path mutates the active
repository.

```mermaid
%%{init: {"theme":"base","themeVariables":{"background":"#05080d","primaryColor":"#07131c","primaryTextColor":"#f5fbff","primaryBorderColor":"#00d7e6","lineColor":"#00d7e6","secondaryColor":"#06222a","tertiaryColor":"#ff9f1c","edgeLabelBackground":"#05080d","fontFamily":"Inter, ui-sans-serif, system-ui, sans-serif"}}}%%
flowchart LR
  cli["run_skill_workflow.py<br/>single workflow"] --> json["JSON result"]
  cli --> markdown["Markdown report"]
  cli --> cacheWrite["~/.cache/ctk-codex-seo update"]
  suite["run_api_smoke_suite.py<br/>all workflows"] --> json
  suite --> outputRoot["~/.local/state/ctk-codex-seo/reports/api-smoke-*"]
  verify["verify_environment.py"] --> readiness["ready / setup_required<br/>capability status"]
  markdown --> outputRoot
  json --> outputRoot
  cacheWrite --> cache["~/.cache/ctk-codex-seo"]
  class cli,suite,verify accent
  class cacheWrite,readiness data
  class json,markdown,outputRoot,cache output
  classDef default fill:#07131c,stroke:#00d7e6,color:#f5fbff,stroke-width:1.4px
  classDef accent fill:#10151a,stroke:#ff9f1c,color:#fff7ed,stroke-width:2px
  classDef data fill:#06222a,stroke:#21e6c1,color:#ecfeff,stroke-width:1.5px
  classDef output fill:#15101a,stroke:#ff9f1c,color:#fff7ed,stroke-width:1.8px
```

## Architecture

The repository separates Codex-facing instructions, deterministic runtime code, optional provider setup, and validation contracts. That keeps the skill system usable in chat, installable as a suite, and testable from CI/API workflows.

```mermaid
%%{init: {"theme":"base","themeVariables":{"background":"#05080d","primaryColor":"#07131c","primaryTextColor":"#f5fbff","primaryBorderColor":"#00d7e6","lineColor":"#00d7e6","secondaryColor":"#06222a","tertiaryColor":"#ff9f1c","edgeLabelBackground":"#05080d","fontFamily":"Inter, ui-sans-serif, system-ui, sans-serif"}}}%%
flowchart TB
  manifest[".codex-plugin/plugin.json"] --> skillsRoot["skills/"]
  skillsRoot --> orchestrator["ctk-seo/SKILL.md<br/>routing and orchestration"]
  skillsRoot --> specialists["ctk-seo-*/SKILL.md<br/>specialist workflows"]
  agentsDir["agents/ctk-seo-*.toml"] --> specialists
  scriptsDir["scripts/<br/>deterministic runners"] --> specialists
  extensionsDir["extensions/<br/>optional MCP setup"] --> specialists
  references["skills/ctk-seo/references/<br/>thresholds and shared contracts"] --> specialists
  specialists --> cacheDir["~/.cache/ctk-codex-seo/<br/>cross-skill memory"]
  specialists --> outputDir["~/.local/state/ctk-codex-seo/reports/<br/>reports and artifacts"]
  testsDir["tests/<br/>contract and smoke coverage"] --> manifest
  testsDir --> skillsRoot
  testsDir --> scriptsDir
  class manifest,orchestrator accent
  class skillsRoot,specialists,agentsDir,scriptsDir,extensionsDir,references,testsDir data
  class cacheDir,outputDir output
  classDef default fill:#07131c,stroke:#00d7e6,color:#f5fbff,stroke-width:1.4px
  classDef accent fill:#10151a,stroke:#ff9f1c,color:#fff7ed,stroke-width:2px
  classDef data fill:#06222a,stroke:#21e6c1,color:#ecfeff,stroke-width:1.5px
  classDef output fill:#15101a,stroke:#ff9f1c,color:#fff7ed,stroke-width:1.8px
```

```text
ctk-codex-seo/
├── .codex-plugin/plugin.json        # Codex plugin manifest
├── skills/
│   ├── ctk-seo/SKILL.md                 # Main orchestrator
│   └── ctk-seo-*/SKILL.md           # 26 specialist workflows
├── agents/                          # 24 Codex TOML agent profiles
├── scripts/                         # Deterministic runners and API helpers
├── extensions/
│   ├── dataforseo/                  # DataForSEO MCP setup and docs
│   ├── firecrawl/                   # Firecrawl MCP setup and docs
│   └── banana/                      # Gemini/nanobanana image generation setup
├── hooks/                           # Quality-gate hooks
├── schema/                          # Schema.org templates
├── docs/                            # Architecture, commands, installation, MCP, demo
└── tests/                           # Contract and workflow tests
```

Design principles:

- `skills/` is the source of truth.
- `skills/ctk-seo/SKILL.md` routes natural-language SEO requests.
- TOML agents are Codex-native and mirror specialist workflows.
- Runtime credentials stay in `~/.config/ctk-codex-seo/` or explicit
  environment variables.
- Legacy `claude-seo` config/cache paths are read only as migration fallback.

More detail: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## Verification

Local release gate:

```bash
python -m pytest tests/
bash -n install.sh uninstall.sh
python -m compileall -q scripts hooks
python scripts/run_api_smoke_suite.py https://example.com --json
```

PowerShell parse check:

```powershell
$files = Get-ChildItem -Recurse -Filter *.ps1
foreach ($f in $files) {
  $tokens = $null
  $errs = $null
  [System.Management.Automation.Language.Parser]::ParseFile($f.FullName, [ref]$tokens, [ref]$errs) > $null
  if ($errs.Count) { $errs; exit 1 }
}
```

Current GitHub CI runs:

- dependency install
- shell syntax checks
- Python compile checks
- `--help` checks for runner scripts
- `python -m pytest tests/`
- contract smoke checks for MCP-aware workflows

## Requirements

- Codex CLI with local skills support
- Python 3.10+
- Git
- Optional: Playwright Chromium for screenshots and PDF reports
- Optional: DataForSEO account for live SEO data
- Optional: Google API credentials for PageSpeed/CrUX/GSC/GA4
- Optional: Firecrawl API key for JS-rendered crawling
- Optional: Google AI API key for Gemini/nanobanana image generation

## Credentials And Cache

Codex SEO writes new local credentials and state to Codex-specific paths:

- `~/.config/ctk-codex-seo/` for API configs and cost ledgers
- `~/.cache/ctk-codex-seo/` for runtime caches
- `~/.local/state/ctk-codex-seo/reports/` for generated reports

Legacy `~/.config/claude-seo/` and `~/.cache/claude-seo/` paths are read only
as migration fallback. Never place `.mcp.json`, `.env`, OAuth tokens, service
accounts, or provider keys in a repository.

## Security

- URL-aware scripts block private, loopback, reserved, multicast, unspecified, and metadata hosts.
- Credential setup writes outside tracked repo files.
- Sensitive local settings are expected to use `0600` file permissions.
- DataForSEO calls use cost guardrails through `scripts/dataforseo_costs.py`.
- Report vulnerabilities through [SECURITY.md](SECURITY.md).

## Uninstall

```bash
bash uninstall.sh
```

Windows:

```powershell
powershell -ExecutionPolicy Bypass -File .\uninstall.ps1
```

## Contributing

Use [CONTRIBUTING.md](CONTRIBUTING.md) for local setup and validation, [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) for project standards, [SECURITY.md](SECURITY.md) for vulnerability reporting, and [CREDITS.md](CREDITS.md) for project credits. Agent-facing project context is also available in [llms.txt](llms.txt).

## Related Projects

- [`claude-seo`](https://github.com/AgriciDaniel/claude-seo) - original Claude Code SEO skill suite
- [`claude-blog`](https://github.com/AgriciDaniel/claude-blog) - blog creation and optimization skill ecosystem
- [`claude-ads`](https://github.com/AgriciDaniel/claude-ads) - paid advertising audit skill suite
- [`flow`](https://github.com/AgriciDaniel/flow) - evidence-led SEO framework for AI search
- [`wp-mcp-ultimate`](https://github.com/AgriciDaniel/wp-mcp-ultimate) - WordPress MCP server

## Credits

Special thanks to [avalonreset](https://github.com/avalonreset) for making the Codex conversion possible and for creating the initial Codex SEO version that this repository builds on.

## Attribution

Original project and concept by [AgriciDaniel](https://github.com/AgriciDaniel) in [`claude-seo`](https://github.com/AgriciDaniel/claude-seo). This Codex port preserves upstream SEO capabilities and adapts the runtime for Codex skills, TOML agents, plugin discovery, cache sharing, MCP extension setup, and API-safe wrappers.

Codex SEO is released under the MIT License. FLOW prompt references retain their upstream attribution and licensing notices where included.
