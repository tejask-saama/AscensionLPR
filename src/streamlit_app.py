
import streamlit as st
import streamlit.components.v1 as components
import requests
from typing import Dict, Any, List
import json
import pandas as pd
import uuid
import time
from datetime import datetime
import pytz

# Configure the page
st.set_page_config(
    page_title="Patient Portal",
    page_icon="🏥",
    layout="wide"
)

# --- Custom CSS for the Fixed Top Navigation Bar, Smart Assistant Panel, and General Styling ---
st.markdown("""
    <style>
    /* Global styles for the body and main content area */
    body {
        font-family: 'Inter', sans-serif; /* Using Inter font as recommended */
        margin: 0;
        padding: 0;
    }

    .stApp{
        background-color: #F5F8FF; /* Very light blue background */
    }

    /* Vertical divider styling */
    .vertical-divider {
        position: fixed;
        top: 0;
        height: 100vh;
        width: 0.1px;
        background-color: rgba(0, 0, 0, 0.2);
        box-shadow: 0 0 8px rgba(0, 0, 0, 0.3);
        margin: 0 auto;
    }

    /* Custom button styling */
    .stButton button {
        background-color: #FFFFFF;
        color: #2D3748;
        border: 1px solid #E2E8F0;
        transition: all 0.2s ease;
    }

    .stButton button:hover {
        background-color: #E2E8F0;
        border-color: #CBD5E0;
    }

    /* Style for selected patient button */
    .stButton button[kind="primary"] {
        background-color: #0D4B77;
        color: white;
        border: 1px solid #0D4B77;
    }

    /* Smart Assistant Panel Styling */
    div[data-testid="column"]:nth-child(4) {
        background: transparent !important;
    }

    /* Chat input container styles */
    .chat-input-container {
        background: transparent !important;
        padding: 0;
        margin: 0;
        display: flex;
        align-items: center;
    }

    /* Loading indicator styles */
    .typing-indicator {
        display: flex;
        align-items: center;
        column-gap: 6px;
        padding: 10px;
    }

    .typing-indicator::after {
        content: '...';
        animation: typing 1.5s steps(3, start) infinite;
        font-size: 20px;
        line-height: 0;
        margin-top: -10px;
    }

    @keyframes typing {
        0% { content: '.'; }
        33% { content: '..'; }
        66% { content: '...'; }
        100% { content: '.'; }
    }

    /* Remove default streamlit container padding */
    .element-container, .stTextInput > div {
        padding: 0 !important;
        margin: 0 !important;
        border-radius: 30px;
    }

    /* Chat input styling */
    .stTextInput input {
        background-color: white;
        border: 1px solid #0d4b77;
        border-radius: 20px;
        padding: 12px 20px;
        font-size: 14px;
        transition: all 0.2s ease;
        color: #2D3748;
        margin: 0;
    }

    .stTextInput input:focus {
        border-color: #0d4b77 !important;
        box-shadow: 0 0 0 1px #0d4b77 !important;
    }

    .stTextInput input::placeholder {
        color: #718096;
        font-style: italic;
    }

    /* Send button container */
    div[data-testid="column"]:has(.send-button) {
        padding: 0 !important;
        background: transparent !important;
        border-radius: 30px;
    }

    .stButton button[kind="primary"]:hover {
        background-color: #0d4b77 !important;
        border-color: #0d4b77 !important;
        color: white;
    }

    .main .block-container {
        padding-top: 0;
        padding-bottom: 0;
        max-width: 100%;
    }

    /* Fixed top navigation bar styling */
    .fixed-top-navbar {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        width: 100%;
        background-color: white;
        padding: 10px 20px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        z-index: 1000;
    }

    /* Add padding to main content to account for fixed navbar */
    .main-content {
        padding-top: 4rem;
    }
    .navbar-left, .navbar-right {
        display: flex;
        align-items: center;
    }

    .navbar-title {
        font-size: 1.2rem;
        font-weight: bold;
        color: #0d4b77;
        margin-right: 20px;
    }

    .navbar-subtitle {
        font-size: 0.9rem;
        color: #666;
    }

    .user-info {
        display: flex;
        align-items: center;
        font-size: 0.9rem;
        color: #333;
    }
    .user-info span {
        margin-right: 8px; /* Spacing for the dropdown arrow */
    }

    /* General Streamlit app adjustments */
    .stMainBlockContainer {
        padding: 0rem 0rem; /* Remove default top padding */
    }
    header[data-testid="stHeader"] {
        display: none; /* Hide Streamlit's default header */
    }


    /* Custom tab styling */
    .stTabs [data-baseweb="tab-list"] {
        display: flex;
        justify-content: space-between;
        background-color: #f8fafc;
        padding: 10px;
        border-radius: 10px;
    }

    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre;
        font-size: 1.5rem;
        flex: 1;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: all 0.2s ease;
    }

    .stTabs [aria-selected="true"] {
        background-color: #1f77b4 !important;
        color: white !important;
        border-color: #1f77b4 !important;
    }

    .stTabs [data-baseweb="tab"]:hover {
        background-color: #edf2f7;
        border-color: #cbd5e0;
    }


    /* Patient Card Styling (for all info cards) */
    .patient-card {
        background-color: #F8FAFC;
        padding: 1.5rem;
        border-radius: 10px;
        border: 1px solid #E2E8F0;
        margin-bottom: 1rem;
        transition: all 0.2s ease;
    }

    .patient-card:hover {
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        transform: translateY(-2px);
    }
    .card-title {
        color: #2D3748;
        font-size: 1.2rem;
        font-weight: 600;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #E2E8F0;
    }

    /* Patient selection buttons */
    .main-content div[data-testid="stHorizontalBlock"] > div > div {
        padding: 0 0.5rem;
    }
    .main-content div[data-testid="stHorizontalBlock"] button[kind="secondary"] {
        width: 100% !important;
        height: 100% !important;
        min-height: 50px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        text-align: center;
        background-color: white;
        border: 1px solid #ddd;
        border-radius: 20px;
        margin: 0 5px;
        font-size: 0.9rem;
        font-weight: normal;
        color: #333;
        transition: all 0.3s ease;
    }
    .main-content div[data-testid="stHorizontalBlock"] button[kind="secondary"]:hover {
        border-color: #1a73e8;
        color: #1a73e8;
        background-color: #f8f9fa;
    }

    /* Patient Information Banner (Blue header for selected patient details) */
    .patient-info-banner {
        background-color: #1f77b4; /* Dark blue background */
        color: white;
        padding: 10px 20px 15px 20px;
        border-radius: 8px;
        margin-top: 20px;
        margin-bottom: 20px;
        text-align: center;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    .patient-info-banner h2 {
        color: white;
        margin-top: 0;
    }
    .patient-info-banner p {
        margin: 5px 0;
        font-size: 1.1rem;
    }
    .info-tag {
        background-color: rgba(255,255,255,0.2); /* Semi-transparent white tag */
        color: white;
        padding: 5px 10px;
        border-radius: 15px; /* Pill shape */
        font-size: 0.8rem;
        margin-right: 10px;
        display: inline-block;
    }

    .chat-messages-display {
        flex-grow: 1; /* Allows message area to take available space */
        padding: 15px 20px;
        overflow-y: auto; /* Enable scrolling for messages */
        display: flex;
        flex-direction: column; /* Stack messages vertically */
    }

    .message-bubble.assistant {
        background-color: #e6e6e6; /* Light grey for incoming message bubble */
        border-radius: 15px 15px 15px 0; /* Rounded corners, flat on bottom-left for sender */
        padding: 10px 15px;
        margin-bottom: 10px;
        max-width: calc(100% - 80px); /* Limit bubble width accounting for avatar */
        word-wrap: break-word;
        align-self: flex-start; /* Align to left for incoming */
        font-size: 0.9rem;
    }
    .message-bubble.user {
        background-color: #d8eaff; /* Light blue for outgoing message bubble */
        border-radius: 15px 15px 0 15px; /* Rounded corners, flat on bottom-right for sender */
        padding: 10px 15px;
        margin-bottom: 10px;
        max-width: calc(100% - 80px); /* Limit bubble width accounting for avatar */
        word-wrap: break-word;
        align-self: flex-end; /* Align to right for outgoing */
        font-size: 0.9rem;
    }

    .message-time {
        font-size: 0.75rem;
        color: #777;
    }
    .message-bubble.assistant .message-time {
        text-align: right;
    }
    .message-bubble.user .message-time {
        text-align: right; /* Adjust time alignment for user messages if needed */
    }

    .chat-input-container {
        padding: 10px 20px;
        border-top: 1px solid #eee;
        display: flex;
        align-items: center;
        background-color: white; /* Ensure background is white */
        border-radius: 20px; /* Rounded bottom corners */
    }

    /* Style for Streamlit's text_input within the custom container */
    .chat-input-container div[data-testid="stTextInput"] {
        flex-grow: 1;
        margin-right: 10px;
    }
    
    .chat-input-container div[data-testid="stTextInput"] div[data-baseweb="input"] {
        border-radius: 20px; /* Pill shape for input */
        border: 1px solid #ccc;
        padding: 5px 15px; /* Adjust padding inside input */
    }
    .chat-input-container div[data-testid="stTextInput"] input {
        font-size: 0.9rem;
        outline: none;
    }

    .chat-input-container .send-button {
        background: none;
        border: none;
        cursor: pointer;
        font-size: 1.4rem;
        color: #0D4B77;
        padding: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        line-height: 1;
        margin-left: -8px;
        transition: all 0.2s ease;
    }
    .chat-input-container .send-button:hover {
        color: #0A3B5C;
        transform: scale(1.1);
    }

    /* Suggested questions section */
    .element-container:has(.suggested-questions-header) ~ div button[kind="secondary"] {
        color: #333 !important;
        border: 1px solid #e0e0e0 !important;
        border-radius: 20px !important;
        width: 70% !important;
        padding: 5px 10px !important;
        background-color: #f0f2f6 !important;
        transition: all 0.3s ease !important;
    }

    div[data-testid="stVerticalBlock"] button[kind="secondary"]:hover {
        background-color: #e6e6e6 !important;
        border-color: #1a73e8 !important;
        color: #1a73e8 !important;
    }

    .suggested-questions-header {
        display: flex;
        align-items: center;
        margin-bottom: 10px;
        color: #718096;
        font-size: 0.9rem;
    }

    .suggested-questions-header i {
        color: #ecc94b;
        margin-right: 8px;
    }

    /* Targeting Streamlit's inner block containers within the smart assistant column */
    /* This aims to remove default padding that Streamlit adds inside its columns */
    .st-emotion-cache-zt5ig8 { /* Default Streamlit inner block container class (may vary) */
        padding: 0px !important; /* Aggressively remove padding */
    }
    .st-emotion-cache-1kyxreqy { /* Another common inner div (may vary) */
         padding: 0px !important;
    }

    .chat-message-row { /* NEW: Flex container for avatar and bubble */
        display: flex;
        align-items: flex-start; /* Align avatar and message bubble to the top */
        margin-bottom: 10px;
    }
    .chat-message-row.user-message { /* NEW: For user messages, reverse direction and align right */
        justify-content: flex-end; /* Push user messages to the right */
    }


    </style>

    <!-- Font Awesome for icons -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css">
""", unsafe_allow_html=True)

