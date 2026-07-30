$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
python "$ScriptDir\scripts\ctk_install.py" uninstall @args
exit $LASTEXITCODE
