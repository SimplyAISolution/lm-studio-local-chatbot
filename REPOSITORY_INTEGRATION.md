# LM Studio Repository Integration Guide

This guide explains how to set up LM Studio to interact directly with your repository, allowing the AI to read files, write code, run tests, and manage your project.

## 🎯 Overview

The Repository Interface creates a REST API that LM Studio can use to:
- 📁 **Read repository structure** and understand your codebase
- 📖 **Read any file** in your project
- ✏️ **Write and modify files** with automatic backups
- 🔍 **Search for code** across all files
- 🧪 **Run tests** to verify changes
- 📊 **Check git status** and track changes

## 🚀 Quick Setup

### 1. Install Dependencies
```bash
# Run the setup script
python setup.py

# Or install manually
pip install -r requirements.txt
```

### 2. Start the Repository Interface
```bash
# Start the API server
python start_repo_interface.py

# Or run directly
python repository_interface.py
```

The interface will start on `http://localhost:8080` by default.

### 3. Test the Connection
```bash
# Test if the interface is working
python start_repo_interface.py --test
```

## 🔧 LM Studio Configuration

### Method 1: Tool Configuration (Recommended)

1. **Open LM Studio**
2. **Go to Settings/Tools** (if available in your version)
3. **Import Tool Configuration**:
   - Use the file: `lm_studio_tools.json`
   - This defines all available repository operations

4. **Load System Prompt**:
   - Copy content from `system_prompt.md`
   - Paste into LM Studio's system prompt field
   - This teaches the AI how to use the repository tools

### Method 2: Manual Prompt Setup

If your LM Studio version doesn't support tool configurations, you can still use the repository interface by including these instructions in your conversation:

```
You have access to a repository management API at http://localhost:8080. 

Available endpoints:
- GET /api/repository/structure - Get repository structure
- GET /api/repository/file?path=<file_path> - Read a file
- POST /api/repository/file - Write a file (JSON: {"path": "file.py", "content": "code"})
- GET /api/repository/search?query=<search_term> - Search files
- POST /api/repository/tests - Run tests
- GET /api/repository/git/status - Get git status

Use these endpoints to help with code analysis, debugging, and development tasks.
```

## 📋 Usage Examples

### Analyzing Code
```
User: "Can you analyze my Python project structure?"

LM Studio will:
1. Call GET /api/repository/structure
2. Examine the layout
3. Read key files like main.py, requirements.txt
4. Provide analysis and suggestions
```

### Fixing Bugs
```
User: "There's a bug in my authentication module"

LM Studio will:
1. Search for authentication-related files
2. Read the relevant code
3. Identify the issue
4. Write the fix with automatic backup
5. Run tests to verify the fix
```

### Adding Features
```
User: "Add a new user registration endpoint"

LM Studio will:
1. Examine existing endpoint patterns
2. Read related files (models, routes, etc.)
3. Write the new endpoint code
4. Update related files as needed
5. Run tests to ensure everything works
```

## ⚙️ Configuration Options

### Environment Variables (.env file)
```env
# Repository Interface
REPO_INTERFACE_PORT=8080  # Change if port 8080 is in use
DEBUG=false               # Set to true for debugging

# LM Studio Connection  
LM_STUDIO_BASE_URL=http://localhost:1234/v1
LM_STUDIO_API_KEY=lm-studio
```

### Security Settings

The repository interface includes safety features:
- **Path restrictions**: Only accesses files within the repository
- **File type filtering**: Only reads/writes approved file types (.py, .md, .txt, etc.)
- **Automatic backups**: Creates backups before modifying files
- **Read-only mode**: Can be configured to prevent file modifications

## 🛠️ Troubleshooting

### Common Issues

1. **"Connection refused" errors**
   ```bash
   # Check if interface is running
   python start_repo_interface.py --test
   
   # Restart the interface
   python start_repo_interface.py
   ```

2. **Port conflicts**
   ```bash
   # Change port in .env file
   REPO_INTERFACE_PORT=8081
   ```

3. **Permission errors**
   - Ensure Python has read/write access to repository
   - Run with appropriate permissions
   - Check file ownership

4. **LM Studio not using tools**
   - Verify tool configuration is loaded
   - Check system prompt is set correctly
   - Ensure LM Studio version supports function calling

### Debug Mode

Enable debug mode for detailed logging:
```bash
# Set in .env file
DEBUG=true

# Or set environment variable
export DEBUG=true
python start_repo_interface.py
```

## 🔄 Workflow Examples

### Daily Development
1. Start Repository Interface: `python start_repo_interface.py`
2. Start LM Studio with repository tools loaded
3. Ask LM Studio to help with your coding tasks
4. LM Studio can now read, write, test, and manage your code

### Code Review
```
"Please review the changes in my authentication module and suggest improvements"
```
- LM Studio reads the files
- Analyzes the code quality
- Suggests improvements
- Can even implement the changes

### Testing and Debugging
```
"Run the tests and fix any failures"
```
- LM Studio runs your test suite
- Identifies failing tests
- Reads the problematic code
- Implements fixes
- Re-runs tests to verify

## 📊 API Reference

### Repository Structure
```http
GET /api/repository/structure?max_depth=3
```
Returns the directory tree and file information.

### File Operations
```http
# Read file
GET /api/repository/file?path=src/main.py&start_line=10&end_line=20

# Write file
POST /api/repository/file
Content-Type: application/json
{
  "path": "src/new_feature.py",
  "content": "def new_function():\n    pass",
  "backup": true
}
```

### Search
```http
GET /api/repository/search?query=authentication&file_types=.py&file_types=.md
```

### Testing
```http
POST /api/repository/tests
```

### Git Status
```http
GET /api/repository/git/status
```

## 🎉 Benefits

With this setup, LM Studio becomes a powerful coding assistant that can:
- **Understand your entire codebase** context
- **Make informed decisions** based on existing code patterns  
- **Implement changes safely** with automatic backups
- **Test changes immediately** to catch issues early
- **Follow your coding style** by analyzing existing code
- **Work with git** to track and manage changes

## 📞 Support

If you encounter issues:
1. Check the troubleshooting section above
2. Review the debug logs (enable with `DEBUG=true`)
3. Test the API endpoints manually with curl or a browser
4. Ensure all dependencies are installed correctly

The Repository Interface bridges the gap between LM Studio and your codebase, creating a powerful development environment where AI can actively participate in your coding workflow.