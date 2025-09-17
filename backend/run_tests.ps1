# AI Integration Test Runner Script (PowerShell)
# Runs all AI integration tests and generates reports

Write-Host "🚀 AI Integration Test Suite Runner" -ForegroundColor Green
Write-Host "==================================" -ForegroundColor Green

# Check if we're in the right directory
if (-not (Test-Path "quick_ai_test.py")) {
    Write-Host "❌ Error: Please run this script from the backend directory" -ForegroundColor Red
    exit 1
}

# Check if .env file exists
if (-not (Test-Path ".env")) {
    Write-Host "❌ Error: .env file not found. Please create it with your OpenAI API key:" -ForegroundColor Red
    Write-Host "   OPENAI_API_KEY=your_key_here" -ForegroundColor Yellow
    exit 1
}

# Check if Python dependencies are installed
Write-Host "📦 Checking dependencies..." -ForegroundColor Blue
try {
    python -c "import openai, sqlalchemy, fastapi" 2>$null
    if ($LASTEXITCODE -ne 0) {
        throw "Dependencies not installed"
    }
    Write-Host "✅ Dependencies check passed" -ForegroundColor Green
} catch {
    Write-Host "❌ Error: Required dependencies not installed. Please run:" -ForegroundColor Red
    Write-Host "   pip install openai sqlalchemy fastapi python-dotenv" -ForegroundColor Yellow
    exit 1
}

# Run quick test first
Write-Host ""
Write-Host "🧪 Running Quick AI Test..." -ForegroundColor Blue
python quick_ai_test.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Quick test failed. Please fix issues before running full test suite." -ForegroundColor Red
    exit 1
}

Write-Host "✅ Quick test passed" -ForegroundColor Green

# Ask user if they want to run full test suite
Write-Host ""
$response = Read-Host "🤔 Run full test suite? This will take several minutes (y/n)"
if ($response -match "^[Yy]$") {
    Write-Host ""
    Write-Host "🧪 Running Full Test Suite..." -ForegroundColor Blue
    Write-Host "This may take 5-10 minutes..." -ForegroundColor Yellow
    
    python tests/run_all_tests.py
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "🎉 ALL TESTS COMPLETED SUCCESSFULLY!" -ForegroundColor Green
        Write-Host "📄 Check the generated report files:" -ForegroundColor Blue
        Write-Host "   - comprehensive_ai_test_report.json" -ForegroundColor Cyan
        Write-Host "   - ai_integration_test_report.json" -ForegroundColor Cyan
        Write-Host "   - api_endpoint_test_report.json" -ForegroundColor Cyan
        Write-Host "   - real_world_scenarios_test_report.json" -ForegroundColor Cyan
        Write-Host "   - performance_test_report.json" -ForegroundColor Cyan
    } else {
        Write-Host ""
        Write-Host "❌ SOME TESTS FAILED!" -ForegroundColor Red
        Write-Host "📄 Check the report files for details" -ForegroundColor Yellow
        exit 1
    }
} else {
    Write-Host "✅ Quick test completed successfully" -ForegroundColor Green
    Write-Host "💡 Run 'python tests/run_all_tests.py' for full test suite" -ForegroundColor Blue
}

Write-Host ""
Write-Host "🏁 Test execution completed" -ForegroundColor Green
