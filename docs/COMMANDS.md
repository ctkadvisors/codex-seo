# Command Reference

Codex SEO works best from natural-language prompts, but command-style prompts are supported.

## Common Workflows

| Prompt | Purpose |
|---|---|
| `$ctk-seo audit <url>` | Full SEO audit with specialist routing |
| `$ctk-seo page <url>` | Deep single-page analysis |
| `$ctk-seo technical <url>` | Crawlability, indexability, CWV, JavaScript, security |
| `$ctk-seo content <url>` | E-E-A-T, helpfulness, readability, AI citation readiness |
| `$ctk-seo schema <url>` | Structured data detection, validation, generation |
| `$ctk-seo images <url>` | Alt text, image weight, metadata, SERP image opportunities |
| `$ctk-seo sitemap <url>` | XML sitemap discovery, coverage, generation guidance |
| `$ctk-seo geo <url>` | AI search/GEO readiness, crawler access, citability |
| `$ctk-seo performance <url>` | Core Web Vitals and Lighthouse-oriented performance |
| `$ctk-seo visual <url>` | Screenshot, mobile, above-the-fold, CTA visibility |
| `$ctk-seo plan <business-type>` | Strategic SEO roadmap |
| `$ctk-seo programmatic <url>` | Programmatic SEO risk and scale planning |
| `$ctk-seo competitor-pages <url>` | Comparison/alternative page opportunities |
| `$ctk-seo hreflang <url>` | International SEO and content parity |
| `$ctk-seo local <url>` | Local SEO, NAP, GBP signals, citations, reviews |
| `$ctk-seo maps <command>` | Maps/geo-grid intelligence when integrations exist |
| `$ctk-seo google setup` | Google API credential setup guidance |
| `$ctk-seo backlinks <url>` | Backlink profile summary and data-source detection |
| `$ctk-seo cluster <keyword>` | SERP-based topic clustering |
| `$ctk-seo sxo <url>` | Search Experience Optimization |
| `$ctk-seo drift baseline <url>` | Capture SEO baseline |
| `$ctk-seo drift compare <url>` | Compare against baseline |
| `$ctk-seo ecommerce <url>` | Product/e-commerce SEO |
| `$ctk-seo flow <stage>` | FLOW framework prompt workflow |
| `$ctk-seo dataforseo <command>` | Live DataForSEO data when MCP is configured |
| `$ctk-seo firecrawl <command>` | Site crawling when Firecrawl MCP is configured |
| `$ctk-seo image-gen <use-case>` | SEO image asset generation when MCP is configured |

## Headless Examples

```bash
python scripts/run_skill_workflow.py --skill ctk-seo-technical https://example.com --json
python scripts/run_skill_workflow.py --skill ctk-seo-google https://example.com --json
python scripts/run_api_smoke_suite.py https://example.com --skill ctk-seo-drift --json
```

Wrappers write artifacts to `~/.local/state/ctk-codex-seo/reports/` and cache summaries to `~/.cache/ctk-codex-seo/`.
