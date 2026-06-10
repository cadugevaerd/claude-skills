<#
.SYNOPSIS
    Instala skills deste repositório no Claude Code globalmente (~/.claude/skills).

.DESCRIPTION
    Descobre as skills disponíveis no repositório (pasta skills/), permite
    selecionar quais instalar e as baixa para ~/.claude/skills, tornando-as
    disponíveis em qualquer sessão do Claude Code.

    Uso remoto (uma linha):
      irm https://raw.githubusercontent.com/cadugevaerd/claude-skills/main/install.ps1 | iex

    Uso local:
      .\install.ps1                       # menu interativo de seleção
      .\install.ps1 -Skills backlog       # instala apenas uma, sem menu
      .\install.ps1 -Skills all           # todas, sem menu
      .\install.ps1 -Force                # sobrescreve sem perguntar

.PARAMETER Skills
    Quais skills instalar (nomes das pastas em skills/, ou 'all').
    Sem o parâmetro, abre o menu de seleção.

.PARAMETER Force
    Sobrescreve skills já instaladas sem pedir confirmação.

.PARAMETER Ref
    Branch ou tag do repositório a baixar. Padrão: main.
#>
[CmdletBinding()]
param(
    [string[]] $Skills,
    [switch]   $Force,
    [string]   $Ref = 'main'
)

$ErrorActionPreference = 'Stop'

$Repo       = 'cadugevaerd/claude-skills'
$SkillsRoot = Join-Path $HOME '.claude\skills'

function Write-Step([string]$msg) { Write-Host "==> $msg" -ForegroundColor Cyan }
function Write-Ok([string]$msg)   { Write-Host "    $msg" -ForegroundColor Green }
function Write-Warn([string]$msg) { Write-Host "    $msg" -ForegroundColor Yellow }

# --- Descobre dinamicamente as skills e seus arquivos (GitHub API) ---
# Layout do repo: plugins/<plugin>/skills/<skill>/<arquivos>
Write-Step "Consultando skills disponíveis em $Repo@$Ref"
$tree = Invoke-RestMethod -Uri "https://api.github.com/repos/$Repo/git/trees/${Ref}?recursive=1" -UseBasicParsing
$skillFiles = @{}
$skillUrlBase = @{}
foreach ($item in $tree.tree) {
    if ($item.type -eq 'blob' -and $item.path -match '^(plugins/[^/]+/skills/([^/]+))/(.+)$') {
        $base = $Matches[1]
        $name = $Matches[2]
        $rel  = $Matches[3]
        if (-not $skillFiles.ContainsKey($name)) { $skillFiles[$name] = @(); $skillUrlBase[$name] = $base }
        $skillFiles[$name] += $rel
    }
}
$available = @($skillFiles.Keys | Sort-Object)
if ($available.Count -eq 0) { throw "Nenhuma skill encontrada em $Repo (pasta plugins/*/skills/)." }

# --- Resolve a seleção ---
if ($Skills) {
    if ($Skills -contains 'all') {
        $targets = $available
    }
    else {
        $invalid = @($Skills | Where-Object { $_ -notin $available })
        if ($invalid.Count -gt 0) {
            throw "Skill(s) inexistente(s): $($invalid -join ', '). Disponíveis: $($available -join ', ')"
        }
        $targets = $Skills
    }
}
else {
    Write-Host ""
    Write-Host "Skills disponíveis:" -ForegroundColor Cyan
    for ($i = 0; $i -lt $available.Count; $i++) {
        $mark = ''
        if (Test-Path (Join-Path $SkillsRoot $available[$i])) { $mark = '  (já instalada)' }
        Write-Host ("  [{0}] {1}{2}" -f ($i + 1), $available[$i], $mark)
    }
    Write-Host ""
    $answer = Read-Host "Quais instalar? (números separados por vírgula, ou Enter = todas)"
    if ([string]::IsNullOrWhiteSpace($answer)) {
        $targets = $available
    }
    else {
        $targets = @()
        foreach ($n in ($answer -split '[,\s]+' | Where-Object { $_ })) {
            $idx = [int]$n - 1
            if ($idx -lt 0 -or $idx -ge $available.Count) { throw "Opção inválida: $n" }
            $targets += $available[$idx]
        }
        $targets = @($targets | Select-Object -Unique)
    }
}

Write-Host ""
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

    foreach ($rel in $skillFiles[$skill]) {
        $url     = "https://raw.githubusercontent.com/$Repo/$Ref/$($skillUrlBase[$skill])/$rel"
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