st.markdown('<div class="main-content">', unsafe_allow_html=True)

# --- Fixed Top Navigation Bar HTML ---
st.markdown(
    """
    <div class="fixed-top-navbar">
        <div class="navbar-left">
            <span class="navbar-title">Ascension</span>
            <span class="navbar-subtitle">Longitudinal Patient Record</span>
        </div>
        <div class="navbar-right">
            <span class="user-info"><span class="user-icon">👨‍⚕️</span>Dr. Smith</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)


# Constants
SUGGESTED_QUESTIONS = [
    "What are the patient's current medications?",
    "Summarize recent vital signs",
    "List the patient's allergies"
]

# Initialize session state
if 'selected_patient' not in st.session_state:
    st.session_state.selected_patient = None
if 'lpr_data' not in st.session_state:
    st.session_state.lpr_data = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'conversation_id' not in st.session_state:
    st.session_state.conversation_id = None
if 'is_first_message' not in st.session_state:
    st.session_state.is_first_message = True
if 'custom_query' not in st.session_state:
    st.session_state.custom_query = ''
if 'user_timezone_offset' not in st.session_state:
    st.session_state.user_timezone_offset = None


def format_timestamp(timestamp):
    """Convert Unix timestamp to local time string"""
    dt = datetime.fromtimestamp(timestamp)
    return dt.strftime("%I:%M %p")  # Format as "HH:MM AM/PM"

def render_smart_assistant_panel():
    
    # Header for Smart Assistant
    st.markdown("<h2 style='color: #0d4b77; padding: 0rem; font-size: 1.5rem;'>Smart Assistant</h2>", unsafe_allow_html=True)

    # Chat messages display area
    st.markdown("<div class='chat-messages-display' style='flex-grow: 1; padding: 15px 20px; overflow-y: auto;'>", unsafe_allow_html=True)
    
    # Suggested questions section
    st.markdown(
        """
        <style>
        #suggested-questions-container button[kind="secondary"] {
            font-size: 0.75rem !important;
        }
        </style>
        <div id='suggested-questions-container'>
            <div class='suggested-questions-header'>
                <i class='fas fa-lightbulb'></i>
                <span>Suggested Questions</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    # Create a container for suggested questions
    suggested_container = st.container()
    with suggested_container:
        st.markdown(
            '''
            <style>
                [data-testid="stButton"]:has(button[key*="column_suggest_"]) button {
                    font-size: 0.75rem !important;
                }
            </style>
            ''',
            unsafe_allow_html=True
        )
        for question in SUGGESTED_QUESTIONS:
            st.button(
                question,
                key=f"column_suggest_{question}",
                on_click=process_query,
                args=(question,),
                use_container_width=True
            )
    st.markdown("</div>", unsafe_allow_html=True)
    # Updated chat message rendering loop to include avatars and action buttons (Key Visual Change)
    if st.session_state.is_first_message and st.session_state.selected_patient is None:
        st.markdown(
            f"""
            <div class="chat-message-row assistant-message">
                <div class="message-bubble assistant">
                    Hello! I'm your Smart Assistant. How can I help you today?
                </div>
            </div>
            <script>scrollToLatestMessage();</script>
            """, unsafe_allow_html=True
        )
    elif st.session_state.is_first_message and st.session_state.selected_patient:
        st.markdown(
            f"""
            <div class="chat-message-row assistant-message" id="message-0">
                <div class="message-bubble assistant">
                    Hello! I'm your Smart Assistant. How can I help you with {st.session_state.selected_patient['name']} today?
                    <div class="message-time">{format_timestamp(time.time())}</div>
                </div>
            </div>
            <script>scrollToLatestMessage();</script>
            """, unsafe_allow_html=True
        )

    for i, chat in enumerate(st.session_state.chat_history):
        message_id = f"message-{i*2}"
        # User message with avatar
        timestamp = format_timestamp(chat['timestamp'])
        st.markdown(f"""
        <div class="chat-message-row user-message" id="{message_id}">
            <div class="message-bubble user">
                {chat['question']}
                <div class="message-time">{timestamp}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Assistant response with avatar and action buttons (NEW)
        timestamp = format_timestamp(chat['timestamp'])
        st.markdown(f"""
        <div class="chat-message-row assistant-message" id="{message_id}-response">
            <div class="message-bubble assistant">
                {chat['response']}
                <div class="message-time">{timestamp}</div>
            </div>
        </div>
        <script>scrollToLatestMessage();</script>
        """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True) # Close chat-messages-display div

    

    # Chat input area (now directly in column)
    st.markdown("<div class='chat-input-container'>", unsafe_allow_html=True)
    col_input, col_send = st.columns([0.85, 0.15])
    with col_input:
        st.text_input(
            "Type your question here...",
            value=st.session_state.get('custom_query', ''),
            key=f"custom_query_input_column",
            on_change=process_query,
            disabled=not st.session_state.selected_patient,
            label_visibility="collapsed",
            placeholder="Ask me anything about the patient..."
        )
    with col_send:
        st.markdown(
            f"""
            <button class="send-button" onclick="
                var inputElement = document.getElementById('text-input-custom_query_input_column');
                if (inputElement) {{
                    inputElement.dispatchEvent(new Event('change'));
                }}
            " {"disabled" if not st.session_state.selected_patient else ""}>
                <i class="fas fa-paper-plane"></i>
            </button>
            """,
            unsafe_allow_html=True
        )
    st.markdown("</div>", unsafe_allow_html=True)

def format_chat_response(text):
    """Format the response for chat display with proper styling"""
    if not text:
        return ""

    # Split into sections based on double newlines
    sections = text.split('\n\n')
    formatted_sections = []

    for section in sections:
        lines = section.split('\n')
        formatted_lines = []
        is_list = False

        # Check if this section is a header (e.g., "LAB RESULTS:")
        if len(lines) > 0 and lines[0].strip().endswith(':'):
            formatted_lines.append(f"<div style='color: #1f77b4; font-size: 1.0em; font-weight: bold; margin: 0.8em 0 0.4em 0;'>{lines[0].strip()}</div>")
            lines = lines[1:]

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Check for numbered items or bullet points
            if line.strip().startswith(('•', '-', '*')) or (line.strip()[:2].replace('.', '').isdigit()):
                is_list = True
                line_content = line.strip().lstrip('•-* 0123456789.')
                
                # Handle different types of data
                if "Visit Date:" in line:
                    # Format visit date entries
                    date_parts = line_content.split('•')
                    formatted_date = f"<strong style='color: #2c5282;'>{date_parts[0].strip()}</strong>"
                    if len(date_parts) > 1:
                        formatted_date += f"<span style='color: #4a5568;'> • {date_parts[1].strip()}</span>"
                    formatted_lines.append(f"<li style='margin-bottom: 0.8em;'>{formatted_date}</li>")
                elif any(key in line for key in ['Weight:', 'Creatinine:', 'BNP:', 'FEV1:', 'EF:']):
                    # Format lab values
                    label, value = line_content.split(':', 1)
                    formatted_lines.append(f"<li style='margin: 0.4em 0;'><span style='color: #4a5568;'>{label.strip()}:</span> <strong>{value.strip()}</strong></li>")
                else:
                    # Default list item formatting
                    formatted_lines.append(f"<li style='margin: 0.4em 0;'>{line_content}</li>")
            else:
                if "NOTE:" in line:
                    formatted_lines.append(f"<div style='margin: 0.8em 0; font-style: italic; color: #718096; font-size: 0.9em; background-color: #f7fafc; padding: 0.6em; border-radius: 4px;'>{line}</div>")
                else:
                    formatted_lines.append(f"<div style='margin: 0.4em 0;'>{line}</div>")

        if is_list:
            formatted_sections.append(f"<ul style='list-style-type: none; margin: 0; padding: 0;'>\n{''.join(formatted_lines)}\n</ul>")
        else:
            formatted_sections.append(''.join(formatted_lines))

    return '\n'.join(formatted_sections)

def get_display_value(data_dict, key):
    value = data_dict.get(key)
    if value is None or (isinstance(value, str) and value.strip() == ''):
        return 'N/A'
    return value
        
def process_query(question_text: str = None):
    """Function to handle query submission"""
    # Initialize query_text before the processing check
    query_text = question_text if question_text else st.session_state.get('custom_query_input_column', '').strip()
    
    if not st.session_state.get('query_processing', False):
        st.session_state.query_processing = True

    if query_text and st.session_state.selected_patient:
        # Add the user message immediately to show it's processing
        message_id = str(uuid.uuid4())
        st.session_state.chat_history.append({
            'question': query_text,
            'messageId': message_id,
            'timestamp': time.time(),
            'sender': 'user',
            'processing': True  # Flag to show it's processing
        })

        try:
            conversation_history_for_api = []
            for chat in st.session_state.chat_history:
                conversation_history_for_api.append({
                    'content': chat['question'],
                    'sender': 'user',
                    'messageId': chat['messageId'],
                    'timestamp': chat['timestamp']
                })
                if chat.get('raw_response'):
                    conversation_history_for_api.append({
                        'content': chat['raw_response'],
                        'sender': 'assistant',
                        'messageId': chat['responseMessageId'],
                        'timestamp': chat['timestamp']
                    })

            custom_response = requests.post(
                "http://127.0.0.1:8000/api/patient/query",
                json={
                    "query": query_text,
                    "patientId": st.session_state.selected_patient['id'],
                    "messageId": message_id,
                    "conversationHistory": conversation_history_for_api
                }
            )
            
            if custom_response.status_code == 200:
                custom_data = custom_response.json()
                response_text = custom_data.get('response', 'No response available')                 
                formatted_response = format_chat_response(response_text)
                
                # Update the last message with response and remove processing flag
                for chat in st.session_state.chat_history:
                    if chat['messageId'] == message_id:
                        chat.update({
                            'response': formatted_response,
                            'raw_response': response_text,
                            'responseMessageId': custom_data.get('message_id', str(uuid.uuid4())),
                            'processing': False
                        })
                        break
                
                st.session_state.is_first_message = False
                st.session_state.custom_query = '' # Clear the input
            else:
                st.error(f"Error: {custom_response.status_code} - {custom_response.text}")
                # Remove the processing message on error
                st.session_state.chat_history = [chat for chat in st.session_state.chat_history if chat['messageId'] != message_id]
        except requests.exceptions.ConnectionError:
            st.error("Could not connect to the backend API. Please ensure your backend is running at http://127.0.0.1:8000.")
            # Remove the processing message on error
            st.session_state.chat_history = [chat for chat in st.session_state.chat_history if chat['messageId'] != message_id]
        except Exception as e:
            st.error(f"Error processing query: {str(e)}")
            # Remove the processing message on error
            st.session_state.chat_history = [chat for chat in st.session_state.chat_history if chat['messageId'] != message_id]
        finally:
            st.session_state.query_processing = False
        
        # Reset processing flag
        st.session_state.query_processing = False

# --- Main Content Area (Layout with 2 columns: Main Details, Smart Assistant) ---
col1, col_patient_details_content, col2, col_smart_assistant, col3 = st.columns([0.025, 0.7, 0.025, 0.3, 0.025])

# Add vertical divider in col2
with col2:
    st.markdown('<div class="vertical-divider"></div>', unsafe_allow_html=True)

with col_patient_details_content:
    # st.markdown("### Select a patient:")
    st.markdown('<h3 style="color: #0d4b77;">Select a patient</h3>', unsafe_allow_html=True)

    # Patient selection buttons (horizontal layout)
    patients = [
        {"id": "b452d3ec-ce76-424d-87cb-7849422dbf92", "name": "James Robertson"},
        {"id": "29378b30-61c1-4e91-a731-443cabd4ae48", "name": "Linda Chen"},
        {"id": "992dbaa2-966e-426b-b78a-803828931d21", "name": "Robert Anderson"},
        {"id": "a4a2eaf4-3e41-471c-aea5-89497add41d9", "name": "John Doe"},
        {"id": "patient-1015", "name": "Ian Russell"}
    ]
    
    cols_buttons = st.columns(len(patients))
    for idx, patient in enumerate(patients):
        with cols_buttons[idx]:
            button_type = "primary" if st.session_state.selected_patient and st.session_state.selected_patient['id'] == patient['id'] else "secondary"
            if st.button(
                patient['name'],
                key=patient['id'],
                use_container_width=True,
                type=button_type  # Dynamically set button type
            ):
                # Only update state if a new patient is selected, or if the same patient is re-clicked (to re-fetch data/reset chat)
                if st.session_state.selected_patient and st.session_state.selected_patient['id'] == patient['id']:
                    # If the same patient is clicked, consider it a refresh or explicit re-selection
                    # Re-trigger data load and chat reset
                    st.session_state.selected_patient = patient
                    st.session_state.lpr_data = None
                    st.session_state.chat_history = []
                    st.session_state.conversation_id = None
                    st.session_state.is_first_message = True
                    st.session_state.custom_query = ''
                    st.rerun()
                elif not st.session_state.selected_patient or st.session_state.selected_patient['id'] != patient['id']:
                    st.session_state.selected_patient = patient
                    st.session_state.lpr_data = None
                    st.session_state.chat_history = []
                    st.session_state.conversation_id = None
                    st.session_state.is_first_message = True
                    st.session_state.custom_query = ''
                    st.rerun()

    if st.session_state.selected_patient is None:
        st.info("👆 Please select a patient to begin")


    if st.session_state.selected_patient:
        if st.session_state.lpr_data is None:
            with st.spinner(f"Loading data for {st.session_state.selected_patient['name']}..."):
                try:
                    lpr_response = requests.post(
                        "http://127.0.0.1:8000/api/patient/lpr",
                        json={
                            "query": "LPR",
                            "patient_id": st.session_state.selected_patient['id']
                        }
                    )
                    
                    if lpr_response.status_code != 200:
                        st.error(f"An error occurred while fetching patient data: {lpr_response.status_code} - {lpr_response.text}. Please ensure your backend is running.")
                    else:
                        st.session_state.lpr_data = lpr_response.json()
                except requests.exceptions.ConnectionError:
                    st.error("Could not connect to the backend API. Please ensure your backend is running at http://127.00.1:8000.")
                except Exception as e:
                    st.error(f"Error loading patient data")
                    print(f"Error: {str(e)}")
        
        if st.session_state.lpr_data:
            response_data = st.session_state.lpr_data.get('response', {})
            if not isinstance(response_data, dict):
                st.error("Invalid response format from LPR API. Please ensure your backend is running.")
            else:
                patient_info = response_data.get('patientInformation', {})
                st.markdown(f"""
                        <div class="patient-info-banner">
                            <h2>{st.session_state.selected_patient['name']}</h2>
                            <p>MRN: {get_display_value(patient_info, 'mrnId')}</p>
                            <p>
                                <span class="info-tag">DOB: {get_display_value(patient_info, 'dob')}</span>
                                <span class="info-tag">Age: {get_display_value(patient_info, 'age')} years</span>
                                <span class="info-tag">Sex: {get_display_value(patient_info, 'sex').capitalize()}</span>
                            </p>
                        </div>
                        """, unsafe_allow_html=True
                    )

                # Create tabs for different sections
                tab_labels = ["📋 Overview", "📅 Medical Timeline", "💊 Current Care", "⚠️ Risk Assessment", "📝 Recommendations"]
                overview_tab, timeline_tab, care_tab, risk_tab, recommendation_tab = st.tabs(tab_labels)
                
                
                with overview_tab:
                    background = response_data.get('background', {})
                    if not background:
                        st.write("No background data available.")
                    
                    col1_bg, col2_bg = st.columns(2)
                    
                    with col1_bg:
                        st.markdown(f"""<div class='patient-card'>
                            <div class='card-title'>Past Medical History</div>
                            {''.join([f"<p>{condition.get('condition', 'Unknown')} <br><small style='color: #666;'>Diagnosed: {condition.get('diagnosedDate', 'N/A')[:10] if condition.get('diagnosedDate') else 'N/A'}</small></p>" for condition in background.get('pastMedicalHistory', [])]) if background.get('pastMedicalHistory') else '<p>No data available</p>'}
                        </div>""", unsafe_allow_html=True)

                        st.markdown(f"""<div class='patient-card'>
                            <div class='card-title'>Immunizations</div>
                            {''.join([f"<p>{immunization.get('vaccine', 'Unknown')} <br><small style='color: #666;'>Date: {immunization.get('administeredDate', 'N/A')[:10] if immunization.get('administeredDate') else 'N/A'}</small></p>" for immunization in background.get('immunizations', [])]) if background.get('immunizations') else '<p>No data available</p>'}
                        </div>""", unsafe_allow_html=True)

                    with col2_bg:
                        allergies = background.get('allergies', [])
                        allergy_content = ''.join([f"<p> {allergy.get('allergen', 'Unknown')}</p>" for allergy in allergies]) if allergies else '<p>No data available</p>'
                        st.markdown(f"""
                            <div class='patient-card'>
                                <div class='card-title'>Allergies</div>
                                {allergy_content}
                            </div>
                        """, unsafe_allow_html=True)

                        # Get medication history
                        med_history = background.get('medicationHistory', [])
                        
                        st.markdown(f"""<div class='patient-card'>
                            <div class='card-title'>Past Medications</div>
                            {''.join([f"<p>💊 {med.get('medication', 'Unknown')}<br><small style='color: #666;'>Reason: {med.get('reasonForUse', 'N/A')}</small></p>" for med in med_history]) if med_history else '<p>No past medication data available</p>'}
                        </div>""", unsafe_allow_html=True)
                        

                with timeline_tab:
                    timeline = response_data.get('chronologicalMedicalTimeline', [])
                    if not timeline:
                        st.write("No medical timeline data available.")
                    for visit in timeline:
                        def clean_text(text):
                            if not isinstance(text, str):
                                if isinstance(text, dict):
                                    cleaned = ', '.join(f"{k}: {v}" for k, v in text.items() if v)
                                    return cleaned if cleaned else 'N/A'
                                return 'N/A'
                            text = text.replace('<p>', '').replace('</p>', '').replace('<strong>', '').replace('</strong>', '')
                            text = text.replace('</div>', '').replace('<div>', '')
                            text = ' '.join(text.split())
                            if text.startswith('Assessment:') or text.startswith('Plan:') or text.startswith('Diagnosis:') or text.startswith('Symptoms:'):
                                text = text.split(':', 1)[1].strip()
                            return text.strip() or 'N/A'
                        
                        # Function to get field value and clean it
                        def get_field(visit_data, field_name):
                            value = clean_text(visit_data.get(field_name, 'N/A'))
                            return (value, value != 'N/A' and value.strip() != '')
                        
                        # Get all fields with their values and presence flags
                        visit_date = visit.get('visitDate', 'N/A')[:10] if visit.get('visitDate') else 'N/A'
                        visit_type = visit.get('visitType', 'N/A')
                        
                        fields = [
                            ('Vital Signs', *get_field(visit, 'vitalSigns')),
                            ('Physical Exam', *get_field(visit, 'physicalExam')),
                            ('Symptoms', *get_field(visit, 'symptoms')),
                            ('Diagnosis', *get_field(visit, 'diagnosis')),
                            ('Hospital Course', *get_field(visit, 'hospitalCourse')),
                            ('Labs', *get_field(visit, 'labs')),
                            ('Imaging', *get_field(visit, 'imaging')),
                            ('Procedures', *get_field(visit, 'procedures')),
                            ('Assessment', *get_field(visit, 'assessment')),
                            ('Plan', *get_field(visit, 'plan'))
                        ]
                        
                        # Start card with title
                        card_content = f"""<div class='patient-card'>
                            <div class='card-title'>{visit_date} - {visit_type}</div>"""
                        
                        # Add fields that have data
                        has_data = False
                        for field_name, value, has_value in fields:
                            if has_value:
                                has_data = True
                                card_content += f"<p style='margin-bottom: 0.5rem;'><strong>{field_name}:</strong> {value}</p>"
                        
                        # If no data fields are present, show a message
                        if not has_data:
                            card_content += "<p>No additional details available for this visit</p>"
                        
                        card_content += "</div>"
                        st.markdown(card_content, unsafe_allow_html=True)

                with care_tab:
                    care_plan = response_data.get('currentCarePlan', {})
                    if not care_plan:
                        st.write("No current care plan data available.")
                    
                    col1_cp, col2_cp = st.columns(2)
                    
                    with col1_cp:
                        if care_plan.get('activeCarePlan'):
                            active_plan = care_plan['activeCarePlan']
                            st.markdown(f"""<div class='patient-card'>
                                <div class='card-title'>Active Care Plan</div>
                                <p><strong>{active_plan.get('title', 'N/A')}</strong></p>
                                <p style='color: #666;'>{active_plan.get('description', 'N/A')}</p>
                            </div>""", unsafe_allow_html=True)
                        else:
                            st.markdown(f"""<div class='patient-card'><div class='card-title'>Active Care Plan</div><p>No data available</p></div>""", unsafe_allow_html=True)

                        if care_plan.get('currentGoals'):
                            st.markdown(f"""<div class='patient-card'>
                                <div class='card-title'>Current Goals</div>
                                {''.join([f"<p>🎯 {goal.get('goal', 'N/A')}</p>" for goal in care_plan.get('currentGoals', [])])}
                            </div>""", unsafe_allow_html=True)
                        else:
                            st.markdown(f"""<div class='patient-card'><div class='card-title'>Current Goals</div><p>No data available</p></div>""", unsafe_allow_html=True)

                    with col2_cp:
                        if care_plan.get('recentVitalSigns'):
                            vitals = care_plan['recentVitalSigns']
                            def clean_vital_sign(text):
                                if not isinstance(text, str): return 'N/A'
                                text = text.replace('<div>', '').replace('</div>', '').replace('<p>', '').replace('</p>', '').replace('<strong>', '').replace('</strong>', '')
                                return ' '.join(text.split())
                            
                            bp = clean_vital_sign(vitals.get('bp', 'N/A'))
                            temp = clean_vital_sign(vitals.get('temperature', 'N/A'))
                            resp_rate = clean_vital_sign(vitals.get('respiratoryRate', 'N/A'))
                            
                            card_content = f"""<div class='patient-card'>
                                <div class='card-title'>Recent Vital Signs</div>"""
                            
                            if bp != 'N/A': card_content += f"<p style='margin-bottom: 0.5rem;'><strong>Blood Pressure:</strong> {bp}</p>"
                            if temp != 'N/A': card_content += f"<p style='margin-bottom: 0.5rem;'><strong>Temperature:</strong> {temp}</p>"
                            if resp_rate != 'N/A': card_content += f"<p style='margin-bottom: 0.5rem;'><strong>Respiratory Rate:</strong> {resp_rate}</p>"
                            
                            card_content += "</div>"
                            st.markdown(card_content, unsafe_allow_html=True)
                        else:
                            st.markdown(f"""<div class='patient-card'><div class='card-title'>Recent Vital Signs</div><p>No data available</p></div>""", unsafe_allow_html=True)

                        if care_plan.get('currentMedications'):
                            st.markdown(f"""<div class='patient-card'>
                                <div class='card-title'>Current Medications</div>
                                {''.join([f"<p>💊 {med.get('medication', 'Unknown')} <br><small style='color: #666;'>{med.get('purpose', 'N/A')}</small></p>" for med in care_plan.get('currentMedications', [])])}
                            </div>""", unsafe_allow_html=True)
                        else:
                            st.markdown(f"""<div class='patient-card'><div class='card-title'>Current Medications</div><p>No data available</p></div>""", unsafe_allow_html=True)

                with risk_tab:
                    risk = response_data.get('riskAssessment', {})
                    if not risk:
                        st.write("No risk assessment data available.")

                    else:
                        st.markdown("""
                            <style>
                            .risk-card {
                                background-color: white;
                                padding: 15px 20px 10px 20px;
                                border-radius: 10px;
                                margin-bottom: 10px;
                                border: 1px solid #e1e4e8;
                            }
                            .risk-high {
                                border-left: 4px solid #dc3545;
                            }
                            .risk-medium {
                                border-left: 4px solid #ffc107;
                            }
                            .risk-low {
                                border-left: 4px solid #28a745;
                            }
                            </style>
                        """, unsafe_allow_html=True)
                    
                    if risk.get('cardiovascularRisk'):
                        st.markdown(f"""<div class='risk-card risk-high'>
                            <h6>Cardiovascular Risk Factors</h6>
                            {''.join([f"<p>❗ {factor.get('riskFactor', 'Unknown Risk')}</p>" for factor in risk.get('cardiovascularRisk', [])])}
                        </div>""", unsafe_allow_html=True)
                    else:
                        st.markdown(f"""<div class='patient-card'><div class='card-title'>Cardiovascular Risk Factors</div><p>No data available</p></div>""", unsafe_allow_html=True)
                    
                    if risk.get('conditionSpecificComplications'):
                        st.markdown(f"""<div class='risk-card risk-medium'>
                            <h6>Condition Specific Complications</h6>
                            {''.join([f"<p>⚠️ {complication.get('complication', 'Unknown Complication')}</p>" for complication in risk.get('conditionSpecificComplications', [])])}
                        </div>""", unsafe_allow_html=True)
                    else:
                        st.markdown(f"""<div class='patient-card'><div class='card-title'>Condition Specific Complications</div><p>No data available</p></div>""", unsafe_allow_html=True)
                    
                    if risk.get('fallRisk'):
                        st.markdown(f"""<div class='risk-card risk-medium'>
                            <h6>Fall Risk</h6>
                            <p><strong>🚨 Risk Factors:</strong> {risk['fallRisk'].get('riskFactors', 'N/A')}</p>
                            <p><strong>💡 Recommendations:</strong> {risk['fallRisk'].get('recommendations', 'N/A')}</p>
                        </div>""", unsafe_allow_html=True)
                    else:
                        st.markdown(f"""<div class='patient-card'><div class='card-title'>Fall Risk</div><p>No data available</p></div>""", unsafe_allow_html=True)

                with recommendation_tab:
                    recommendations = response_data.get('recommendations', {})
                    if not recommendations:
                        st.write("No recommendations data available.")
                    
                    if recommendations.get('followUpSchedule'):
                        schedule = recommendations['followUpSchedule']
                        specialist_names = {
                            'specialist1': 'Cardiology',
                            'specialist2': 'Nephrology',
                            'specialist3': 'Psychiatry'
                        }
                        formatted_schedule = []
                        for key, value in schedule.items():
                            display_name = specialist_names.get(key, key.replace('_', ' ').title())
                            formatted_schedule.append(f"<p>📅 <strong>{display_name}:</strong> {value if value else 'N/A'}</p>")
                        
                        st.markdown(f"""<div class='patient-card'>
                            <div class='card-title'>Follow-up Schedule</div>
                            {''.join(formatted_schedule)}
                        </div>""", unsafe_allow_html=True)
                    else:
                        st.markdown(f"""<div class='patient-card'><div class='card-title'>Follow-up Schedule</div><p>No data available</p></div>""", unsafe_allow_html=True)
                    
                    if recommendations.get('preventiveCare'):
                        st.markdown(f"""<div class='patient-card'>
                            <div class='card-title'>Preventive Care</div>
                            {''.join([f"<p>✅ {list(care.values())[0] if care and care.values() else 'N/A'}</p>" for care in recommendations.get('preventiveCare', [])])}
                        </div>""", unsafe_allow_html=True)
                    else:
                        st.markdown(f"""<div class='patient-card'><div class='card-title'>Preventive Care</div><p>No data available</p></div>""", unsafe_allow_html=True)
                    
                    if recommendations.get('lifestyleRecommendations'):
                        st.markdown(f"""<div class='patient-card'>
                            <div class='card-title'>Lifestyle Recommendations</div>
                            {''.join([f"<p>💡 {rec if rec else 'N/A'}</p>" for rec in recommendations.get('lifestyleRecommendations', [])])}
                        </div>""", unsafe_allow_html=True)
                    else:
                        st.markdown(f"""<div class='patient-card'><div class='card-title'>Lifestyle Recommendations</div><p>No data available</p></div>""", unsafe_allow_html=True)
        else:
            st.info("No detailed patient data available. Please select a patient.")
            
# Render Smart Assistant Panel
with col_smart_assistant:
    render_smart_assistant_panel()

# Handle the timezone offset from JavaScript
if st.session_state.user_timezone_offset is None:
    components.html("""
    <script>
        // Send timezone offset to Python
        const offset = new Date().getTimezoneOffset();
        const offsetHours = -offset/60;
        window.parent.postMessage({
            type: "streamlit:setComponentValue",
            value: offsetHours
        }, "*");
    </script>
    """, height=0)
