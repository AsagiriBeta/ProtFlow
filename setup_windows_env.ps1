# ProtFlow Windows 环境设置脚本
# 提供多种安装策略

param(
    [ValidateSet("pip", "conda", "hybrid")]
    [string]$Method = "pip",
    [switch]$SkipESM,
    [switch]$Verbose
)

$ErrorActionPreference = "Continue"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "ProtFlow Windows 环境设置" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 检查 Python
$pythonCmd = "python"
try {
    $pythonVersion = & $pythonCmd --version 2>&1
    Write-Host "检测到 Python: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "错误: 未找到 Python！" -ForegroundColor Red
    exit 1
}

switch ($Method) {
    "pip" {
        Write-Host "使用 pip 安装方法..." -ForegroundColor Yellow
        Write-Host ""
        
        # 检查虚拟环境
        if (-not (Test-Path ".venv")) {
            Write-Host "创建虚拟环境..." -ForegroundColor Cyan
            & $pythonCmd -m venv .venv
        }
        
        $venvPython = ".venv\Scripts\python.exe"
        if (-not (Test-Path $venvPython)) {
            Write-Host "错误: 虚拟环境创建失败！" -ForegroundColor Red
            exit 1
        }
        
        Write-Host "升级 pip、setuptools、wheel..." -ForegroundColor Cyan
        & $venvPython -m pip install --upgrade pip setuptools wheel
        
        Write-Host ""
        Write-Host "安装基础依赖..." -ForegroundColor Cyan
        & $venvPython -m pip install numpy pandas biopython matplotlib scipy requests tqdm huggingface_hub
        
        if (-not $SkipESM) {
            Write-Host ""
            Write-Host "尝试安装 ESM（可能需要编译工具）..." -ForegroundColor Cyan
            Write-Host "如果失败，请安装 Visual C++ Build Tools 或使用 conda 方法" -ForegroundColor Yellow
            
            & $venvPython -m pip install 'esm>=3.2.1.post1'
            
            if ($LASTEXITCODE -ne 0) {
                Write-Host ""
                Write-Host "ESM 安装失败！" -ForegroundColor Red
                Write-Host "请选择以下方案之一:" -ForegroundColor Yellow
                Write-Host "  1. 安装 Visual C++ Build Tools 后重试" -ForegroundColor White
                Write-Host "  2. 使用 conda 方法: .\setup_windows_env.ps1 -Method conda" -ForegroundColor White
                Write-Host "  3. 跳过 ESM: .\setup_windows_env.ps1 -Method pip -SkipESM" -ForegroundColor White
            }
        }
        
        Write-Host ""
        Write-Host "安装其他依赖..." -ForegroundColor Cyan
        & $venvPython -m pip install -r requirements.txt
    }
    
    "conda" {
        Write-Host "使用 Conda 安装方法（推荐）..." -ForegroundColor Yellow
        Write-Host ""
        
        # 检查 conda
        $condaCmd = "conda"
        try {
            & $condaCmd --version | Out-Null
        } catch {
            Write-Host "错误: 未找到 Conda！" -ForegroundColor Red
            Write-Host "请安装 Anaconda 或 Miniconda" -ForegroundColor Yellow
            exit 1
        }
        
        $envName = "protflow"
        Write-Host "创建 Conda 环境: $envName" -ForegroundColor Cyan
        & $condaCmd create -n $envName python=3.12 -y
        
        Write-Host ""
        Write-Host "激活环境并安装依赖..." -ForegroundColor Cyan
        Write-Host "请手动运行以下命令:" -ForegroundColor Yellow
        Write-Host "  conda activate $envName" -ForegroundColor White
        Write-Host "  conda install -c conda-forge numpy pandas matplotlib scipy biopython -y" -ForegroundColor White
        Write-Host "  pip install -r requirements.txt" -ForegroundColor White
    }
    
    "hybrid" {
        Write-Host "使用混合方法（Conda + pip）..." -ForegroundColor Yellow
        Write-Host ""
        Write-Host "1. 使用 Conda 安装需要编译的包" -ForegroundColor Cyan
        Write-Host "   conda install -c conda-forge biotite -y" -ForegroundColor White
        Write-Host ""
        Write-Host "2. 使用 pip 安装其他包" -ForegroundColor Cyan
        Write-Host "   pip install -r requirements.txt" -ForegroundColor White
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "设置完成！" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
