# Prints HTTP headers for the GitHub MCP server as JSON, fetching the token
# from the GitHub CLI at connection time. The token is never stored in a file.
$token = (gh auth token 2>$null)
if (-not $token) { exit 1 }
@{ Authorization = "Bearer $token" } | ConvertTo-Json -Compress
