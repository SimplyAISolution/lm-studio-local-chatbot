import streamlit as st
import os
from typing import List, Dict
from lm_studio_client import create_client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title=os.getenv('APP_TITLE', 'LM Studio Local Chatbot'),
    page_icon="🤖",
    layout="centered"
)

@st.cache_resource
def get_lm_studio_client():
    """Get cached LM Studio client"""
    return create_client()

def check_connection():
    """Check LM Studio connection with caching"""
    client = get_lm_studio_client()
    return client.check_connection()

def get_available_models():
    """Get available models from LM Studio"""
    client = get_lm_studio_client()
    return client.get_models()

def main():
    st.title("🤖 LM Studio Local Chatbot")
    
    # Initialize session state
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "client" not in st.session_state:
        st.session_state.client = get_lm_studio_client()
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Connection status
        connection_status = check_connection()
        if connection_status:
            st.success("✅ Connected to LM Studio")
        else:
            st.error("❌ Cannot connect to LM Studio")
            st.info("""
            Please make sure:
            1. LM Studio is running
            2. A model is loaded
            3. Local server is started
            """)
        
        # Model selection
        if connection_status:
            models = get_available_models()
            if models:
                model_options = [model.get('id', 'Unknown') for model in models]
                selected_model = st.selectbox(
                    "Select Model:",
                    options=model_options,
                    index=0 if model_options else None
                )
            else:
                st.warning("No models available")
                selected_model = None
        else:
            selected_model = None
        
        # Chat parameters
        st.subheader("Chat Parameters")
        temperature = st.slider(
            "Temperature:",
            min_value=0.0,
            max_value=2.0,
            value=float(os.getenv('TEMPERATURE', 0.7)),
            step=0.1,
            help="Controls randomness in responses"
        )
        
        max_tokens = st.number_input(
            "Max Tokens:",
            min_value=1,
            max_value=4000,
            value=int(os.getenv('MAX_TOKENS', 1000)),
            help="Maximum length of the response"
        )
        
        # Clear conversation
        if st.button("🧹 Clear Conversation"):
            st.session_state.messages = []
            st.rerun()
    
    # Main chat interface
    if not connection_status:
        st.error("Please connect to LM Studio to start chatting.")
        return
    
    if not selected_model:
        st.warning("Please select a model to start chatting.")
        return
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("What would you like to know?"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate assistant response
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            
            try:
                # Prepare messages for API
                api_messages = [
                    {"role": msg["role"], "content": msg["content"]} 
                    for msg in st.session_state.messages
                ]
                
                # Get streaming response
                response_generator = st.session_state.client.chat_completion(
                    messages=api_messages,
                    model=selected_model,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    stream=True
                )
                
                # Stream the response
                full_response = ""
                for chunk in response_generator:
                    if isinstance(chunk, str):
                        full_response += chunk
                        message_placeholder.markdown(full_response + "▌")
                
                # Finalize the response
                message_placeholder.markdown(full_response)
                
                # Add assistant response to chat history
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": full_response
                })
                
            except Exception as e:
                error_message = f"Error: {str(e)}"
                message_placeholder.error(error_message)
                
                # Add error to chat history
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": error_message
                })

    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #666;'>
            Powered by LM Studio | Local AI at your fingertips
        </div>
        """, 
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()