<#
.SYNOPSIS
    Azure Automation runbook: generate the Daily Health Briefing with Azure OpenAI and open
    a pull request on the GitHub Pages repo for review.

.DESCRIPTION
    Designed to run in an Azure Automation account on a schedule (e.g. daily), using a
    system-assigned managed identity to read secrets from Key Vault. It:
      1. Reads a GitHub token (+ Azure OpenAI key) from Key Vault.
      2. Calls Azure OpenAI to generate a briefing that follows the agent instructions.
      3. Creates a branch, commits health/briefings/<date>.json and the updated
         health/index.json via the GitHub Contents API, and opens a PR.

    Merge the PR to publish (a push to main auto-deploys via GitHub Pages).

.NOTES
    Prerequisites
      - Az PowerShell modules in the Automation account: Az.Accounts, Az.KeyVault.
      - System-assigned managed identity enabled, with Key Vault "get secret" access.
      - Key Vault secrets:
          gh-pat-blog      : fine-grained GitHub PAT with contents:rw + pull_requests:rw on the repo
          aoai-api-key     : Azure OpenAI API key
      - Automation variables (or edit the param defaults below):
          KeyVaultName, AoaiEndpoint, AoaiDeployment, GitHubOwner, GitHubRepo
#>

param(
    [string] $KeyVaultName   = (Get-AutomationVariable -Name 'KeyVaultName'),
    [string] $AoaiEndpoint   = (Get-AutomationVariable -Name 'AoaiEndpoint'),    # https://my-aoai.openai.azure.com
    [string] $AoaiDeployment = (Get-AutomationVariable -Name 'AoaiDeployment'),  # e.g. gpt-4o
    [string] $AoaiApiVersion = '2024-10-21',
    [string] $GitHubOwner    = 'j00x',
    [string] $GitHubRepo     = 'apremote.github.io',
    [string] $Date           = (Get-Date).ToString('yyyy-MM-dd')
)

$ErrorActionPreference = 'Stop'
$allowedIcons = @('sparkle', 'bolt', 'anchor', 'ribbon', 'moon', 'pulse')

# --- 1. Auth & secrets ------------------------------------------------------
Connect-AzAccount -Identity | Out-Null
$ghToken  = (Get-AzKeyVaultSecret -VaultName $KeyVaultName -Name 'gh-pat-blog'  -AsPlainText)
$aoaiKey  = (Get-AzKeyVaultSecret -VaultName $KeyVaultName -Name 'aoai-api-key' -AsPlainText)

$ghHeaders = @{
    Authorization          = "Bearer $ghToken"
    'User-Agent'           = 'health-briefing-runbook'
    Accept                 = 'application/vnd.github+json'
    'X-GitHub-Api-Version' = '2022-11-28'
}
$apiBase = "https://api.github.com/repos/$GitHubOwner/$GitHubRepo"

# --- 2. Pull the agent instructions + memory from the repo ------------------
function Get-RepoFile([string] $Path) {
    # Returns @{ text = <decoded>; sha = <blob sha> }
    $r = Invoke-RestMethod -Method Get -Uri "$apiBase/contents/$Path" -Headers $ghHeaders
    @{ text = [Text.Encoding]::UTF8.GetString([Convert]::FromBase64String($r.content)); sha = $r.sha }
}
$instructions = (Get-RepoFile 'automation/health-briefing-agent.md').text
$memories     = (Get-RepoFile 'automation/memories.md').text

# --- 3. Generate the briefing with Azure OpenAI -----------------------------
$system  = "$instructions`n`n---`nLONG-TERM MEMORY (authoritative for topics/voice/rules):`n$memories"
$userMsg = @"
Write today's Daily Health Briefing following the instructions and memory above.
- Date: $Date (use this exact value for the `date` field).
- Produce ONE section per standing topic from memory, in the canonical order.
- Only cite real sources you actually found; never invent a title, journal, or URL.

