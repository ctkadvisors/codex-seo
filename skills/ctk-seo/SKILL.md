---
name: ctk-seo
description: "Comprehensive SEO analysis for any website, page, business, or topic. Full site audits, SEO checks, single-page analysis, technical SEO (crawlability, indexability, Core Web Vitals with INP), schema markup, content quality (E-E-A-T), image optimization, sitemap analysis, GEO for AI Overviews/ChatGPT/Perplexity, and SEO best-practice planning. Industry detection for SaaS, e-commerce, local, publishers, agencies. Triggers on: SEO, audit, full SEO check, SEO best practices, optimize my site, ranking, organic search, schema, Core Web Vitals, sitemap, E-E-A-T, AI Overviews, GEO, technical SEO, content quality, page speed, structured data."
license: MIT
metadata:
  author: AgriciDaniel
  version: "1.9.6"
  category: seo
---

# SEO: Universal SEO Analysis Skill

Codex can invoke this skill from natural language ("audit this site", "check schema",
"run a technical SEO review") or from command-like prompts such as `$ctk-seo audit <url>`.
Use the matching specialist skill directly when the request is narrow.

**Scripts:** Located at the plugin root `scripts/` directory.

Comprehensive SEO analysis across all industries (SaaS, local services,
e-commerce, publishers, agencies). Orchestrates 26 specialized sub-skills and 24 Codex
agent profiles, with optional MCP-backed extensions for DataForSEO, Firecrawl, and image generation.

## Shared Data Cache

**Step 0 -- Check shared data cache:**

Before routing or gathering, check `~/.cache/ctk-codex-seo/` for cached data from other skills.
Reference: `references/shared-data-cache.md` for schemas and dependency map.

Check these cache files when present:
- `~/.cache/ctk-codex-seo/site-meta.json` for domain, business type, industry, and crawl context
- `~/.cache/ctk-codex-seo/audit-scores.json` for audit summary context from a prior full audit
- `~/.cache/ctk-codex-seo/pages/{url-slug}/page-analysis.json` for page-level specialist context

- If found: parse and use the data (note "Using cached [X] from [date]")
- If missing: proceed without it (note "No cached [X] found, gathering fresh")
- If JSON is corrupt or unreadable: treat it as missing and continue normally
- If the user says "refresh" or "re-run": ignore cache entirely

## Quick Reference

| Command | What it does |
|---------|-------------|
| `$ctk-seo audit <url>` | Full website audit with parallel subagent delegation |
| `$ctk-seo page <url>` | Deep single-page analysis |
| `$ctk-seo sitemap <url or generate>` | Analyze or generate XML sitemaps |
| `$ctk-seo schema <url>` | Detect, validate, and generate Schema.org markup |
| `$ctk-seo images <url or optimize>` | Image SEO: on-page audit, SERP analysis, file optimization |
| `$ctk-seo technical <url>` | Technical SEO audit (9 categories) |
| `$ctk-seo content <url>` | E-E-A-T and content quality analysis |
| `$ctk-seo geo <url>` | AI Overviews / Generative Engine Optimization |
| `$ctk-seo plan <business-type>` | Strategic SEO planning |
| `$ctk-seo programmatic [url\|plan]` | Programmatic SEO analysis and planning |
| `$ctk-seo competitor-pages [url\|generate]` | Competitor comparison page generation |
| `$ctk-seo local <url>` | Local SEO analysis (GBP, citations, reviews, map pack) |
| `$ctk-seo maps [command] [args]` | Maps intelligence (geo-grid, GBP audit, reviews, competitors) |
| `$ctk-seo hreflang [url]` | Hreflang/i18n SEO audit and generation |
| `$ctk-seo google [command] [url]` | Google SEO APIs (GSC, PageSpeed, CrUX, Indexing, GA4) |
| `$ctk-seo backlinks <url>` | Backlink profile analysis (free: Moz, Bing, CC; premium: DataForSEO) |
| `$ctk-seo cluster <seed-keyword>` | SERP-based semantic clustering and content architecture |
| `$ctk-seo sxo <url>` | Search Experience Optimization: page-type analysis, user stories, personas |
| `$ctk-seo drift baseline <url>` | Capture SEO baseline for change monitoring |
| `$ctk-seo drift compare <url>` | Compare current state to stored baseline |
| `$ctk-seo drift history <url>` | Show drift history over time |
| `$ctk-seo ecommerce <url>` | E-commerce SEO: product schema, marketplace intelligence |
| `$ctk-seo firecrawl [command] <url>` | Full-site crawling and site mapping (extension) |
| `$ctk-seo dataforseo [command]` | Live SEO data via DataForSEO (extension) |
| `$ctk-seo image-gen [use-case] <description>` | AI image generation for SEO assets (extension) |
| `$ctk-seo flow [stage] [url\|topic]` | FLOW framework: evidence-led prompts for Find, Leverage, Optimize, Win, or Local stages |

