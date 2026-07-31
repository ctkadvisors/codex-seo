# Upstream Policy

This repository is a security-hardened fork of
[`AgriciDaniel/codex-seo`](https://github.com/AgriciDaniel/codex-seo). MIT
license and attribution are preserved.

Upstream changes are never merged automatically. Each sync is reviewed for:

- installer or uninstall scope changes
- new hooks, subprocess execution, or credential discovery
- new network call sites or provider origins
- writes outside CTK XDG roots and explicit user output paths
- dependency and workflow changes

Namespace migration and security-policy tests must pass before an upstream
change can enter `main`.
