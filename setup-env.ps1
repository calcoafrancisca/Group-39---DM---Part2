# setup-env.ps1
# Usage: Run this script from PowerShell (not Admin) in the repo root.
# It attempts to create the Conda environment from environment.yml and register a Jupyter kernel.

$envFile = Join-Path -Path (Get-Location) -ChildPath 'environment.yml'
if (-Not (Test-Path $envFile)) {
    Write-Error "environment.yml not found in current directory: $envFile"
    exit 1
}

# Check if conda is available
$condamsg = & conda --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "Conda not found on PATH." -ForegroundColor Yellow
    Write-Host "Please install Miniconda or Anaconda and re-open this PowerShell session (or run from Anaconda Prompt)."
    Write-Host "Miniconda: https://docs.conda.io/en/latest/miniconda.html"
    Write-Host "After installing, run these commands manually:"
    Write-Host "  conda env create -f .\environment.yml"
    Write-Host "  conda activate dm_project"
    Write-Host "  python -m ipykernel install --user --name=dm_project --display-name \"Python (dm_project)\""
    exit 2
}

# Create environment
Write-Host "Creating conda environment from $envFile..." -ForegroundColor Cyan
& conda env create -f $envFile
if ($LASTEXITCODE -ne 0) {
    Write-Error "conda env create failed (exit code $LASTEXITCODE). Check the output above for details."
    exit $LASTEXITCODE
}

Write-Host "Activating environment 'dm_project'..." -ForegroundColor Cyan
# Activation in a script: use conda run if activation in-script isn't available
& conda activate dm_project 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "conda activate failed in script; continuing and attempting to register kernel with current Python." -ForegroundColor Yellow
}

Write-Host "Registering Jupyter kernel 'dm_project'..." -ForegroundColor Cyan
& python -m ipykernel install --user --name=dm_project --display-name "Python (dm_project)"
if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to register Jupyter kernel (exit code $LASTEXITCODE)."
    exit $LASTEXITCODE
}

Write-Host "Done. To use the environment, run:`n  conda activate dm_project`" -ForegroundColor Green
