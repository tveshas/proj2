"""Main FastAPI application for quiz solver endpoint."""
import json
import logging
from typing import Dict, Any
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ValidationError
import asyncio

from app.config import config
from app.quiz_solver import QuizSolver

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Quiz Solver API", version="1.0.0")

# Initialize quiz solver
quiz_solver = QuizSolver()


class QuizRequest(BaseModel):
    """Request model for quiz task."""
    email: str
    secret: str
    url: str
    # Allow additional fields
    class Config:
        extra = "allow"


@app.post("/quiz")
async def handle_quiz_task(request: Request):
    """
    Handle quiz task POST request.
    
    Returns:
        - 200: Secret valid, quiz processing started
        - 400: Invalid JSON payload
        - 403: Invalid secret
    """
    try:
        # Read and parse JSON body
        body = await request.body()
        
        # Check payload size
        if len(body) > config.MAX_PAYLOAD_SIZE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Payload too large"
            )
        
        try:
            payload = json.loads(body)
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid JSON: {str(e)}"
            )
        
        # Validate request model
        try:
            quiz_request = QuizRequest(**payload)
        except ValidationError as e:
            logger.error(f"Validation error: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid request format: {str(e)}"
            )
        
        # Verify secret
        if quiz_request.secret != config.SECRET:
            logger.warning(f"Invalid secret attempt for email: {quiz_request.email}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid secret"
            )
        
        # Verify email matches (optional but good practice)
        if quiz_request.email != config.EMAIL:
            logger.warning(f"Email mismatch: {quiz_request.email} vs {config.EMAIL}")
            # Still allow if secret is correct, but log it
        
        logger.info(f"Valid request received for URL: {quiz_request.url}")
        
        # Start quiz solving asynchronously (don't block the response)
        asyncio.create_task(quiz_solver.solve_quiz(quiz_request.url, quiz_request.email, quiz_request.secret))
        
        # Return immediate response
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "status": "accepted",
                "message": "Quiz task received and processing started"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Quiz Solver API",
        "version": "1.0.0",
        "endpoints": {
            "POST /quiz": "Submit a quiz task",
            "GET /health": "Health check"
        }
    }

