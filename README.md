# LM Studio Local Chatbot

A Python toolkit for interacting with LM Studio's local API to run and manage LLM-based chatbots. This project provides an easy-to-use interface for loading models, conducting conversations, and experimenting with local language models.

## Features

- 🤖 **Interactive Chat Interface** - Beautiful CLI interface with rich formatting
- 🔧 **Configurable Settings** - YAML-based configuration for easy customization
- 📝 **Conversation History** - Save and review chat histories
- 📊 **Jupyter Notebook Integration** - Experiment and test in Jupyter notebooks
- 🔌 **LM Studio API Integration** - Seamless connection to local LM Studio server
- 📋 **Logging** - Comprehensive logging for debugging and monitoring

## Project Structure

```
lm-studio-local-chatbot/
├── src/                    # Source code
│   └── chatbot.py         # Main chatbot implementation
├── configs/               # Configuration files
│   └── config.yaml        # Example configuration
├── notebooks/             # Jupyter notebooks for testing
│   └── chatbot_testing.ipynb
├── logs/                  # Runtime logs and conversation histories
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## Prerequisites

- Python 3.8 or higher
- [LM Studio](https://lmstudio.ai/) installed and running locally
- A language model loaded in LM Studio

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/SimplyAISolution/lm-studio-local-chatbot.git
   cd lm-studio-local-chatbot
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure the chatbot:**
   - Edit `configs/config.yaml` to match your LM Studio setup
   - Default API URL is `http://localhost:1234`

## LM Studio Setup

1. **Download and install LM Studio** from [lmstudio.ai](https://lmstudio.ai/)

2. **Download a model:**
   - Open LM Studio
   - Browse and download a model (e.g., Llama 2, Mistral, etc.)

3. **Start the local server:**
   - In LM Studio, go to the "Local Server" tab
   - Click "Start Server"
   - Note the port (default: 1234)

4. **Load a model:**
   - Select your downloaded model
   - Click "Load Model"

## Usage

### Interactive Mode

Run the chatbot in interactive mode:

```bash
python src/chatbot.py
```

**Available commands:**
- `/models` - List available models in LM Studio
- `/load <model>` - Load a specific model
- `/clear` - Clear conversation history
- `/save <file>` - Save conversation to a file
- `/quit` or `/exit` - Exit the chatbot

### Command Line Options

```bash
# List available models
python src/chatbot.py --list-models

# Load a specific model
python src/chatbot.py --model "your-model-name"

# Use a custom configuration file
python src/chatbot.py --config path/to/config.yaml
```

### Jupyter Notebook

Explore and test the chatbot in a Jupyter notebook:

```bash
# Install Jupyter if not already installed
pip install jupyter

# Start Jupyter
jupyter notebook

# Open notebooks/chatbot_testing.ipynb
```

## Configuration

Edit `configs/config.yaml` to customize the chatbot behavior:

```yaml
# API URL for LM Studio
api_url: "http://localhost:1234"

# Model name (leave empty to select interactively)
model_name: ""

# Temperature (0.0 = deterministic, 1.0 = creative)
temperature: 0.7

# Maximum tokens in response
max_tokens: 1000

# System prompt
system_prompt: "You are a helpful AI assistant running locally via LM Studio."
```

## Examples

### Basic Chat

```python
from chatbot import LMStudioChatbot

# Initialize chatbot
chatbot = LMStudioChatbot()

# List and load a model
models = chatbot.list_models()
chatbot.load_model(models[0])

# Chat
response = chatbot.chat("Hello! How are you?")
print(response)
```

### Save Conversation

```python
# After chatting...
chatbot.save_conversation("logs/my_conversation.json")
```

### Adjust Parameters

```python
# Make responses more creative
chatbot.temperature = 0.9

# Limit response length
chatbot.max_tokens = 500
```

## Logging

Logs are automatically saved to `logs/chatbot.log` and include:
- API requests and responses
- Model loading events
- Error messages
- Conversation metadata

## Troubleshooting

### Connection Error

**Error:** `Error connecting to LM Studio API`

**Solution:**
- Ensure LM Studio is running
- Verify the local server is started in LM Studio
- Check that the API URL in `config.yaml` matches LM Studio's server port
- Default: `http://localhost:1234`

### No Models Found

**Error:** `No models found or unable to connect to LM Studio`

**Solution:**
- Load a model in LM Studio before running the chatbot
- Make sure the model is fully loaded (check LM Studio's status)

### Import Errors

**Error:** `ModuleNotFoundError`

**Solution:**
```bash
pip install -r requirements.txt
```

## Development

### Adding Features

The main chatbot class is in `src/chatbot.py`. Key methods:
- `list_models()` - Get available models
- `load_model()` - Load a specific model
- `chat()` - Send a message and get a response
- `clear_history()` - Reset conversation
- `save_conversation()` - Save chat history

### Testing

Use the Jupyter notebook in `notebooks/chatbot_testing.ipynb` for interactive testing and experimentation.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [LM Studio](https://lmstudio.ai/) - Local LLM runtime
- [Rich](https://github.com/Textualize/rich) - Beautiful terminal output
- The open-source LLM community

## Support

For issues, questions, or suggestions, please open an issue on GitHub.

---

**Note:** This tool requires LM Studio to be running locally. It does not include any models or replace LM Studio - it's a Python interface to make interaction easier.