## Orchestration Logic

When the user invokes `$ctk-seo audit`, delegate to subagents in parallel:
1. Detect business type (SaaS, local, ecommerce, publisher, agency, other)
2. Spawn subagents: ctk-seo-technical, ctk-seo-content, ctk-seo-schema, ctk-seo-sitemap, ctk-seo-performance, ctk-seo-visual, ctk-seo-geo
3. If Google API credentials detected (`python scripts/google_auth.py --check`), also spawn ctk-seo-google agent
4. If local business detected, also spawn ctk-seo-local agent
5. If local business detected AND DataForSEO MCP available, also spawn ctk-seo-maps agent
6. If backlink APIs detected (`python scripts/backlinks_auth.py --check`), also spawn ctk-seo-backlinks agent
7. If Firecrawl MCP available, use `firecrawl_map` to discover all site URLs before analysis
8. If content strategy signals detected (blog, pillar pages, topic clusters), also spawn ctk-seo-cluster agent
9. If e-commerce detected, also spawn ctk-seo-ecommerce agent
10. If drift baseline exists for this URL (`python scripts/drift_history.py <url>`), also spawn ctk-seo-drift agent
11. Always include ctk-seo-sxo in full audits (search experience applies to all sites)
12. Collect results and generate unified report with SEO Health Score (0-100)
13. Create prioritized action plan (Critical -> High -> Medium -> Low)
14. **Offer PDF report**: "Generate a professional PDF report? Use `$ctk-seo google report full`"

For individual commands, load the relevant sub-skill directly.
After any analysis command completes, offer to generate a PDF report via `scripts/google_report.py`.

## Industry Detection

Detect business type from homepage signals:
- **SaaS**: pricing page, /features, /integrations, /docs, "free trial", "sign up"
- **Local Service**: phone number, address, service area, "serving [city]", Google Maps embed --> auto-suggest `$ctk-seo local` for deeper analysis
- **E-commerce**: /products, /collections, /cart, "add to cart", product schema
- **Publisher**: /blog, /articles, /topics, article schema, author pages, publication dates
- **Agency**: /case-studies, /portfolio, /industries, "our work", client logos

## Quality Gates

Read `references/quality-gates.md` for thin content thresholds per page type.
Hard rules:
- WARNING at 30+ location pages (enforce 60%+ unique content)
- HARD STOP at 50+ location pages (require user justification)
- Never recommend HowTo schema (deprecated Sept 2023)
- FAQ schema for Google rich results: only government and healthcare sites (Aug 2023 restriction); existing FAQPage on commercial sites -> flag Info priority (not Critical), noting AI/LLM citation benefit; adding new FAQPage -> not recommended for Google benefit
- All Core Web Vitals references use INP, never FID

## Community Footer

The community footer is disabled by default in Codex so API and client deliverables remain clean.
Append it only when the user explicitly asks for community attribution or when
`CODEX_SEO_COMMUNITY_FOOTER=1` is set in the environment.

