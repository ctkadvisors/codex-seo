#!/usr/bin/env bash
set -euo pipefail

main() {
    CODEX_ROOT="${CODEX_HOME:-${HOME}/.codex}"
    SKILLS_ROOT="${CODEX_ROOT}/skills"
    echo "[INFO] Uninstalling Codex SEO..."

    # Remove main skill (includes venv and requirements.txt)
    rm -rf "${SKILLS_ROOT}/ctk-seo"

    # Remove sub-skills
    for skill in ctk-seo-audit ctk-seo-backlinks ctk-seo-cluster ctk-seo-competitor-pages ctk-seo-content ctk-seo-dataforseo ctk-seo-drift ctk-seo-ecommerce ctk-seo-flow ctk-seo-firecrawl ctk-seo-geo ctk-seo-google ctk-seo-hreflang ctk-seo-image-gen ctk-seo-images ctk-seo-local ctk-seo-maps ctk-seo-page ctk-seo-performance ctk-seo-plan ctk-seo-programmatic ctk-seo-schema ctk-seo-sitemap ctk-seo-sxo ctk-seo-technical ctk-seo-visual; do
        rm -rf "${SKILLS_ROOT}/${skill}"
    done

    # Remove agent profiles
    for agent in ctk-seo-backlinks ctk-seo-cluster ctk-seo-competitor-pages ctk-seo-content ctk-seo-dataforseo ctk-seo-drift ctk-seo-ecommerce ctk-seo-flow ctk-seo-firecrawl ctk-seo-geo ctk-seo-google ctk-seo-hreflang ctk-seo-image-gen ctk-seo-images ctk-seo-local ctk-seo-maps ctk-seo-performance ctk-seo-plan ctk-seo-programmatic ctk-seo-schema ctk-seo-sitemap ctk-seo-sxo ctk-seo-technical ctk-seo-visual; do
        rm -f "${CODEX_ROOT}/agents/${agent}.toml"
        rm -f "${CODEX_ROOT}/agents/${agent}.md"
    done

    echo "[OK] Codex SEO uninstalled."
}

main "$@"
