# ESM3 安装脚本 - 使用 Conda（推荐方法）
# 避免 Windows 上的编译问题

$ErrorActionPreference = "Continue"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "ESM3 安装脚本（使用 Conda）" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 检查 Conda
$condaCmd = "conda"
try {
    $condaVersion = & $condaCmd --version 2>&1
    Write-Host "检测到 Conda: $condaVersion" -ForegroundColor Green
} catch {
    Write-Host "错误: 未找到 Conda！" -ForegroundColor Red
    Write-Host "请安装 Anaconda 或 Miniconda" -ForegroundColor Yellow
    Write-Host "下载地址: https://www.anaconda.com/download" -ForegroundColor Yellow
    exit 1
}

# 检查是否在虚拟环境中
if ($env:VIRTUAL_ENV) {
    Write-Host "警告: 检测到虚拟环境，建议使用 Conda 环境" -ForegroundColor Yellow
    Write-Host "当前虚拟环境: $env:VIRTUAL_ENV" -ForegroundColor Yellow
    Write-Host ""
    $continue = Read-Host "是否继续在当前环境安装？(y/n)"
    if ($continue -ne "y") {
        Write-Host "请创建 Conda 环境:" -ForegroundColor Cyan
        Write-Host "  conda create -n protflow python=3.12 -y" -ForegroundColor White
        Write-Host "  conda activate protflow" -ForegroundColor White
        Write-Host "  conda install -c conda-forge biotite -y" -ForegroundColor White
        Write-Host "  pip install esm>=3.2.1.post1" -ForegroundColor White
        exit 0
    }
}

Write-Host "步骤 1: 使用 Conda 安装 biotite（避免编译问题）..." -ForegroundColor Yellow
& $condaCmd install -c conda-forge biotite -y

if ($LASTEXITCODE -ne 0) {
    Write-Host "警告: Conda 安装 biotite 失败，尝试使用 pip..." -ForegroundColor Yellow
} else {
    Write-Host "✓ biotite 安装成功" -ForegroundColor Green
}

Write-Host ""
Write-Host "步骤 2: 使用 pip 安装 ESM..." -ForegroundColor Yellow
$pythonExe = if ($env:VIRTUAL_ENV) { "$env:VIRTUAL_ENV\Scripts\python.exe" } else { "python" }

& $pythonExe -m pip install --upgrade pip setuptools wheel
& $pythonExe -m pip install "esm>=3.2.1.post1"

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "✓ ESM3 安装成功！" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    
    Write-Host "验证安装:" -ForegroundColor Cyan
    & $pythonExe -c "import esm; print(f'ESM version: {esm.__version__}')" 2>&1
    & $pythonExe -c "from esm.models.esm3 import ESM3; print('ESM3 model class: OK')" 2>&1
    & $pythonExe -c "from esm.sdk.api import ESMProtein, GenerationConfig; print('ESM SDK: OK')" 2>&1
} else {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "安装失败！" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "建议使用 Conda 环境:" -ForegroundColor Yellow
    Write-Host "  conda create -n protflow python=3.12 -y" -ForegroundColor White
    Write-Host "  conda activate protflow" -ForegroundColor White
    Write-Host "  conda install -c conda-forge biotite -y" -ForegroundColor White
    Write-Host "  pip install esm>=3.2.1.post1" -ForegroundColor White
}
