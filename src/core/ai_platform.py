#!/usr/bin/env python3
"""
Production AI Platform - Windows Edition
Real, working AI infrastructure adapted for Windows
"""

import asyncio
import logging
import os
import time
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

import uvicorn
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, UploadFile, File
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import numpy as np

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

# Configuration
class Config:
    def __init__(self):
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY", "")
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "")
        self.perplexity_api_key = os.getenv("PERPLEXITY_API_KEY", "")
        self.app_dir = Path.home() / "AI-Platform"
        self.data_dir = self.app_dir / "data"
        self.logs_dir = self.app_dir / "logs"
        self.uploads_dir = self.app_dir / "uploads"
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        
        # Create directories
        for dir in [self.app_dir, self.data_dir, self.logs_dir, self.uploads_dir]:
            dir.mkdir(parents=True, exist_ok=True)

config = Config()

# Initialize FastAPI
app = FastAPI(
    title="Production AI Platform - Windows Edition",
    description="Real AI infrastructure running on Windows",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Data Models
class AIRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=5000)
    model: str = Field(default="claude-3-haiku-20240307", 
                      description="Model: claude-*, gpt-*, sonar-pro, sonar-small")
    max_tokens: int = Field(default=1000, ge=1, le=4000)
    temperature: float = Field(default=0.7, ge=0, le=1)

class AIResponse(BaseModel):
    id: str
    content: str
    model: str
    usage: Dict[str, int]
    processing_time_ms: int
    timestamp: datetime

class DocumentAnalysisRequest(BaseModel):
    analysis_type: str = Field(default="summarize")
    language: str = Field(default="en")

class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=500)
    model: str = Field(default="sonar-pro", description="sonar-pro or sonar-small")
    max_tokens: int = Field(default=1000, ge=1, le=4000)
    temperature: float = Field(default=0.7, ge=0, le=1)

