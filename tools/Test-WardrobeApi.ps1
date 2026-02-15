param(
  [string]$BaseUrl = "http://127.0.0.1:5002"
)

function Test-Endpoint([string]$Path) {
  $url = "$BaseUrl$Path"
  Write-Host "`n=== GET $url ==="
  try {
    $resp = Invoke-WebRequest -UseBasicParsing -Uri $url -Method GET -TimeoutSec 10 -ErrorAction Stop
    $ct = $resp.Headers["Content-Type"]
    $rid = $resp.Headers["X-Request-Id"]
    $snippet = $resp.Content
    if ($snippet.Length -gt 300) { $snippet = $snippet.Substring(0,300) }
    Write-Host "Status: $($resp.StatusCode)"
    Write-Host "Content-Type: $ct"
    if ($rid) { Write-Host "X-Request-Id: $rid" }
    Write-Host "Body: $snippet"
  } catch {
    $r = $_.Exception.Response
    if ($r) {
      $status = [int]$r.StatusCode
      $ct = $r.ContentType
      $reader = New-Object System.IO.StreamReader($r.GetResponseStream())
      $body = $reader.ReadToEnd()
      $reader.Close()
      $snippet = $body
      if ($snippet.Length -gt 300) { $snippet = $snippet.Substring(0,300) }
      Write-Host "Status: $status"
      Write-Host "Content-Type: $ct"
      Write-Host "Body: $snippet"
    } else {
      Write-Host "ERROR: $($_.Exception.Message)"
    }
  }
}

Test-Endpoint "/healthz"
Test-Endpoint "/openapi.json"
Test-Endpoint "/debug/routes"
Test-Endpoint "/api/v2/health"
