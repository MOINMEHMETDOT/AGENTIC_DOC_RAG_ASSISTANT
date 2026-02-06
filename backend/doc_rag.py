from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import PGVector
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings # Added Embeddings
from langchain_community.tools import WikipediaQueryRun, DuckDuckGoSearchRun
from langchain_community.utilities import WikipediaAPIWrapper
from langchain_classic.agents import AgentExecutor, create_react_agent
from langchain_classic.chains import LLMMathChain
from langchain_core.tools import Tool, tool
from langchain_classic import hub
from langchain_classic.memory import ConversationBufferMemory
import os
import uuid
load_dotenv()
CONNECTION_STRING = os.getenv("DATABASE_URL")
# Secure way to set API Key
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

def build_agent(pdf_paths: list):
    retriever = None

    # Document pipeline
    if pdf_paths:
        all_chunks = []
        for pdf_path in pdf_paths:
            loader = PyPDFLoader(pdf_path)
            docs = loader.load()
            if not docs:
                continue

            splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
            chunks = splitter.split_documents(docs)
            all_chunks.extend(chunks)

        if all_chunks:
            # ✅ CHANGED: Using Google Gemini Embeddings instead of HuggingFace
            embeddings = GoogleGenerativeAIEmbeddings(
                model="gemini-embedding-001", # Latest and fastest model
                google_api_key=GOOGLE_API_KEY
            )
            collection_name = f"rag_docs_{uuid.uuid4().hex[:8]}"  # Unique collection name to avoid conflicts
            vectorstore = PGVector.from_documents(
                documents=all_chunks,
                embedding=embeddings,
                collection_name=collection_name,  
                connection_string=CONNECTION_STRING, # Parameter name might vary based on version
                use_jsonb=True
            )

            retriever = vectorstore.as_retriever(search_kwargs={"k": 4})
            print(f"✅ Processed {len(pdf_paths)} PDFs with Gemini Embeddings")

    # LLM Setup - Updated to stable 1.5-flash
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.7)
    
    @tool
    def document_search(query: str) -> str:
        """Search uploaded document for relevant information."""
        if retriever is None:
            return "No document uploaded yet."
        docs = retriever.invoke(query)
        return "\n\n".join([doc.page_content for doc in docs]) if docs else "No relevant information found."

    math_chain = LLMMathChain.from_llm(llm=llm)
    calculator = Tool(name="Calculator", func=math_chain.run, description="Useful for math calculations")
    search = DuckDuckGoSearchRun()
    wiki = WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper())
    
    tools = [calculator, search, document_search, wiki]

    prompt = hub.pull("hwchase17/react")
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

    agent = create_react_agent(llm=llm, tools=tools, prompt=prompt)

    return AgentExecutor(
        agent=agent,
        tools=tools,
        memory=memory,
        verbose=True,
        max_iterations=3,
        handle_parsing_errors=True

    )


