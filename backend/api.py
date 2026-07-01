from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Annotated

from agents.agent3 import get_verdict

import traceback

app = FastAPI(
    title="Misinformation Detection API",
    description="API for fact-checking claims using a multi-agent RAG system",
    version="1.0.0"
    )

#for writing the claim and sending it 
class ClaimRequest(BaseModel):
    claim : Annotated[str, Field(description="Enter the claim you want to ask", examples=["Cracking your knuckles causes arthritis"])]

#for getting the response in right way
class ClaimResponse(BaseModel):
    verdict: str
    confidence: float
    explanation: str
    sources: list[str]
    

@app.post('/predict', response_model=ClaimResponse) 
def predict(request : ClaimRequest):
    
    try :
        verdict, context = get_verdict(request.claim)
        
        lines = verdict.strip().split("\n")

        verdict_text = ""
        confidence = 0.0
        explanation = ""
        sources = []
        
        reading_sources = False
        reading_explanation = False

        for line in lines:
            if line.startswith("VERDICT:"):
                reading_explanation = False
                verdict_text = line.replace("VERDICT:", "").strip()

            elif line.startswith("CONFIDENCE:"):
                reading_explanation = False
                confidence = float(line.replace("CONFIDENCE:", "").strip())

            elif line.startswith("EXPLANATION:"):
                reading_explanation = True
                reading_sources = False
                explanation = line.replace("EXPLANATION:", "").strip()

            elif line.startswith("SOURCES:"):
                reading_explanation = False
                reading_sources = True

                first_source = line.replace("SOURCES:", "").strip()
                if first_source:
                    sources.extend([s.strip() for s in first_source.split(",") if s.strip()])
            
            elif reading_explanation:
                explanation += line.strip() + " "    
            elif reading_sources and line.strip():
                sources.append(line.strip())
        
        
        return ClaimResponse(
            verdict=verdict_text,
            confidence=confidence,
            explanation=explanation,
            sources=sources
        )

    except Exception as e:
        traceback.print_exc()  
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )