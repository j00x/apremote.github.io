<#
.SYNOPSIS
    Azure Automation runbook: generate an Azure blog post with Azure OpenAI and open a
    pull request on the GitHub Pages repo for review.

.DESCRIPTION
    Designed to run in an Azure Automation account on a schedule (e.g. weekly), using a
    system-assigned managed identity to read secrets from Key Vault. It:
      1. Reads a GitHub token (+ Azure OpenAI key) from Key Vault.
      2. Calls Azure OpenAI to generate a post that follows the agent instructions.
      3. Creates a branch, commits the post via the GitHub Contents API, and opens a PR.

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
    [ValidateSet('auto', 'how-to', 'lessons-learned')]
    [string] $Category       = 'auto',
    [string] $Topic          = ''
)

$ErrorActionPreference = 'Stop'

# --- 1. Auth & secrets ------------------------------------------------------
Connect-AzAccount -Identity | Out-Null
$ghToken  = (Get-AzKeyVaultSecret -VaultName $KeyVaultName -Name 'gh-pat-blog'  -AsPlainText)
$aoaiKey  = (Get-AzKeyVaultSecret -VaultName $KeyVaultName -Name 'aoai-api-key' -AsPlainText)

$ghHeaders = @{
    Authorization          = "Bearer $ghToken"
    'User-Agent'           = 'azure-blog-runbook'
    Accept                 = 'application/vnd.github+json'
    'X-GitHub-Api-Version' = '2022-11-28'
}
$apiBase = "https://api.github.com/repos/$GitHubOwner/$GitHubRepo"

# --- 2. Pull the agent instructions + memory from the repo ------------------
function Get-RepoText([string] $Path) {
    $uri = "$apiBase/contents/$Path"
    $r = Invoke-RestMethod -Method Get -Uri $uri -Headers $ghHeaders
    [Text.Encoding]::UTF8.GetString([Convert]::FromBase64String($r.content))
}
$instructions = Get-RepoText 'automation/azure-blog-agent.md'
$memories     = Get-RepoText 'automation/azure-memories.md'

# --- 3. Generate the post with Azure OpenAI ---------------------------------
$catLine = if ($Category -in @('how-to', 'lessons-learned')) { $Category }
           else { "choose 'how-to' or 'lessons-learned', alternating based on the running log" }
$topicLine = if ($Topic) { $Topic } else { 'choose a fresh topic from the backlog NOT already in the running log' }

$system = "$instructions`n`n---`nLONG-TERM MEMORY (authoritative for topics/voice/rules):`n$memories"
$userMsg = @"
Write today's Azure blog post following the instructions and memory above.
- Category: $catLine
- Topic: $topicLine

Return ONLY a JSON object with keys:
  title (string), category ('how-to'|'lessons-learned'), tags (array of lowercase strings),
  summary (one sentence, < 160 chars), body_markdown (full Markdown body with language-tagged
  fenced code blocks; do NOT include YAML front matter).
"@

$aoaiUri  = "$($AoaiEndpoint.TrimEnd('/'))/openai/deployments/$AoaiDeployment/chat/completions?api-version=$AoaiApiVersion"
$aoaiBody = @{
    messages        = @(
        @{ role = 'system'; content = $system },
        @{ role = 'user';   content = $userMsg }
    )
    response_format = @{ type = 'json_object' }
    temperature     = 0.4
} | ConvertTo-Json -Depth 6

$aoaiResp = Invoke-RestMethod -Method Post -Uri $aoaiUri `
    -Headers @{ 'api-key' = $aoaiKey; 'Content-Type' = 'application/json' } -Body $aoaiBody
$post = $aoaiResp.choices[0].message.content | ConvertFrom-Json

if ($post.category -notin @('how-to', 'lessons-learned')) {
    throw "Model returned invalid category: '$($post.category)'"
}

# --- 4. Build the post file -------------------------------------------------
$date  = (Get-Date).ToString('yyyy-MM-dd')
$slug  = ($post.title.ToLower() -replace '[^a-z0-9]+', '-').Trim('-')
if ($slug.Length -gt 60) { $slug = $slug.Substring(0, 60).Trim('-') }
$path  = "_posts/$date-$slug.md"
$tags  = ($post.tags -join ', ')
$title = $post.title -replace '"', "'"
$summary = ($post.summary -replace '"', "'")

$fileText = @"
---
title: "$title"
category: $($post.category)
tags: [$tags]
summary: "$summary"
---

$($post.body_markdown.TrimEnd())
"@

# --- 5. Create a branch, commit the file, open a PR -------------------------
$branch = "bot/azure-post-$date-$(Get-Random -Maximum 9999)"
$mainRef = Invoke-RestMethod -Method Get -Uri "$apiBase/git/ref/heads/main" -Headers $ghHeaders
$baseSha = $mainRef.object.sha

Invoke-RestMethod -Method Post -Uri "$apiBase/git/refs" -Headers $ghHeaders -Body (
    @{ ref = "refs/heads/$branch"; sha = $baseSha } | ConvertTo-Json
) | Out-Null

$contentB64 = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($fileText))
Invoke-RestMethod -Method Put -Uri "$apiBase/contents/$path" -Headers $ghHeaders -Body (
    @{ message = "azure: add $($post.category) post — $title"; content = $contentB64; branch = $branch } | ConvertTo-Json
) | Out-Null

$pr = Invoke-RestMethod -Method Post -Uri "$apiBase/pulls" -Headers $ghHeaders -Body (
    @{
        title = "azure: $title"
        head  = $branch
        base  = 'main'
        body  = "Automated draft from the Azure Blog Agent runbook.`n`n- File: ``$path```n- Category: ``$($post.category)```n`nReview, then merge to publish."
        draft = $true
    } | ConvertTo-Json
)

Write-Output "Opened PR #$($pr.number): $($pr.html_url)"
Write-Output "Post file: $path"
# Tip: to also append to automation/azure-memories.md, fetch it (with its sha), insert a
# running-log line, and PUT it on the same branch before opening the PR.
