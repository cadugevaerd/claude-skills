<#
.SYNOPSIS
    Instala APENAS a skill grillme-gestor no Claude Code, globalmente.

.DESCRIPTION
    Versao simplificada do instalador, voltada ao gestor / usuario nao-tecnico.
    Baixa somente a skill grillme-gestor para ~/.claude/skills e a deixa
    disponivel em qualquer sessao do Claude Code.

    Uso (uma linha no PowerShell):
      irm https://raw.githubusercontent.com/cadugevaerd/claude-skills/main/install-gestor.ps1 | iex
#>
[CmdletBinding()]
param(
    [switch] $Force,
    [string] $Ref = 'main'
)

$ErrorActionPreference = 'Stop'

$Repo       = 'cadugevaerd/claude-skills'
$Skill      = 'grillme-gestor'
$SkillsRoot = Join-Path $HOME '.claude\skills'
$Dest       = Join-Path $SkillsRoot $Skill

$SkillFiles = @(
    'SKILL.md',
    'references/padrao-langgraph.md',
    'assets/template-saida.md'
)

function Write-Step([string]$m) { Write-Host "==> $m" -ForegroundColor Cyan }
function Write-Ok([string]$m)   { Write-Host "    $m" -ForegroundColor Green }
function Write-Warn([string]$m) { Write-Host "    $m" -ForegroundColor Yellow }

Write-Step "Instalando a skill '$Skill' no Claude Code"
Write-Host "    Destino: $Dest"
Write-Host ""

if ((Test-Path $Dest) -and -not $Force) {
    $answer = Read-Host "    '$Skill' ja existe. Sobrescrever? (s/N)"
    if ($answer -notmatch '^[sSyY]') { Write-Warn "Cancelado."; return }
}

New-Item -ItemType Directory -Force -Path $Dest | Out-Null

foreach ($rel in $SkillFiles) {
    $url     = "https://raw.githubusercontent.com/$Repo/$Ref/skills/$Skill/$rel"
    $outPath = Join-Path $Dest ($rel -replace '/', '\')
    New-Item -ItemType Directory -Force -Path (Split-Path $outPath -Parent) | Out-Null
    try {
        Invoke-WebRequest -Uri $url -OutFile $outPath -UseBasicParsing
        Write-Ok "baixado: $rel"
    }
    catch {
        Write-Warn "FALHOU: $rel"
        throw
    }
}

Write-Host ""
Write-Step "Concluido."
Write-Host "    Abra (ou reinicie) o Claude Code e use:  /grillme-gestor" -ForegroundColor Green
