#!/usr/bin/env python3
"""
Gradio web interface for LM Studio Local Chatbot
"""

import gradio as gr
import os
from typing import List, Tuple
from lm_studio_client import create_client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class GradioChat:
    def __init__(self):
        self.client = create_client()
        self.conversation_history = []
    
    def check_connection(self) -> str:
        """Check LM Studio connection status"""
        if self.client.check_connection():
            return "✅ Connected to LM Studio"
        else:
            return "❌ Cannot connect to LM Studio. Please ensure it's running with a model loaded."
    
    def get_models(self) -> List[str]:
        """Get available models"""
        models = self.client.get_models()
        if models:
            return [model.get('id', 'Unknown') for model in models]
        return ["No models available"]
    
    def chat_response(self, message: str, history: List[Tuple[str, str]], model: str, temperature: float, max_tokens: int) -> Tuple[str, List[Tuple[str, str]]]:
        """Generate chat response"""
        if not message.strip():
            return "", history
        
        # Prepare conversation for API
        api_messages = []
        for user_msg, assistant_msg in history:
            api_messages.append({"role": "user", "content": user_msg})
            api_messages.append({"role": "assistant", "content": assistant_msg})
        api_messages.append({"role": "user", "content": message})
        
        try:
            # Get streaming response
            response_generator = self.client.chat_completion(
                messages=api_messages,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True
            )
            
            # Collect full response
            full_response = ""
            for chunk in response_generator:
                if isinstance(chunk, str):
                    full_response += chunk
            
            # Add to history
            history.append((message, full_response))
            
            return "", history
            
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            history.append((message, error_msg))
            return "", history
    
    def clear_chat(self) -> List[Tuple[str, str]]:
        """Clear chat history"""
        return []
    
    def create_interface(self):
        """Create and return the Gradio interface"""
        with gr.Blocks(title="LM Studio Local Chatbot", theme=gr.themes.Soft()) as interface:
            gr.Markdown("# 🤖 LM Studio Local Chatbot")
            
            with gr.Row():
                with gr.Column(scale=3):
                    # Chat interface
                    chatbot = gr.Chatbot(
                        label="Chat History",
                        height=500,
                        show_label=True
                    )
                    
                    with gr.Row():
                        message_input = gr.Textbox(
                            label="Your Message",
                            placeholder="Type your message here...",
                            scale=4,
                            lines=1
                        )
                        send_button = gr.Button("Send", variant="primary", scale=1)
                
                with gr.Column(scale=1):
                    # Status and controls
                    status_display = gr.Textbox(
                        label="Connection Status",
                        value=self.check_connection(),
                        interactive=False
                    )
                    
                    refresh_status = gr.Button("Refresh Status")
                    
                    # Model selection
                    model_dropdown = gr.Dropdown(
                        label="Select Model",
                        choices=self.get_models(),
                        value=self.get_models()[0] if self.get_models() else None,
                        interactive=True
                    )
                    
                    refresh_models = gr.Button("Refresh Models")
                    
                    # Parameters
                    temperature_slider = gr.Slider(
                        minimum=0.0,
                        maximum=2.0,
                        value=float(os.getenv('TEMPERATURE', 0.7)),
                        step=0.1,
                        label="Temperature",
                        info="Controls randomness (0 = deterministic, 2 = very random)"
                    )
                    
                    max_tokens_number = gr.Number(
                        label="Max Tokens",
                        value=int(os.getenv('MAX_TOKENS', 1000)),
                        minimum=1,
                        maximum=4000,
                        step=1,
                        info="Maximum length of response"
                    )
                    
                    clear_button = gr.Button("Clear Chat", variant="secondary")
            
            # Event handlers
            def send_message_handler(message, history, model, temperature, max_tokens):
                return self.chat_response(message, history, model, temperature, max_tokens)
            
            # Send message on button click or Enter press
            send_button.click(
                send_message_handler,
                inputs=[message_input, chatbot, model_dropdown, temperature_slider, max_tokens_number],
                outputs=[message_input, chatbot]
            )
            
            message_input.submit(
                send_message_handler,
                inputs=[message_input, chatbot, model_dropdown, temperature_slider, max_tokens_number],
                outputs=[message_input, chatbot]
            )
            
            # Clear chat
            clear_button.click(
                self.clear_chat,
                outputs=[chatbot]
            )
            
            # Refresh status
            refresh_status.click(
                self.check_connection,
                outputs=[status_display]
            )
            
            # Refresh models
            refresh_models.click(
                self.get_models,
                outputs=[model_dropdown]
            )
            
            # Footer
            gr.Markdown("---")
            gr.Markdown("Powered by LM Studio | Local AI at your fingertips")
        
        return interface

def main():
    """Main function to launch the Gradio interface"""
    chat_app = GradioChat()
    interface = chat_app.create_interface()
    
    # Launch the interface
    interface.launch(
        server_name="0.0.0.0",
        server_port=int(os.getenv('APP_PORT', 7860)),
        share=False,
        show_error=True
    )

if __name__ == "__main__":
    main()