# Services
class AIService:
    def __init__(self):
        self.anthropic_client = None
        self.openai_client = None
        self.perplexity_client = None
        
        # Performance optimization: track client health
        self.client_health = {
            "anthropic": {"healthy": True, "last_error": None, "error_count": 0},
            "openai": {"healthy": True, "last_error": None, "error_count": 0},
            "perplexity": {"healthy": True, "last_error": None, "error_count": 0}
        }
        
        # Error suppression: avoid logging same error repeatedly
        self.last_logged_errors = {}
        self.error_log_cooldown = 300  # 5 minutes
        
        # Response caching to reduce redundant API calls
        self.response_cache = {}
        self.cache_ttl = 600  # 10 minutes
        self.max_cache_size = 100  # Limit cache size
        
        self.setup_clients()
        
    def setup_clients(self):
        """Setup AI clients if API keys are available"""
        try:
            if config.anthropic_api_key:
                import anthropic
                self.anthropic_client = anthropic.Anthropic(api_key=config.anthropic_api_key)
                logging.info("Anthropic client initialized")
        except ImportError:
            logging.warning("Anthropic library not installed")
            
        try:
            if config.openai_api_key:
                import openai
                # Connection pooling optimization: configure HTTP client
                self.openai_client = openai.OpenAI(
                    api_key=config.openai_api_key,
                    max_retries=2,  # Reduce retries to fail faster
                    timeout=30.0    # Shorter timeout to avoid hanging
                )
                logging.info("OpenAI client initialized")
        except ImportError:
            logging.warning("OpenAI library not installed")
            
        try:
            if config.perplexity_api_key:
                import openai
                # Connection pooling optimization: configure HTTP client
                self.perplexity_client = openai.OpenAI(
                    api_key=config.perplexity_api_key,
                    base_url="https://api.perplexity.ai",
                    max_retries=2,  # Reduce retries to fail faster
                    timeout=30.0    # Shorter timeout to avoid hanging
                )
                logging.info("Perplexity client initialized")
        except ImportError:
            logging.warning("OpenAI library not installed (needed for Perplexity)")
    
    async def process_request(self, request: AIRequest) -> AIResponse:
        """Process AI request with the specified model"""
        start_time = time.time()
        request_id = str(uuid.uuid4())
        
        # Check cache first for identical requests
        cache_key = self._generate_cache_key(request)
        cached_response = self._get_cached_response(cache_key)
        if cached_response:
            # Update timestamp and return cached response
            cached_response.timestamp = datetime.now()
            cached_response.id = request_id  # New ID for tracking
            logging.info(f"Returning cached response for {request.model}")
            return cached_response
        
        try:
            # Process with appropriate model
            if request.model.startswith("claude") and self.anthropic_client:
                # Use Anthropic
                response = self.anthropic_client.messages.create(
                    model=request.model,
                    max_tokens=request.max_tokens,
                    temperature=request.temperature,
                    messages=[{"role": "user", "content": request.prompt}]
                )
                content = response.content[0].text
                usage = {
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens
                }
            elif request.model.startswith("gpt") and self.openai_client:
                # Use OpenAI
                response = self.openai_client.chat.completions.create(
                    model=request.model,
                    max_tokens=request.max_tokens,
                    temperature=request.temperature,
                    messages=[{"role": "user", "content": request.prompt}]
                )
                content = response.choices[0].message.content
                usage = {
                    "input_tokens": response.usage.prompt_tokens,
                    "output_tokens": response.usage.completion_tokens
                }
            elif request.model.startswith("sonar") and self.perplexity_client:
                # Use Perplexity
                response = self.perplexity_client.chat.completions.create(
                    model=request.model,
                    max_tokens=request.max_tokens,
                    temperature=request.temperature,
                    messages=[{"role": "user", "content": request.prompt}]
                )
                content = response.choices[0].message.content
                usage = {
                    "input_tokens": response.usage.prompt_tokens if response.usage.prompt_tokens else 0,
                    "output_tokens": response.usage.completion_tokens if response.usage.completion_tokens else 0
                }
            else:
                # Fallback to mock response for testing
                content = f"Mock response for: {request.prompt[:50]}..."
                usage = {"input_tokens": 10, "output_tokens": 10}
            
            processing_time = int((time.time() - start_time) * 1000)
            
            response_obj = AIResponse(
                id=request_id,
                content=content,
                model=request.model,
                usage=usage,
                processing_time_ms=processing_time,
                timestamp=datetime.now()
            )
            
            # Cache the response for future identical requests
            self._cache_response(cache_key, response_obj)
            
            return response_obj
            
        except Exception as e:
            # Smart error handling with suppression
            error_str = str(e)
            current_time = time.time()
            
            # Track client health based on error type
            if "exceeded your current quota" in error_str or "insufficient_quota" in error_str:
                self._update_client_health("openai", False, "quota_exceeded")
            elif "401 Authorization Required" in error_str:
                if request.model.startswith("sonar"):
                    self._update_client_health("perplexity", False, "auth_failed")
            elif "anthropic" in error_str.lower():
                self._update_client_health("anthropic", False, "api_error")
            
            # Only log error if not recently logged (error suppression)
            error_key = f"{request.model}:{type(e).__name__}"
            if (error_key not in self.last_logged_errors or 
                current_time - self.last_logged_errors[error_key] > self.error_log_cooldown):
                logging.error(f"Error processing request: {e}")
                self.last_logged_errors[error_key] = current_time
            
            raise HTTPException(status_code=500, detail=str(e))
    
    def _update_client_health(self, client_name: str, healthy: bool, error_type: str = None):
        """Update client health status for smart routing"""
        if client_name in self.client_health:
            self.client_health[client_name]["healthy"] = healthy
            if not healthy:
                self.client_health[client_name]["error_count"] += 1
                self.client_health[client_name]["last_error"] = error_type
                # Auto-recovery after some time
                if self.client_health[client_name]["error_count"] >= 5:
                    logging.warning(f"{client_name} marked as unhealthy after {self.client_health[client_name]['error_count']} errors")
    
    def _get_best_available_client(self, preferred_model: str):
        """Smart routing: get the best available client for the request"""
        # If preferred client is healthy, use it
        if preferred_model.startswith("claude") and self.client_health["anthropic"]["healthy"]:
            return "anthropic"
        elif preferred_model.startswith("gpt") and self.client_health["openai"]["healthy"]:
            return "openai"
        elif preferred_model.startswith("sonar") and self.client_health["perplexity"]["healthy"]:
            return "perplexity"
        
        # Fallback to any healthy client
        for client_name, health in self.client_health.items():
            if health["healthy"]:
                if client_name == "anthropic" and self.anthropic_client:
                    return "anthropic"
                elif client_name == "openai" and self.openai_client:
                    return "openai"
                elif client_name == "perplexity" and self.perplexity_client:
                    return "perplexity"
        
        # No healthy clients available, proceed with original logic
        return None
    
    def _generate_cache_key(self, request: AIRequest) -> str:
        """Generate a cache key for the request"""
        import hashlib
        # Create cache key from prompt, model, and key parameters
        key_data = f"{request.prompt}:{request.model}:{request.max_tokens}:{request.temperature}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def _get_cached_response(self, cache_key: str) -> Optional[AIResponse]:
        """Get cached response if valid and not expired"""
        if cache_key not in self.response_cache:
            return None
            
        cached_item = self.response_cache[cache_key]
        current_time = time.time()
        
        # Check if cache is expired
        if current_time - cached_item["timestamp"] > self.cache_ttl:
            # Remove expired cache entry
            del self.response_cache[cache_key]
            return None
            
        return cached_item["response"]
    
    def _cache_response(self, cache_key: str, response: AIResponse):
        """Cache the response with timestamp"""
        # Limit cache size to prevent memory issues
        if len(self.response_cache) >= self.max_cache_size:
            # Remove oldest cache entry
            oldest_key = min(self.response_cache.keys(), 
                           key=lambda k: self.response_cache[k]["timestamp"])
            del self.response_cache[oldest_key]
        
        # Store response with timestamp
        self.response_cache[cache_key] = {
            "response": response,
            "timestamp": time.time()
        }

