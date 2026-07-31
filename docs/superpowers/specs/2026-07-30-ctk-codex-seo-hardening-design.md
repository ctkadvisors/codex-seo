# CTK Codex SEO Hardening Design

## Goal

Turn the upstream Codex SEO suite into a reusable CTK Advisors plugin that can
be installed, authenticated, run, updated, and removed without overwriting
unrelated Codex configuration or exposing local credentials to unintended
processes or network destinations.

The fork remains public at `ctkadvisors/codex-seo`, preserves upstream history,
license, and attribution, and keeps `AgriciDaniel/codex-seo` as the documented
upstream source.

## Security and Safety Invariants

The following conditions are release blockers:

1. Installation and uninstallation may change only paths recorded in a
   CTK-owned installation manifest.
2. Existing skills, agents, plugins, hooks, settings, and project files are
   never deleted or overwritten implicitly.
3. A collision with a non-CTK-owned path fails before any persistent change.
4. Installation is staged and committed atomically. Any failure restores the
   exact pre-install state.
5. Default installation performs no optional vendor integration, browser
   download, global hook registration, or credential setup.
6. Credentials remain outside the repository and generated report/cache data.
7. Credential directories use mode `0700`; credential and token files use mode
   `0600` on POSIX systems.
8. The default Google integration requests Search Console read-only access
   only. Broader scopes require a separate explicit command and confirmation.
9. Core workflows may fetch only public HTTP(S) resources. Every redirect and
   DNS resolution is revalidated against private, loopback, link-local,
   reserved, multicast, and metadata destinations.
10. Provider-authenticated requests may send credentials only to an explicit,
    documented provider hostname allowlist.
11. Secret values never appear in logs, reports, cache files, exceptions, test
    snapshots, subprocess arguments, or diagnostic output.
12. Running the plugin does not modify a target repository unless the user
    supplies an explicit output or apply option.

## Packaging and Namespacing

The forked repository keeps its GitHub name for discoverability, but the Codex
plugin identity becomes `ctk-codex-seo`.

Installed resources are namespaced:

- plugin: `ctk-codex-seo`
- skills: `ctk-seo`, `ctk-seo-audit`, `ctk-seo-technical`, and so on
- agents: `ctk-seo-*.toml`
- runtime/config: `${CODEX_HOME}/marketplaces/ctk-advisors/plugins/ctk-codex-seo` and
  `${XDG_CONFIG_HOME:-~/.config}/ctk-codex-seo`
- cache/reports: `${XDG_CACHE_HOME:-~/.cache}/ctk-codex-seo/<site-id>` and
  `${XDG_STATE_HOME:-~/.local/state}/ctk-codex-seo`

No `seo*` resource owned by another installation is a valid replacement
target. The plugin does not edit `~/.codex/settings.json` during its default
installation.

## Installation Architecture

### Preflight

The installer:

1. Resolves and validates all target paths beneath the selected `CODEX_HOME`.
2. Rejects symlinks, traversal, unexpected owners, and non-regular manifest
   files.
3. Computes the complete install plan before writing.
4. Detects collisions and exits with a machine-readable report.
5. Verifies the source tree and release metadata.

### Transaction

The installer copies into a temporary sibling directory, verifies the staged
plugin, writes a content manifest containing relative paths and SHA-256
digests, and then performs an atomic rename.

Updating an existing CTK installation is allowed only when its ownership
manifest is valid. The current installation is renamed to a rollback directory,
the staged installation is activated, and the rollback directory is removed
only after post-install verification succeeds.

### Uninstall

The uninstaller reads the ownership manifest, validates every path and digest,
and removes only CTK-owned files. Modified files are reported and preserved
unless the user supplies an explicit force flag. Empty CTK-owned directories
may be removed; parent directories and shared configuration are never removed.

### Profiles

- `core` (default): technical, page, content, schema, sitemap, performance,
  GEO, SXO, drift, and Google Search Console read-only workflows.
- `visual`: Playwright package and Chromium, explicitly requested.
- `reports`: report-rendering dependencies, explicitly requested.
- `vendors`: DataForSEO, Firecrawl, Gemini/image generation, or other external
  providers, each installed and authenticated separately.

## Credential Architecture

Search Console supports a dedicated service account or a read-only OAuth flow.
The default scope is:

`https://www.googleapis.com/auth/webmasters.readonly`

The service account JSON remains at a user-selected path. The CTK config stores
only that path and the Search Console property identifier. OAuth token files
are created with restrictive permissions and are written atomically.

The Google Indexing API is excluded from the core profile because ordinary
content pages are not eligible. If retained as an optional workflow, it is
clearly limited to qualifying `JobPosting` or live-stream pages and uses a
separate authorization flow.

