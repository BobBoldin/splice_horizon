# tools/Convert-DocxToMd.ps1
<#
.SYNOPSIS
  Convert .docx chapters to Markdown under docs/episodes/chXX/draft.md using pandoc.
  PowerShell version for Windows users.
.EXAMPLE
  pwsh -File tools/Convert-DocxToMd.ps1 -Source "C:\Users\bobbo\OneDrive\Documents\bob\Splice_Horizon\chapters"
#>

param(
  [Parameter(Mandatory = $true)]
  [string]$Source
)

function Require-Command($name) {
  if (-not (Get-Command $name -ErrorAction SilentlyContinue)) {
    Write-Error "Required command not found: $name"
    exit 1
  }
}

Require-Command pandoc
Require-Command git

if (-not (Test-Path $Source -PathType Container)) {
  Write-Error "Source directory not found: $Source"
  exit 2
}

$root = (git rev-parse --show-toplevel) 2>$null
if (-not $root) { $root = (Get-Location).Path }

$outRoot = Join-Path $root "docs\episodes"
New-Item -ItemType Directory -Force -Path $outRoot | Out-Null

$docs = Get-ChildItem -Path $Source -Filter *.docx -File
if ($docs.Count -eq 0) {
  Write-Host "[done] No .docx files in $Source"
  exit 0
}

$converted = @()

foreach ($f in $docs) {
  $base = $f.Name
  $num = $null
  if ($base -match '(?i)ch(apter)?[ _-]*([0-9]+)') { $num = $Matches[2] }
  elseif ($base -match '([0-9]{1,2})') { $num = $Matches[1] }

  if (-not $num) {
    Write-Warning "Could not detect chapter number from '$base'; skipping."
    continue
  }
  $num2 = "{0:d2}" -f [int]$num
  $outDir = Join-Path $outRoot ("ch" + $num2)
  New-Item -ItemType Directory -Force -Path $outDir | Out-Null
  $outMd = Join-Path $outDir "draft.md"

  Write-Host "[info] Converting: $base -> docs/episodes/ch$num2/draft.md"
  pandoc $f.FullName -o $outMd --wrap=none

  $readme = Join-Path $outDir "README.md"
  if (-not (Test-Path $readme)) {
    @"
# Chapter $num Checklist

- Target length: around two thousand five hundred words (plus or minus three hundred)
- No contractions, numbers spelled, no em dashes
- Dialogue conversational; narration carries senses
- Spoken transitions at scene shifts
"@ | Out-File -FilePath $readme -Encoding UTF8 -Force
  }

  $converted += $outMd
}

# Optional: run the linter if present
$lintPath = Join-Path $root "tools\lint_audio.py"
if (Test-Path $lintPath) {
  Write-Host "[info] Running audio linter on converted files..."
  python $lintPath $converted 2>$null
} else {
  Write-Host "[hint] Linter not found at tools/lint_audio.py; skip."
}

Write-Host "[done] Converted $($converted.Count) chapter(s)."