Return ONLY a JSON object with keys:
  date (string YYYY-MM-DD), title (string), intro (one warm sentence),
  sections (array of { topic (string), icon (sparkle|bolt|anchor|ribbon|moon|pulse),
  body (Markdown, ~60-150 words), sources (array of { title, publisher, url, date }) }).
"@

$aoaiUri  = "$($AoaiEndpoint.TrimEnd('/'))/openai/deployments/$AoaiDeployment/chat/completions?api-version=$AoaiApiVersion"
$aoaiBody = @{
    messages        = @(
        @{ role = 'system'; content = $system },
        @{ role = 'user';   content = $userMsg }
    )
    response_format = @{ type = 'json_object' }
    temperature     = 0.3
} | ConvertTo-Json -Depth 6

$aoaiResp  = Invoke-RestMethod -Method Post -Uri $aoaiUri `
    -Headers @{ 'api-key' = $aoaiKey; 'Content-Type' = 'application/json' } -Body $aoaiBody
$briefing  = $aoaiResp.choices[0].message.content | ConvertFrom-Json

if (-not $briefing.sections -or $briefing.sections.Count -eq 0) {
    throw 'Model returned no sections; refusing to publish an empty briefing.'
}

# --- 4. Normalise + build the briefing file ---------------------------------
$briefing.date = $Date
if (-not $briefing.title) { $briefing | Add-Member -NotePropertyName title -NotePropertyValue 'Daily Health Briefing' -Force }
foreach ($sec in $briefing.sections) {
    if ($sec.icon -notin $allowedIcons) { $sec.icon = 'pulse' }
}
$briefingJson = ($briefing | ConvertTo-Json -Depth 8)

# --- 5. Read + update the archive manifest (prepend today) ------------------
$indexFile = Get-RepoFile 'health/index.json'
$index     = $indexFile.text | ConvertFrom-Json
$kept      = @($index.briefings | Where-Object { $_.date -ne $Date })
$index.briefings = @(@{ date = $Date; title = $briefing.title }) + $kept
$indexJson = ($index | ConvertTo-Json -Depth 5)

# --- 6. Create a branch, commit both files, open a PR -----------------------
$branch  = "bot/health-briefing-$Date-$(Get-Random -Maximum 9999)"
$mainRef = Invoke-RestMethod -Method Get -Uri "$apiBase/git/ref/heads/main" -Headers $ghHeaders
$baseSha = $mainRef.object.sha

Invoke-RestMethod -Method Post -Uri "$apiBase/git/refs" -Headers $ghHeaders -Body (
    @{ ref = "refs/heads/$branch"; sha = $baseSha } | ConvertTo-Json
) | Out-Null

function Put-RepoFile([string] $Path, [string] $Text, [string] $Sha) {
    $body = @{
        message = "health: add briefing for $Date"
        content = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($Text))
        branch  = $branch
    }
    if ($Sha) { $body.sha = $Sha }   # required when updating an existing file
    Invoke-RestMethod -Method Put -Uri "$apiBase/contents/$Path" -Headers $ghHeaders `
        -Body ($body | ConvertTo-Json) | Out-Null
}

Put-RepoFile "health/briefings/$Date.json" $briefingJson $null
Put-RepoFile 'health/index.json'           $indexJson    $indexFile.sha

$pr = Invoke-RestMethod -Method Post -Uri "$apiBase/pulls" -Headers $ghHeaders -Body (
    @{
        title = "health: briefing for $Date"
        head  = $branch
        base  = 'main'
        body  = "Automated draft from the Health Briefing Agent runbook.`n`n- Date: ``$Date```n- Sections: ``$($briefing.sections.Count)```n`nReview (verify every source resolves), then merge to publish."
        draft = $true
    } | ConvertTo-Json
)

Write-Output "Opened PR #$($pr.number): $($pr.html_url)"
Write-Output "Briefing: health/briefings/$Date.json  •  Sections: $($briefing.sections.Count)"
