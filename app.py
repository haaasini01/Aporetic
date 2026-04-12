import streamlit as st
from AliceBobCindy import SocraticGPT
import time

# Page config
st.set_page_config(
    page_title="SocraticAI",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main {
        padding-top: 1rem;
    }
    .stChatMessage {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)

# Title
st.markdown("# 🧠 SocraticAI - Learn Through Questions")
st.markdown("*Your private tutor using the Socratic method*")

# Initialize session state
if 'socrates' not in st.session_state:
    st.session_state.socrates = SocraticGPT(role="Socrates", n_round=50)
    st.session_state.question = None

# Sidebar
with st.sidebar:
    st.markdown("### About SocraticAI")
    st.markdown("""
    SocraticAI uses the **Socratic method** to help you learn:
    - Ask your question
    - Receive guided hints instead of direct answers
    - Work through the problem step-by-step
    - Develop deeper understanding
    """)
    
    st.markdown("### Technology")
    st.markdown("""
    Built with:
    - **Streamlit** - Interactive UI
    - **LangChain** - LLM integration
    - **Google Gemini** - AI model
    - **WolframAlpha** - Fact checking
    """)

    st.markdown("---")
    # FIX: Moved Clear button to sidebar to prevent layout conflicts with st.chat_input
    if st.button("🗑️ Clear Conversation", use_container_width=True):
        st.session_state.socrates = SocraticGPT(role="Socrates", n_round=50)
        st.session_state.question = None
        st.rerun()

# Main chat interface
st.markdown("---")

# Display chat history
if len(st.session_state.socrates.history) > 0:
    with st.container():
        for msg in st.session_state.socrates.history:
            if hasattr(msg, 'content'):
                content = msg.content
                msg_type = msg.__class__.__name__
                
                if msg_type == 'HumanMessage':
                    with st.chat_message("user"):
                        st.write(content)
                elif msg_type == 'AIMessage':
                    with st.chat_message("assistant"):
                        st.write(content)
                # SystemMessages are intentionally hidden from the UI

# Chat input (must be at bottom level, not inside columns/containers)
user_input = st.chat_input("Type your question or reply here...")

# Process user input
if user_input:
    # First message — treat as the problem statement
    if st.session_state.question is None:
        st.session_state.question = user_input
        st.session_state.socrates.set_question(st.session_state.question)
        st.session_state.socrates.update_history(user_input)
    else:
        st.session_state.socrates.update_history(user_input)
    
    # Get response with spinner
    with st.spinner("Thinking..."):
        response = st.session_state.socrates.get_response()
    
    # Rerun to display updated chat
    st.rerun()