# Installation

Clone the CTK-reviewed fork, inspect the revision if desired, then run its
local installer:

```bash
git clone https://github.com/ctkadvisors/codex-seo.git
cd codex-seo
./install.sh
```

PowerShell:

```powershell
git clone https://github.com/ctkadvisors/codex-seo.git
cd codex-seo
.\install.ps1
```

The installer writes one self-contained directory:
`${CODEX_HOME:-~/.codex}/plugins/ctk-codex-seo`. It does not download code,
install dependencies, edit Codex settings, register hooks, or touch shared
`skills/` and `agents/` directories.

Every installed file is recorded with a SHA-256 digest in
`install-manifest.json`. An existing directory without a valid CTK ownership
manifest is treated as a collision. Updates refuse to overwrite locally
modified owned files.

Use `CODEX_HOME=/alternate/path` to select another Codex home.

## Uninstall

```bash
./uninstall.sh
```

PowerShell:

```powershell
.\uninstall.ps1
```

Uninstall removes only unchanged files listed in the ownership manifest.
Modified files are preserved and reported. To explicitly remove them too:

```bash
./uninstall.sh --force-owned-modifications
```
