# Codex SEO Uninstaller for Windows

$ErrorActionPreference = "Stop"

$codexRoot = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $HOME ".codex" }
$skillsRoot = Join-Path $codexRoot "skills"
$agentDir = Join-Path $codexRoot "agents"

$skillNames = @(
    "ctk-seo",
    "ctk-seo-audit",
    "ctk-seo-backlinks",
    "ctk-seo-cluster",
    "ctk-seo-competitor-pages",
    "ctk-seo-content",
    "ctk-seo-dataforseo",
    "ctk-seo-drift",
    "ctk-seo-ecommerce",
    "ctk-seo-flow",
    "ctk-seo-firecrawl",
    "ctk-seo-geo",
    "ctk-seo-google",
    "ctk-seo-hreflang",
    "ctk-seo-image-gen",
    "ctk-seo-images",
    "ctk-seo-local",
    "ctk-seo-maps",
    "ctk-seo-page",
    "ctk-seo-performance",
    "ctk-seo-plan",
    "ctk-seo-programmatic",
    "ctk-seo-schema",
    "ctk-seo-sitemap",
    "ctk-seo-sxo",
    "ctk-seo-technical",
    "ctk-seo-visual"
)

$agentNames = @(
    "ctk-seo-backlinks",
    "ctk-seo-cluster",
    "ctk-seo-competitor-pages",
    "ctk-seo-content",
    "ctk-seo-dataforseo",
    "ctk-seo-drift",
    "ctk-seo-ecommerce",
    "ctk-seo-flow",
    "ctk-seo-firecrawl",
    "ctk-seo-geo",
    "ctk-seo-google",
    "ctk-seo-hreflang",
    "ctk-seo-image-gen",
    "ctk-seo-images",
    "ctk-seo-local",
    "ctk-seo-maps",
    "ctk-seo-performance",
    "ctk-seo-plan",
    "ctk-seo-programmatic",
    "ctk-seo-schema",
    "ctk-seo-sitemap",
    "ctk-seo-sxo",
    "ctk-seo-technical",
    "ctk-seo-visual"
)

Write-Host "[INFO] Uninstalling Codex SEO..." -ForegroundColor Yellow

foreach ($skill in $skillNames) {
    $path = Join-Path $skillsRoot $skill
    if (Test-Path $path) {
        Remove-Item -Path $path -Recurse -Force
    }
}

foreach ($agent in $agentNames) {
    foreach ($extension in @(".toml", ".md")) {
        $path = Join-Path $agentDir "$agent$extension"
        if (Test-Path $path) {
            Remove-Item -Path $path -Force
        }
    }
}

Write-Host "[OK] Codex SEO uninstalled." -ForegroundColor Green
