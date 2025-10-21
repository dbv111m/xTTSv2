# PowerShell script to set up and run the TTS API project on Windows

# Create virtual environment if it doesn't exist
if (!(Test-Path ".venv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Green
    python -m venv .venv
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Green
& ".venv\Scripts\activate.bat"

# Install dependencies
Write-Host "Installing dependencies..." -ForegroundColor Green
pip install -r requirements.txt

# Create .env file if it doesn't exist
if (!(Test-Path ".env")) {
    Write-Host "Creating .env file from example..." -ForegroundColor Green
    Copy-Item .env.example .env
}

# Create outputs directory
if (!(Test-Path "outputs")) {
    Write-Host "Creating outputs directory..." -ForegroundColor Green
    New-Item -ItemType Directory -Path "outputs" | Out-Null
}

# Run the application
Write-Host "Starting TTS API server..." -ForegroundColor Green
Write-Host "API will be available at http://localhost:8000" -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
python main.py
