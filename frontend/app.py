import streamlit as st
import requests

API_URL = "https://agentic-doc-rag-assistant-1.onrender.com"

st.set_page_config(
    page_title="Multi-Tool AI Assistant v1.0",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Header
st.title("🤖 Multi-Tool AI Assistant")
st.caption("Version 1.0")
st.markdown("""
**Your intelligent assistant with multiple capabilities:**
- 🔍 **Web Search** via DuckDuckGo
- 📚 **Wikipedia** knowledge lookup
- 🧮 **Calculator** for mathematical operations
- 📄 **Document Q&A** - Upload PDFs and ask questions
""")

st.divider()

# Sidebar - Owner Details & Roadmap
with st.sidebar:
    st.header("👤 About")
    st.markdown("""
    **Owner:** Moin
    
    **Version:** 1.0
    
    **Status:** ✅ Active
    """)
    
    st.divider()
    
    st.header("🚀 Roadmap - Version 2.0")
    st.markdown("""
    **Coming Soon:**
    
    1. 📥 **Export Chat History**
       - Download conversations as PDF/TXT
       - Share insights easily
    
    2. 📊 **Evaluation Metrics**
       - Response quality tracking
       - Performance analytics
       - User satisfaction scores
    
    3. ⚡ **Streaming Response**
       - Real-time answer generation
       - Faster perceived response time
       - Better user experience
    
    4. 📑 **Source Citations**
       - Page number references
       - Document preview snippets
       - Transparent sourcing
    """)
    
    st.divider()
    
    st.markdown("""
    <div style='text-align: center; color: gray; font-size: 0.85em;'>
        <p>💬 Feedback? Let me know!</p>
    </div>
    """, unsafe_allow_html=True)

# Initialize session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Document Upload Section (Main Area)
st.header("📂 Document Upload (Optional)")
st.markdown("*Upload PDF documents to enable document-based Q&A. You can also chat without uploading anything!*")

uploaded_files = st.file_uploader(
    "Upload PDF files (optional)",
    type=["pdf"],
    accept_multiple_files=True,
    help="Upload PDFs to ask questions about their content"
)

# Auto-process on upload
if uploaded_files:
    if "last_uploaded_files" not in st.session_state:
        st.session_state.last_uploaded_files = []
    
    # Check if files changed
    current_files = [f.name for f in uploaded_files]
    if current_files != st.session_state.last_uploaded_files:
        with st.spinner("Processing documents..."):
            try:
                files = [
                    ("files", (f.name, f.read(), "application/pdf"))
                    for f in uploaded_files
                ]
                
                response = requests.post(f"{API_URL}/upload", files=files)
                
                if response.status_code == 200:
                    st.success(f"✅ {len(uploaded_files)} document(s) processed successfully!")
                    st.session_state.last_uploaded_files = current_files
                else:
                    st.error(f"Error processing documents: {response.text}")
                    
            except Exception as e:
                st.error(f"Connection error: {str(e)}")

col1, col2 = st.columns([6, 1])
with col2:
    if st.button("🗑️ Clear Chat"):
        st.session_state.chat_history = []
        st.rerun()

st.divider()

# Chat Interface
st.header("💬 Chat")

# Display chat history
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# Chat input
if query := st.chat_input("Ask me anything... (search web, calculate, lookup Wikipedia, or ask about uploaded documents)"):
    # Add user message
    st.session_state.chat_history.append({"role": "user", "content": query})
    
    with st.chat_message("user"):
        st.write(query)
    
    # Get assistant response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = requests.post(
                    f"{API_URL}/query",
                    json={"question": query}
                )
                
                if response.status_code == 200:
                    answer = response.json()["answer"]
                    st.write(answer)
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": answer
                    })
                else:
                    st.error(f"Error: {response.text}")
                    
            except Exception as e:
                st.error(f"Connection error: {str(e)}")
                st.info("Make sure the backend server is running at " + API_URL)

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: gray; font-size: 0.9em;'>
    <p>💡 <b>Tips:</b> Try asking "What's 25 * 47?", "Search for latest AI news", "What is quantum computing?" or upload a PDF and ask questions about it!</p>
    <p style='font-size: 0.8em; margin-top: 10px;'>Multi-Tool AI Assistant v1.0 | Created by Moin</p>
</div>
""", unsafe_allow_html=True)
