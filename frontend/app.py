import streamlit as st
import requests

API_URL = "https://agenticdocragassistant-production.up.railway.app"  # Change for deployment

st.set_page_config(page_title="Agentic RAG", layout="wide")
st.title("📄 Agentic RAG Assistant")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "docs_uploaded" not in st.session_state:
    st.session_state.docs_uploaded = False

# Sidebar
with st.sidebar:
    st.header("📂 Upload Documents")
    
    uploaded_files = st.file_uploader(
        "Upload PDFs",
        type=["pdf"],
        accept_multiple_files=True
    )
    
    if st.button("Process Documents") and uploaded_files:
        with st.spinner("Uploading..."):
            try:
                files = [
                    ("files", (f.name, f.read(), "application/pdf"))
                    for f in uploaded_files
                ]
                
                response = requests.post(f"{API_URL}/upload", files=files)
                
                if response.status_code == 200:
                    st.success(f"✅ {response.json()['message']}")
                    st.session_state.docs_uploaded = True
                else:
                    st.error(f"Error: {response.text}")
                    
            except Exception as e:
                st.error(f"Connection error: {str(e)}")
    
    st.divider()
    
    if st.button("Clear Chat"):
        st.session_state.chat_history = []
        st.success("Cleared")

# Main chat
st.divider()

if not st.session_state.docs_uploaded:
    st.warning("📄 Upload documents first")
    st.stop()

# Display history
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# Input
if query := st.chat_input("Ask anything..."):
    st.session_state.chat_history.append({"role": "user", "content": query})
    
    with st.chat_message("user"):
        st.write(query)
    
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

                st.error(f"API error: {str(e)}")
