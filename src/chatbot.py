#!/usr/bin/env python3
"""
LM Studio Local Chatbot
A Python script to interact with LM Studio's local API for running LLM models.
"""

import requests
import json
import yaml
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

# Initialize rich console for beautiful output
console = Console()

# Setup logging
log_dir = Path(__file__).parent.parent / "logs"
log_dir.mkdir(exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / 'chatbot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class LMStudioChatbot:
    """
    A chatbot client for interacting with LM Studio's local API.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the chatbot with configuration.
        
        Args:
            config_path: Path to YAML configuration file
        """
        self.config = self._load_config(config_path)
        self.base_url = self.config.get('api_url', 'http://localhost:1234')
        self.model_name = self.config.get('model_name', None)
        self.temperature = self.config.get('temperature', 0.7)
        self.max_tokens = self.config.get('max_tokens', 1000)
        self.conversation_history: List[Dict[str, str]] = []
        
        logger.info(f"Initialized LM Studio Chatbot with base URL: {self.base_url}")
    
    def _load_config(self, config_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Load configuration from YAML file.
        
        Args:
            config_path: Path to configuration file
            
        Returns:
            Configuration dictionary
        """
        if config_path is None:
            config_path = Path(__file__).parent.parent / "configs" / "config.yaml"
        
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
                logger.info(f"Loaded configuration from {config_path}")
                return config
        except FileNotFoundError:
            logger.warning(f"Config file not found at {config_path}, using defaults")
            return {}
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            return {}
    
    def list_models(self) -> List[str]:
        """
        List available models from LM Studio API.
        
        Returns:
            List of available model names
        """
        try:
            response = requests.get(f"{self.base_url}/v1/models")
            response.raise_for_status()
            models_data = response.json()
            models = [model['id'] for model in models_data.get('data', [])]
            logger.info(f"Found {len(models)} available models")
            return models
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching models: {e}")
            console.print(f"[red]Error connecting to LM Studio API: {e}[/red]")
            return []
    
    def load_model(self, model_name: Optional[str] = None) -> bool:
        """
        Load a specific model in LM Studio.
        
        Args:
            model_name: Name of the model to load
            
        Returns:
            True if successful, False otherwise
        """
        if model_name:
            self.model_name = model_name
        
        if not self.model_name:
            logger.error("No model name specified")
            return False
        
        logger.info(f"Using model: {self.model_name}")
        console.print(f"[green]Model set to: {self.model_name}[/green]")
        return True
    
    def chat(self, message: str, stream: bool = False) -> Optional[str]:
        """
        Send a message to the chatbot and get a response.
        
        Args:
            message: User message
            stream: Whether to stream the response
            
        Returns:
            Bot response or None if error
        """
        if not self.model_name:
            console.print("[red]No model loaded. Please load a model first.[/red]")
            return None
        
        # Add user message to history
        self.conversation_history.append({"role": "user", "content": message})
        
        # Prepare request payload
        payload = {
            "model": self.model_name,
            "messages": self.conversation_history,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "stream": stream
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/v1/chat/completions",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            
            result = response.json()
            assistant_message = result['choices'][0]['message']['content']
            
            # Add assistant response to history
            self.conversation_history.append({"role": "assistant", "content": assistant_message})
            
            logger.info(f"Received response (length: {len(assistant_message)})")
            return assistant_message
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error during chat: {e}")
            console.print(f"[red]Error communicating with LM Studio: {e}[/red]")
            return None
    
    def clear_history(self):
        """Clear conversation history."""
        self.conversation_history = []
        logger.info("Conversation history cleared")
        console.print("[yellow]Conversation history cleared[/yellow]")
    
    def save_conversation(self, filepath: str):
        """
        Save conversation history to a file.
        
        Args:
            filepath: Path to save the conversation
        """
        try:
            with open(filepath, 'w') as f:
                json.dump(self.conversation_history, f, indent=2)
            logger.info(f"Conversation saved to {filepath}")
            console.print(f"[green]Conversation saved to {filepath}[/green]")
        except Exception as e:
            logger.error(f"Error saving conversation: {e}")
            console.print(f"[red]Error saving conversation: {e}[/red]")


def interactive_mode(chatbot: LMStudioChatbot):
    """
    Run the chatbot in interactive mode.
    
    Args:
        chatbot: LMStudioChatbot instance
    """
    console.print(Panel.fit(
        "[bold blue]LM Studio Local Chatbot[/bold blue]\n"
        "Commands:\n"
        "  /models - List available models\n"
        "  /load <model> - Load a specific model\n"
        "  /clear - Clear conversation history\n"
        "  /save <file> - Save conversation to file\n"
        "  /quit or /exit - Exit the chatbot\n"
        "Type your message to chat!",
        title="Welcome"
    ))
    
    while True:
        try:
            user_input = console.input("\n[bold cyan]You:[/bold cyan] ")
            
            if not user_input.strip():
                continue
            
            # Handle commands
            if user_input.startswith('/'):
                command = user_input.strip().lower()
                
                if command in ['/quit', '/exit']:
                    console.print("[yellow]Goodbye![/yellow]")
                    break
                
                elif command == '/models':
                    models = chatbot.list_models()
                    if models:
                        console.print("\n[bold]Available models:[/bold]")
                        for i, model in enumerate(models, 1):
                            console.print(f"  {i}. {model}")
                    else:
                        console.print("[yellow]No models found or unable to connect to LM Studio[/yellow]")
                
                elif command.startswith('/load '):
                    model_name = command.split(' ', 1)[1]
                    chatbot.load_model(model_name)
                
                elif command == '/clear':
                    chatbot.clear_history()
                
                elif command.startswith('/save '):
                    filepath = command.split(' ', 1)[1]
                    chatbot.save_conversation(filepath)
                
                else:
                    console.print("[red]Unknown command[/red]")
                
                continue
            
            # Send message to chatbot
            response = chatbot.chat(user_input)
            
            if response:
                console.print(f"\n[bold green]Assistant:[/bold green]")
                console.print(Markdown(response))
        
        except KeyboardInterrupt:
            console.print("\n[yellow]Interrupted. Type /quit to exit.[/yellow]")
            continue
        except EOFError:
            console.print("\n[yellow]Goodbye![/yellow]")
            break


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='LM Studio Local Chatbot')
    parser.add_argument('--config', type=str, help='Path to configuration file')
    parser.add_argument('--model', type=str, help='Model name to load')
    parser.add_argument('--list-models', action='store_true', help='List available models and exit')
    
    args = parser.parse_args()
    
    # Initialize chatbot
    chatbot = LMStudioChatbot(config_path=args.config)
    
    # List models if requested
    if args.list_models:
        models = chatbot.list_models()
        if models:
            console.print("\n[bold]Available models:[/bold]")
            for i, model in enumerate(models, 1):
                console.print(f"  {i}. {model}")
        return
    
    # Load model if specified
    if args.model:
        chatbot.load_model(args.model)
    
    # Start interactive mode
    interactive_mode(chatbot)


if __name__ == "__main__":
    main()
