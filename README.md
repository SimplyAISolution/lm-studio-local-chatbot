# LM Studio Local Chatbot

A comprehensive toolkit for building and running local chatbots using LM Studio. This project provides multiple interfaces (CLI and Web UI) to interact with locally hosted Large Language Models through LM Studio's API.

## 🚀 Features

- **Multiple Interfaces**: Command-line and web-based chat interfaces
- **LM Studio Integration**: Seamless connection to LM Studio's local API
- **Repository Interface**: Allow LM Studio to interact with your codebase directly
- **Persistent Memory System**: LM Studio can remember conversations, facts, and learn from interactions
- **Streaming Responses**: Real-time streaming for better user experience
- **Model Management**: Support for multiple models and easy switching
- **Conversation History**: Persistent chat history during sessions
- **Configurable Parameters**: Adjustable temperature, max tokens, and other settings

## 📋 Prerequisites

1. **LM Studio**: Download and install from [lmstudio.ai](https://lmstudio.ai/)
2. **Python 3.7+**: Required for running the chatbot interfaces
3. **A Local Model**: Download any compatible model in LM Studio

## 🛠️ Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/SimplyAISolution/lm-studio-local-chatbot.git
   cd lm-studio-local-chatbot
   ```

2. **Run the setup script**:
   ```bash
   python setup.py
   ```

   Or manually install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment** (optional):
   ```bash
   copy .env.example .env
   # Edit .env file with your preferences
   ```

## 🔧 LM Studio Setup

1. **Start LM Studio**
2. **Load a model**:
   - Go to the "My Models" tab
   - Select and load your preferred model
3. **Start the local server**:
   - Go to the "Local Server" tab
   - Click "Start Server"
   - Default URL: `http://localhost:1234`

## 🎯 Usage

### Repository Interface (NEW!)

**Allow LM Studio to interact directly with your codebase:**

```bash
# Start the repository interface
python start_repo_interface.py

# Test the connection
python start_repo_interface.py --test
```

**Repository Interface Features:**
- LM Studio can read, write, and analyze your code
- Automatic file backups before modifications
- Code search across the entire repository
- Run tests and check git status
- Safe file operations with security restrictions

See [REPOSITORY_INTEGRATION.md](REPOSITORY_INTEGRATION.md) for detailed setup instructions.

### Memory System (NEW!)

**Persistent memory for LM Studio to remember across sessions:**

```bash
# Memory is automatically available with the repository interface
# No additional setup required!

# Use the memory CLI tool
python memory_cli.py stats                    # View memory statistics
python memory_cli.py conversations --query="auth"  # Search conversations
python memory_cli.py facts --category="api"   # Search facts
python memory_cli.py interactive              # Interactive memory explorer
```

**Memory Features:**
- Remembers conversations, user preferences, and project details
- Learns from interactions to provide better assistance
- Stores important facts and coding patterns
- Searchable memory with categories and tags
- Automatic cleanup of expired information

See [memory/README.md](memory/README.md) for detailed memory system documentation.

### Command Line Interface

Run the CLI chatbot:
```bash
python chatbot_cli.py
```

**CLI Commands**:
- `quit` or `exit`: End the conversation
- `clear`: Clear conversation history
- `models`: Show available models

### Web Interface (Streamlit)

Run the web interface:
```bash
streamlit run streamlit_app.py
```

**Web Interface Features**:
- Real-time chat interface
- Model selection dropdown
- Adjustable parameters (temperature, max tokens)
- Clear conversation button
- Connection status indicator

## ⚙️ Configuration

### Environment Variables

Create a `.env` file (copy from `.env.example`) to customize settings:

```env
# LM Studio Configuration
LM_STUDIO_BASE_URL=http://localhost:1234/v1
LM_STUDIO_API_KEY=lm-studio

# Model Configuration
DEFAULT_MODEL=local-model
MAX_TOKENS=1000
TEMPERATURE=0.7
STREAM_RESPONSES=true

# UI Configuration
APP_TITLE=LM Studio Local Chatbot
APP_PORT=8501
```

### Parameters

- **Temperature** (0.0-2.0): Controls response randomness
- **Max Tokens**: Maximum length of responses
- **Stream**: Enable/disable streaming responses

## 🔌 API Reference

### LMStudioClient

The main client class for interacting with LM Studio:

```python
from lm_studio_client import create_client

# Create client
client = create_client()

# Check connection
if client.check_connection():
    print("Connected to LM Studio!")

# Get available models
models = client.get_models()

# Send chat message
response = client.chat_completion(
    messages=[{"role": "user", "content": "Hello!"}],
    temperature=0.7,
    max_tokens=1000,
    stream=False
)
```

### Streaming Example

```python
# Streaming response
response_gen = client.chat_completion(
    messages=[{"role": "user", "content": "Tell me a story"}],
    stream=True
)

for chunk in response_gen:
    print(chunk, end="", flush=True)
```

## 📁 Project Structure

```
lm-studio-local-chatbot/
│
├── README.md                      # This file
├── REPOSITORY_INTEGRATION.md      # Repository interface setup guide
├── requirements.txt               # Python dependencies
├── setup.py                      # Python setup script
├── setup.bat                     # Windows batch setup script
├── setup.ps1                     # PowerShell setup script
├── .env.example                  # Environment variables template
├── .gitignore                    # Git ignore rules
│
├── lm_studio_client.py           # LM Studio API client
├── chatbot_cli.py                # Command-line interface
├── streamlit_app.py              # Web interface (Streamlit)
├── gradio_app.py                 # Alternative web interface (Gradio)
├── test_connection.py            # Connection testing script
│
├── repository_interface.py       # Repository API server
├── start_repo_interface.py       # Repository interface launcher
├── lm_studio_tools.json          # Tool configuration for LM Studio
├── system_prompt.md              # System prompt for repository access
│
└── .env                          # Your environment variables (create from .env.example)
```

## 🛠️ Troubleshooting

### Common Issues

1. **"Cannot connect to LM Studio"**
   - Ensure LM Studio is running
   - Verify a model is loaded
   - Check that the local server is started
   - Confirm the URL (default: http://localhost:1234)

2. **"No models found"**
   - Load a model in LM Studio
   - Restart the local server
   - Check LM Studio's model compatibility

3. **Slow responses**
   - Try a smaller model
   - Reduce max_tokens
   - Check your system resources

4. **Import errors**
   - Run `pip install -r requirements.txt`
   - Check Python version (3.7+ required)

### Debug Mode

Set environment variable for debugging:
```bash
export DEBUG=true
python chatbot_cli.py
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙋‍♀️ Support

- **Issues**: [GitHub Issues](https://github.com/SimplyAISolution/lm-studio-local-chatbot/issues)
- **Discussions**: [GitHub Discussions](https://github.com/SimplyAISolution/lm-studio-local-chatbot/discussions)
- **LM Studio Docs**: [LM Studio Documentation](https://lmstudio.ai/docs)

## 🌟 Acknowledgments

- [LM Studio](https://lmstudio.ai/) for providing an excellent local LLM platform
- [Streamlit](https://streamlit.io/) for the web interface framework
- The open-source community for inspiration and feedback

---

**Happy Chatting with Local AI! 🤖✨**
