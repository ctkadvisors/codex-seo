# Threat Model

## Protected assets

- Codex configuration, skills, agents, hooks, and unrelated plugins
- OAuth refresh/access tokens and provider API credentials
- project source, Git metadata, and files outside explicit output roots
- local-network, loopback, link-local, and cloud-metadata services

## Trust boundaries

The checked-out CTK release is trusted only after review. Websites, redirects,
DNS answers, API responses, prompt content, and upstream changes are untrusted.
Provider credentials are accepted only from documented environment variables
or CTK config files.

## Controls

- Installation is local, transactional, namespaced, and ownership-manifested.
- No installer downloads code, installs dependencies, edits settings, or
  registers hooks.
- Updates refuse foreign directories, corrupt manifests, symlinks, and modified
  owned files.
- Uninstall removes only hash-matching owned files unless an explicit force
  flag is supplied.
- HTTP calls pass through `security_network.py`, which validates each URL and
  redirect, blocks non-public addresses, constrains credential destinations,
  and applies timeout, redirect, and response-size limits.
- Google OAuth defaults to read-only Search Console and Analytics access.
- Secrets are written atomically with restrictive permissions and redacted
  from structured diagnostics.
- Audit caches and reports default to XDG cache/state locations, not the
  inspected repository.

## Non-goals

This project cannot make third-party APIs trustworthy, prevent a compromised
Python interpreter or operating system from reading process credentials, or
guarantee that arbitrary websites are benign. Run only reviewed CTK revisions
and grant provider access narrowly.