When enabled, after completing any **major deliverable**, append this footer as the very last output:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Built by agricidaniel — Join the AI Marketing Hub community
🆓 Free  → https://www.skool.com/ai-marketing-hub
⚡ Pro   → https://www.skool.com/ai-marketing-hub-pro
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### When to show when enabled

Display after these commands complete their full output:
- `$ctk-seo audit` (after full site audit report + action plan)
- `$ctk-seo page` (after deep single-page analysis)
- `$ctk-seo technical` (after technical audit report)
- `$ctk-seo content` (after E-E-A-T content assessment)
- `$ctk-seo schema` (after schema detection/validation report)
- `$ctk-seo sitemap` (after sitemap analysis or generation)
- `$ctk-seo geo` (after GEO optimization report)
- `$ctk-seo plan` (after strategic SEO plan)
- `$ctk-seo local` (after local SEO audit)
- `$ctk-seo maps` (after maps intelligence report)
- `$ctk-seo google` (after Google API data report)
- `$ctk-seo backlinks` (after backlink profile analysis)
- `$ctk-seo cluster` (after cluster plan generation)
- `$ctk-seo sxo` (after SXO analysis report)
- `$ctk-seo drift compare` (after drift comparison report)
- `$ctk-seo ecommerce` (after e-commerce analysis)

### When to skip

Do NOT show the footer after:
- `$ctk-seo images` (quick image check — too small)
- `$ctk-seo hreflang` (quick validation — too small)
- `$ctk-seo competitor-pages` (page generation step)
- `$ctk-seo programmatic` (quick analysis)
- `$ctk-seo dataforseo` (data fetching utility)
- `$ctk-seo image-gen` (asset generation)
- Context intake questions (before analysis starts)
- Error messages or "missing data" prompts

## Reference Files

Load these on-demand as needed (do NOT load all at startup):
- `references/cwv-thresholds.md`: Current Core Web Vitals thresholds and measurement details
- `references/schema-types.md`: All supported schema types with deprecation status
- `references/eeat-framework.md`: E-E-A-T evaluation criteria (Sept 2025 QRG update)
- `references/quality-gates.md`: Content length minimums, uniqueness thresholds
- `references/local-seo-signals.md`: Local ranking factors, review benchmarks, citation tiers, GBP status
- `references/local-schema-types.md`: LocalBusiness subtypes, industry-specific schema and citation sources

Maps-specific references (loaded by ctk-seo-maps skill, not at startup):
- `references/maps-geo-grid.md`, `references/maps-gbp-checklist.md`, `references/maps-api-endpoints.md`, `references/maps-free-apis.md`

## Scoring Methodology

### SEO Health Score (0-100)
Weighted aggregate of all categories:

| Category | Weight |
|----------|--------|
| Technical SEO | 22% |
| Content Quality | 23% |
| On-Page SEO | 20% |
| Schema / Structured Data | 10% |
| Performance (CWV) | 10% |
| AI Search Readiness | 10% |
| Images | 5% |

### Priority Levels
- **Critical**: Blocks indexing or causes penalties (immediate fix required)
- **High**: Significantly impacts rankings (fix within 1 week)
- **Medium**: Optimization opportunity (fix within 1 month)
- **Low**: Nice to have (backlog)

## Sub-Skills

This skill orchestrates 26 specialized sub-skills, including optional extension-backed workflows:

