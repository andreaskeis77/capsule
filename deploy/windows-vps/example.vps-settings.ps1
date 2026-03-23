# Copy this file to:
#   deploy\windows-vps\vps-settings.ps1
# and adapt the values for the VPS.

$CapsuleRepoRoot = "C:\CapsuleWardrobeRAG"
$CapsulePythonExe = "C:\CapsuleWardrobeRAG\.venv\Scripts\python.exe"

# API is intentionally local-only. External access goes through ngrok.
$CapsuleBindHost = "127.0.0.1"
$CapsuleBindPort = 8000

# Git update source on the VPS
$CapsuleGitBranch = "main"

# ngrok
$NgrokExe = "C:\tools\ngrok\ngrok.exe"
$NgrokConfigPath = "C:\CapsuleWardrobeRAG\deploy\windows-vps\ngrok.yml"
$NgrokAuthtoken = "REPLACE_ME"
# Optional reserved domain, e.g. "capsule-yourteam.ngrok.app"
$NgrokDomain = ""

# Scheduled task names
$CapsuleApiTaskName = "Capsule-API"
$CapsuleNgrokTaskName = "Capsule-ngrok"

# Logs
$CapsuleLogsDir = "C:\CapsuleWardrobeRAG\logs\vps"

# Smoke tests
$CapsuleLocalHealthUrl = "http://127.0.0.1:8000/health"
# Optional public URL if you have a reserved ngrok domain:
# $CapsulePublicBaseUrl = "https://capsule-yourteam.ngrok.app"
$CapsulePublicBaseUrl = ""