GA4, Google Ads, DataForSEO, Firecrawl, Bing Webmaster, and image-generation
credentials are optional provider-specific configurations. No workflow reads
Codex MCP settings or invokes `gh auth token` to discover credentials.

## Network and Local Data Policy

All network access goes through shared clients:

- `PublicWebClient` for unauthenticated site crawling.
- `ProviderClient` for allowlisted authenticated APIs.

Direct uses of `requests`, `urllib`, browser navigation, or shell utilities in
workflow scripts are prohibited by tests unless implemented inside the shared
network module.

The public client:

- permits only `http` and `https`;
- resolves hostnames before connecting;
- rejects prohibited IP ranges;
- pins the validated destination for the connection where supported;
- repeats validation on redirects and browser subresources;
- enforces response-size, redirect-count, and timeout limits;
- identifies itself with a documented user agent.

The provider client:

- accepts an enumerated provider identifier rather than an arbitrary URL;
- constructs URLs from fixed HTTPS origins;
- redacts configured secrets from all exceptions and logs;
- refuses redirects to a different origin.

Local reads are limited to explicitly supplied input paths, plugin-owned
configuration, plugin-owned cache/state, and the current audited repository.
Sensitive default locations such as SSH, cloud, GitHub, browser, and Codex
credential stores are denied unless a narrowly documented integration owns the
specific file.

## Repository Mutation Policy

Audit and reporting commands are read-only by default. They do not add
`.ctk-seo-cache` to `.gitignore`, create output in the current repository, edit
markup, install hooks, or apply recommendations.

Commands that produce artifacts default to CTK-owned cache/state locations.
Writing into a project requires `--output <path>`. Applying generated changes
requires a distinct `--apply` operation and remains subject to Codex approval
and the target repository's instructions.

## Dependency and Supply-Chain Policy

- Python runtime dependencies are resolved into a lock file with hashes.
- The installer uses the lock file with hash verification.
- Optional profiles have separate locks.
- Release workflows generate an SBOM and provenance/checksum artifact.
- CI runs dependency vulnerability scanning, secret scanning, static Python
  analysis, CodeQL, tests, and installer sandbox tests.
- Release tags used by installation documentation are immutable and signed by
  the CTK Advisors release identity where supported.
- Documentation never recommends piping a remote script directly into a shell.

## Upstream Maintenance

The fork documents:

- `origin`: `ctkadvisors/codex-seo`
- `upstream`: `AgriciDaniel/codex-seo`

Upstream updates arrive through pull requests. CI produces a security-impact
report identifying changes to installers, hooks, dependencies, credential
handling, subprocesses, and network calls. No automatic upstream merge or
release is permitted.

## Testing

### Installer and Ownership

- fresh install;
- safe update;
- collision before write;
- rollback on every transaction stage;
- uninstall of unchanged owned files;
- preservation of modified owned files;
- preservation of unrelated files byte-for-byte;
- traversal, symlink, and race-resistant path validation;
- spaces and Unicode in paths;
- alternate `CODEX_HOME` and XDG roots.

### Credential Safety

- POSIX directory/file modes;
- atomic token replacement;
- read-only Google scope by default;
- redaction in success, failure, timeout, and subprocess output;
- no credentials in reports, caches, manifests, or Git status.

### Network Safety

- loopback, private, link-local, reserved, multicast, IPv4-mapped IPv6, and
  metadata rejection;
- DNS rebinding simulation;
- redirect and browser-subresource revalidation;
- authenticated cross-origin redirect rejection;
- response-size and timeout enforcement;
- static prohibition of bypass network clients.

### Compatibility

- all retained upstream deterministic workflow tests;
- plugin and skill validation;
- Linux and macOS installation;
- Python 3.10 through current supported stable versions;
- a live, credential-free audit against a controlled public fixture.

## Delivery Sequence

1. Establish CTK identity, threat model, and CI.
2. Build the ownership-manifest installer and uninstaller.
3. Namespace plugin, skills, agents, runtime, cache, and config.
4. Harden credentials and reduce Google scopes.
5. Centralize and constrain network access.
6. Remove implicit repository mutation and credential discovery.
7. Lock dependencies and separate optional profiles.
8. Run security/compatibility verification and publish a pinned CTK release.

## Acceptance Criteria

The first CTK release is acceptable when:

- an integration test proves unrelated Codex state is byte-for-byte unchanged
  across install, update, failed update, and uninstall;
- no default command can read common local credential stores or send data to an
  origin outside the documented allowlist;
- Search Console read-only authentication and URL inspection work without
  exposing credentials;
- the core audit works without optional vendors, Chromium, or global hooks;
- all retained tests and new security gates pass in CI;
- installation documentation uses a pinned CTK release and a reviewable local
  command, never remote shell piping.
