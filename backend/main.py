from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import tempfile
import os
from doc_rag import build_agent
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Agentic RAG API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global agent
agent_instance = None

class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    answer: str
    success: bool

@app.get("/")
def root():
    return {"status": "Agentic RAG API Running", "version": "1.0"}

@app.post("/upload")
async def upload_documents(files: List[UploadFile] = File(...)):
    global agent_instance
    
    try:
        all_paths = []
        
        for file in files:
            if not file.filename.endswith('.pdf'):
                raise HTTPException(400, "Only PDF files allowed")
            
            # Save temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                content = await file.read()
                tmp.write(content)
                all_paths.append(tmp.name)
        
        # Build agent
        agent_instance = build_agent(all_paths)
        
        return {
            "success": True,
            "message": f"Processed {len(files)} documents",
            "file_count": len(files)
        }
        
    except Exception as e:
        raise HTTPException(500, str(e))

@app.post("/query", response_model=QueryResponse)
def query_agent(request: QueryRequest):
    global agent_instance
    
    if agent_instance is None:
        raise HTTPException(400, "No documents uploaded. Upload first.")
    
    try:
        response = agent_instance.invoke({"input": request.question})
        answer = response.get("output", "No response generated")
        
        return QueryResponse(answer=answer, success=True)
        
    except Exception as e:
        raise HTTPException(500, str(e))

@app.delete("/clear")
def clear_agent():
    global agent_instance
    agent_instance = None
    return {"success": True, "message": "Agent cleared"}

if __name__ == "__main__":
    import uvicorn
    import os
    # Railway PORT variable provide karta hai, agar na mile toh default 8000
    port = int(os.environ.get("PORT", 8000)) 
    uvicorn.run(app, host="0.0.0.0", port=port)