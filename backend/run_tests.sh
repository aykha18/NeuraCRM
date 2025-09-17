#!/bin/bash

# AI Integration Test Runner Script
# Runs all AI integration tests and generates reports

echo "🚀 AI Integration Test Suite Runner"
echo "=================================="

# Check if we're in the right directory
if [ ! -f "quick_ai_test.py" ]; then
    echo "❌ Error: Please run this script from the backend directory"
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ Error: .env file not found. Please create it with your OpenAI API key:"
    echo "   OPENAI_API_KEY=your_key_here"
    exit 1
fi

# Check if Python dependencies are installed
echo "📦 Checking dependencies..."
python -c "import openai, sqlalchemy, fastapi" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ Error: Required dependencies not installed. Please run:"
    echo "   pip install openai sqlalchemy fastapi python-dotenv"
    exit 1
fi

echo "✅ Dependencies check passed"

# Run quick test first
echo ""
echo "🧪 Running Quick AI Test..."
python quick_ai_test.py
if [ $? -ne 0 ]; then
    echo "❌ Quick test failed. Please fix issues before running full test suite."
    exit 1
fi

echo "✅ Quick test passed"

# Ask user if they want to run full test suite
echo ""
read -p "🤔 Run full test suite? This will take several minutes (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "🧪 Running Full Test Suite..."
    echo "This may take 5-10 minutes..."
    
    python tests/run_all_tests.py
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "🎉 ALL TESTS COMPLETED SUCCESSFULLY!"
        echo "📄 Check the generated report files:"
        echo "   - comprehensive_ai_test_report.json"
        echo "   - ai_integration_test_report.json"
        echo "   - api_endpoint_test_report.json"
        echo "   - real_world_scenarios_test_report.json"
        echo "   - performance_test_report.json"
    else
        echo ""
        echo "❌ SOME TESTS FAILED!"
        echo "📄 Check the report files for details"
        exit 1
    fi
else
    echo "✅ Quick test completed successfully"
    echo "💡 Run 'python tests/run_all_tests.py' for full test suite"
fi

echo ""
echo "🏁 Test execution completed"
