<#
.SYNOPSIS
    Instala as skills grillme-langgraph e grillme-gestor no Claude Code globalmente.

.DESCRIPTION
    Baixa as skills deste repositório do GitHub e as instala em ~/.claude/skills,
    tornando-as disponíveis em qualquer sessão do Claude Code.

    Uso remoto (uma linha):
      irm https://raw.githubusercontent.com/cadugevaerd/grillme-langgraph-skills/main/install.ps1 | iex

    Uso local:
      .\install.ps1
      .\install.ps1 -Skills grillme-gestor          # instala apenas uma
      .\install.ps1 -Force                           # sobrescreve sem perguntar

.PARAMETER Skills
    Quais skills instalar. Padrão: ambas.

.PARAMETER Force
    Sobrescreve skills já instaladas sem pedir confirmação.

.PARAMETER Ref
    Branch ou tag do repositório a baixar. Padrão: main.
#>
[CmdletBinding()]
param(
    [ValidateSet('grillme-langgraph', 'grillme-gestor', 'all')]
    [string[]] $Skills = @('all'),
    [switch]   $Force,
    [string]   $Ref = 'main'
)

$ErrorActionPreference = 'Stop'

$Repo        = 'cadugevaerd/grillme-langgraph-skills'
$SkillsRoot  = Join-Path $HOME '.claude\skills'
$AllSkills   = @('grillme-langgraph', 'grillme-gestor')

# Arquivos que compõem cada skill (mesmo layout para as duas).
$SkillFiles = @(
    'SKILL.md',
    'references/padrao-langgraph.md',
    'assets/template-saida.md'
)

function Write-Step([string]$msg) { Write-Host "==> $msg" -ForegroundColor Cyan }
function Write-Ok([string]$msg)   { Write-Host "    $msg" -ForegroundColor Green }
function Write-Warn([string]$msg) { Write-Host "    $msg" -ForegroundColor Yellow }

# Resolve a lista final de skills.
if ($Skills -contains 'all') { $targets = $AllSkills } else { $targets = $Skills }

Write-Step "Instalando skills do Claude Code: $($targets -join ', ')"
Write-Host "    Destino: $SkillsRoot"
Write-Host ""

New-Item -ItemType Directory -Force -Path $SkillsRoot | Out-Null

foreach ($skill in $targets) {
    Write-Step "Skill: $skill"
    $dest = Join-Path $SkillsRoot $skill

    if ((Test-Path $dest) -and -not $Force) {
        $answer = Read-Host "    '$skill' já existe. Sobrescrever? (s/N)"
        if ($answer -notmatch '^[sSyY]') { Write-Warn "Pulada."; continue }
    }

    foreach ($rel in $SkillFiles) {
        $url = "https://raw.githubusercontent.com/$Repo/$Ref/skills/$skill/$rel"
        $outPath = Join-Path $dest ($rel -replace '/', '\')
        $outDir  = Split-Path $outPath -Parent
        New-Item -ItemType Directory -Force -Path $outDir | Out-Null

        try {
            Invoke-WebRequest -Uri $url -OutFile $outPath -UseBasicParsing
            Write-Ok "baixado: $rel"
        }
        catch {
            Write-Warn "FALHOU: $rel ($url)"
            throw
        }
    }
    Write-Ok "Instalada em $dest"
    Write-Host ""
}

Write-Step "Concluído."
Write-Host "    Reinicie o Claude Code (ou abra uma nova sessão) e use:" -ForegroundColor Green
foreach ($skill in $targets) { Write-Host "      /$skill" -ForegroundColor Green }