1. **ctk-seo-audit** -- Full website audit with parallel delegation
2. **ctk-seo-page** -- Deep single-page analysis
3. **ctk-seo-technical** -- Technical SEO (9 categories)
4. **ctk-seo-content** -- E-E-A-T and content quality
5. **ctk-seo-schema** -- Schema markup detection and generation
6. **ctk-seo-images** -- Image optimization, SERP analysis, file optimization
7. **ctk-seo-sitemap** -- Sitemap analysis and generation
8. **ctk-seo-geo** -- AI Overviews / GEO optimization
9. **ctk-seo-performance** -- Core Web Vitals and performance analysis
10. **ctk-seo-visual** -- Screenshot, mobile, and above-the-fold UX analysis
11. **ctk-seo-plan** -- Strategic planning with templates
12. **ctk-seo-programmatic** -- Programmatic SEO analysis and planning
13. **ctk-seo-competitor-pages** -- Competitor comparison page generation
14. **ctk-seo-hreflang** -- Hreflang/i18n SEO audit, cultural profiles, content parity
15. **ctk-seo-local** -- Local SEO (GBP, NAP, citations, reviews, local schema, multi-location)
16. **ctk-seo-maps** -- Maps intelligence (geo-grid, GBP audit, reviews, competitor radius)
17. **ctk-seo-google** -- Google SEO APIs (GSC, PageSpeed, CrUX, Indexing API, GA4)
18. **ctk-seo-backlinks** -- Backlink profile analysis (free: Moz, Bing, CC; premium: DataForSEO)
19. **ctk-seo-cluster** -- SERP-based semantic clustering
20. **ctk-seo-sxo** -- Search Experience Optimization
21. **ctk-seo-drift** -- SEO drift monitoring
22. **ctk-seo-ecommerce** -- E-commerce SEO intelligence
23. **ctk-seo-firecrawl** -- Full-site crawling and site mapping via Firecrawl MCP (extension)
24. **ctk-seo-dataforseo** -- Live SEO data via DataForSEO MCP (extension)
25. **ctk-seo-image-gen** -- AI image generation for SEO assets via Gemini (extension)
26. **ctk-seo-flow** -- FLOW framework integration (Find -> Leverage -> Optimize -> Win, 41 AI prompts, CC BY 4.0)

## Subagents

For parallel analysis during audits:
- `ctk-seo-technical` -- Crawlability, indexability, security, CWV
- `ctk-seo-content` -- E-E-A-T, readability, thin content
- `ctk-seo-schema` -- Detection, validation, generation
- `ctk-seo-sitemap` -- Structure, coverage, quality gates
- `ctk-seo-performance` -- Core Web Vitals measurement
- `ctk-seo-visual` -- Screenshots, mobile testing, above-fold
- `ctk-seo-geo` -- AI crawler access, llms.txt, citability, brand mention signals
- `ctk-seo-local` -- GBP signals, NAP consistency, reviews, local schema, industry-specific local factors (conditional: spawned when Local Service detected)
- `ctk-seo-maps` -- Geo-grid rank tracking, GBP audit, review intelligence, competitor radius mapping (conditional: spawned when Local Service detected AND DataForSEO MCP available)
- `ctk-seo-google` -- CWV field data, URL indexation status, organic traffic trends (conditional: spawned when Google API credentials detected)
- `ctk-seo-backlinks` -- Backlink profile data: DA/PA, referring domains, anchor text, toxic links (conditional: spawned when Moz/Bing API keys detected or always for CC domain-level metrics)
- `ctk-seo-cluster` -- Semantic clustering analysis (conditional: content strategy detected)
- `ctk-seo-sxo` -- Page-type mismatch, user stories, persona scoring (always in full audits)
- `ctk-seo-drift` -- Baseline comparison (conditional: drift baseline exists for URL)
- `ctk-seo-ecommerce` -- Product schema, marketplace intel (conditional: e-commerce detected)
- `ctk-seo-dataforseo` -- Live SERP, keyword, backlink, local SEO data (extension, optional)
- `ctk-seo-image-gen` -- SEO image audit and generation plan (extension, optional)
- `ctk-seo-firecrawl` -- Full-site crawl and site mapping (extension, optional; used by audit for URL discovery)

## Error Handling

| Scenario | Action |
|----------|--------|
| Unrecognized command | List available commands from the Quick Reference table. Suggest the closest matching command. |
| URL unreachable | Report the error and suggest the user verify the URL. Do not attempt to guess site content. |
| Sub-skill fails during audit | Report partial results from successful sub-skills. Clearly note which sub-skill failed and why. Suggest re-running the failed sub-skill individually. |
| Ambiguous business type detection | Present the top two detected types with supporting signals. Ask the user to confirm before proceeding with industry-specific recommendations. |