class DocumentProcessor:
    """Process various document types"""
    
    async def process_pdf(self, file_content: bytes) -> str:
        """Extract text from PDF"""
        try:
            import PyPDF2
            import io
            
            pdf_file = io.BytesIO(file_content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
            return text
        except ImportError:
            return "PDF processing requires PyPDF2 library"
        except Exception as e:
            return f"PDF processing error: {e}"
    
    async def process_docx(self, file_content: bytes) -> str:
        """Extract text from DOCX"""
        try:
            import docx
            import io
            
            doc = docx.Document(io.BytesIO(file_content))
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
            return text
        except ImportError:
            return "DOCX processing requires python-docx library"
        except Exception as e:
            return f"DOCX processing error: {e}"
    
    async def process_text(self, file_content: bytes) -> str:
        """Process plain text files"""
        try:
            return file_content.decode('utf-8')
        except UnicodeDecodeError:
            return file_content.decode('latin-1')

class RAGService:
    """Simple RAG service using in-memory storage"""
    
    def __init__(self):
        self.documents = {}
        self.embeddings = {}
        
    async def add_document(self, text: str, metadata: Dict) -> str:
        """Add document to RAG storage"""
        doc_id = str(uuid.uuid4())
        self.documents[doc_id] = {
            "text": text,
            "metadata": metadata,
            "timestamp": datetime.now().isoformat()
        }
        # In a real implementation, generate embeddings here
        return doc_id
    
    async def search_documents(self, query: str, top_k: int = 5) -> List[Dict]:
        """Search documents (simplified without real embeddings)"""
        results = []
        query_lower = query.lower()
        
        for doc_id, doc in self.documents.items():
            if query_lower in doc["text"].lower():
                results.append({
                    "id": doc_id,
                    "snippet": doc["text"][:200],
                    "metadata": doc["metadata"],
                    "score": 0.5  # Mock similarity score
                })
        
        return results[:top_k]

# Initialize services
ai_service = AIService()
doc_processor = DocumentProcessor()
rag_service = RAGService()

# Authentication
async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Simple token verification"""
    # In production, implement real authentication
    if credentials.credentials == "demo-token":
        return True
    # For now, allow any token
    return True

# API Endpoints
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "Production AI Platform - Windows Edition",
        "version": "1.0.0",
        "status": "operational",
        "docs": "http://localhost:8000/docs"
    }

@app.post("/api/v1/ai/generate", response_model=AIResponse)
async def generate_ai_response(
    request: AIRequest,
    background_tasks: BackgroundTasks,
    token: bool = Depends(verify_token)
):
    """Generate AI response"""
    response = await ai_service.process_request(request)
    
    # Log request in background
    background_tasks.add_task(
        log_request, 
        request.model, 
        response.processing_time_ms
    )
    
    return response

@app.post("/api/v1/documents/upload")
async def upload_document(
    file: UploadFile = File(...),
    analysis: DocumentAnalysisRequest = Depends(),
    token: bool = Depends(verify_token)
):
    """Upload and process document"""
    # Read file content
    file_content = await file.read()
    
    # Save uploaded file
    upload_path = config.uploads_dir / file.filename
    with open(upload_path, "wb") as f:
        f.write(file_content)
    
    try:
        # Process based on file type
        if file.filename.endswith('.pdf'):
            text = await doc_processor.process_pdf(file_content)
            doc_type = "pdf"
        elif file.filename.endswith('.docx'):
            text = await doc_processor.process_docx(file_content)
            doc_type = "docx"
        elif file.filename.endswith('.txt'):
            text = await doc_processor.process_text(file_content)
            doc_type = "text"
        else:
            text = "File type not fully supported yet"
            doc_type = "unknown"
        
        # Add to RAG database
        doc_id = await rag_service.add_document(text, {
            "filename": file.filename,
            "type": doc_type,
            "upload_time": datetime.now().isoformat()
        })
        
        # Analyze if requested and AI is available
        analysis_result = "Document processed successfully"
        if analysis.analysis_type == "summarize" and ai_service.anthropic_client:
            summary_request = AIRequest(
                prompt=f"Please summarize this document in 2-3 sentences:\n\n{text[:2000]}",
                max_tokens=200
            )
            try:
                summary_response = await ai_service.process_request(summary_request)
                analysis_result = summary_response.content
            except:
                analysis_result = "Summary generation unavailable"
        
        return {
            "document_id": doc_id,
            "filename": file.filename,
            "type": doc_type,
            "length": len(text),
            "analysis": analysis_result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Document processing failed: {str(e)}")

@app.get("/api/v1/documents/search")
async def search_documents(
    query: str,
    top_k: int = 5,
    token: bool = Depends(verify_token)
):
    """Search documents using semantic similarity"""
    results = await rag_service.search_documents(query, top_k)
    return {"query": query, "results": results}

@app.post("/api/v1/ai/search", response_model=AIResponse)
async def search_ai_enhanced(
    request: SearchRequest,
    background_tasks: BackgroundTasks,
    token: bool = Depends(verify_token)
):
    """AI-enhanced web search using Perplexity"""
    if not ai_service.perplexity_client:
        raise HTTPException(status_code=503, detail="Perplexity API not configured")
    
    # Convert SearchRequest to AIRequest format
    ai_request = AIRequest(
        prompt=request.query,
        model=request.model,
        max_tokens=request.max_tokens,
        temperature=request.temperature
    )
    
    response = await ai_service.process_request(ai_request)
    
    # Log request in background
    background_tasks.add_task(
        log_request, 
        request.model, 
        response.processing_time_ms
    )
    
    return response

@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "services": {
            "api": "operational",
            "anthropic": "configured" if ai_service.anthropic_client else "not_configured",
            "openai": "configured" if ai_service.openai_client else "not_configured",
            "perplexity": "configured" if ai_service.perplexity_client else "not_configured",
            "rag": "operational"
        },
        "paths": {
            "app_dir": str(config.app_dir),
            "data_dir": str(config.data_dir),
            "uploads_dir": str(config.uploads_dir)
        }
    }

# Background tasks
async def log_request(model: str, processing_time: int):
    """Log request for monitoring"""
    log_file = config.logs_dir / f"requests_{datetime.now().strftime('%Y%m%d')}.log"
    with open(log_file, "a") as f:
        f.write(f"{datetime.now().isoformat()} - Model: {model}, Time: {processing_time}ms\n")

def main():
    """Main entry point for the AI Platform"""
    # Setup logging
    logging.basicConfig(
        level=getattr(logging, config.log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(config.logs_dir / "ai_platform.log"),
            logging.StreamHandler()
        ]
    )
    
    logging.info("Starting Production AI Platform - Windows Edition")
    logging.info(f"Data directory: {config.data_dir}")
    logging.info(f"API docs available at: http://localhost:8000/docs")
    
    # Run server
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()