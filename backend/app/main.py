import os
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from app.schemas import DocumentAnalysisResult
from app.modules.parser import DocumentParser
from app.workflow import build_workflow

# Load environment variables
load_dotenv()

app = FastAPI(
    title="RFP / SOW Intelligence Portal API",
    description="ML Backend API for Document Analysis",
    version="1.0.0"
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Workflow
workflow_app = build_workflow()

@app.get("/")
def read_root():
    return {"message": "Welcome to the RFP/SOW Intelligence Portal API"}

@app.post("/api/v1/analyze", response_model=DocumentAnalysisResult)
async def analyze_document(file: UploadFile = File(...)):
    try:
        # 1. Read file bytes
        file_bytes = await file.read()
        
        # 2. Parse text
        text = DocumentParser.parse_document(file_bytes, file.filename)
        if "Error parsing" in text:
            raise HTTPException(status_code=400, detail=text)
            
        if not text.strip():
            raise HTTPException(status_code=400, detail="Document contains no text.")

        # 3. Initialize State
        initial_state = {
            "file_name": file.filename,
            "text": text,
            "classification": None,
            "extracted": None,
            "risks": None,
            "summary": None,
            "similar_projects": [],
            "final_result": None
        }

        # 4. Run Workflow
        # ainvoke runs the workflow asynchronously
        result_state = await workflow_app.ainvoke(initial_state)
        
        return result_state["final_result"]

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
