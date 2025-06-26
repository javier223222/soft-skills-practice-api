# Development startup script for Soft Skill Practice Service (PowerShell)

Write-Host "🚀 Starting Soft Skill Practice Service Development Environment" -ForegroundColor Green

# Check if Docker is running
try {
    docker info | Out-Null
} catch {
    Write-Host "❌ Docker is not running. Please start Docker and try again." -ForegroundColor Red
    exit 1
}

# Check if .env file exists
if (-not (Test-Path ".env")) {
    Write-Host "📝 Creating .env file from example..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host "✅ .env file created. Please review and update the configuration if needed." -ForegroundColor Green
}

# Build and start services
Write-Host "🏗️ Building and starting services..." -ForegroundColor Blue
docker-compose up -d --build

# Wait for services to be ready
Write-Host "⏳ Waiting for services to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Check if database is ready
Write-Host "🔍 Checking database connection..." -ForegroundColor Blue
do {
    $dbReady = docker-compose exec -T postgres pg_isready -U postgres 2>$null
    if (-not $dbReady) {
        Write-Host "Waiting for database..." -ForegroundColor Yellow
        Start-Sleep -Seconds 2
    }
} while (-not $dbReady)

Write-Host "✅ Database is ready!" -ForegroundColor Green

# Populate initial data
Write-Host "📚 Populating initial data..." -ForegroundColor Blue
docker-compose exec api python scripts/populate_data.py

# Show service status
Write-Host "📊 Service Status:" -ForegroundColor Cyan
docker-compose ps

# Show useful URLs
Write-Host ""
Write-Host "🌐 Service URLs:" -ForegroundColor Cyan
Write-Host "  • API Documentation (Swagger): http://localhost:8000/docs" -ForegroundColor White
Write-Host "  • API Documentation (ReDoc): http://localhost:8000/redoc" -ForegroundColor White
Write-Host "  • Health Check: http://localhost:8000/health/" -ForegroundColor White
Write-Host "  • PostgreSQL: localhost:5432 (postgres/postgres)" -ForegroundColor White
Write-Host ""
Write-Host "🎉 Development environment is ready!" -ForegroundColor Green
Write-Host ""
Write-Host "📝 Useful commands:" -ForegroundColor Cyan
Write-Host "  • View logs: docker-compose logs -f" -ForegroundColor White
Write-Host "  • Stop services: docker-compose down" -ForegroundColor White
Write-Host "  • Restart API: docker-compose restart api" -ForegroundColor White
Write-Host "  • Run tests: docker-compose exec api pytest tests/" -ForegroundColor White
