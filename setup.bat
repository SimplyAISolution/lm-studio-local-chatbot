@echo off
echo 🚀 LM Studio Local Chatbot Setup
echo ================================

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python not found! Please install Python 3.7+ first.
    echo Download from: https://python.org/downloads/
    pause
    exit /b 1
)

echo ✅ Python found!

REM Install dependencies
echo 📦 Installing dependencies...
python -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ❌ Failed to install dependencies
    pause
    exit /b 1
)

REM Create .env file if it doesn't exist
if not exist ".env" (
    if exist ".env.example" (
        copy ".env.example" ".env"
        echo ✅ Created .env file from .env.example
    )
)

echo.
echo 🎉 Setup completed successfully!
echo.
echo Next steps:
echo 1. Start LM Studio and load a model
echo 2. Start the local server in LM Studio
echo 3. Run one of the interfaces:
echo    - CLI: python chatbot_cli.py
echo    - Web UI: streamlit run streamlit_app.py
echo    - Gradio UI: python gradio_app.py
echo.
echo To test the connection: python test_connection.py
echo.
pause