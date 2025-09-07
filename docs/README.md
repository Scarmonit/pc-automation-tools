# AI Platform - Windows Edition

Real AI infrastructure adapted for Windows, providing Claude and OpenAI API integration with document processing capabilities.

## Quick Start

1. **Double-click** `start-ai-platform.bat` to run
2. Open http://localhost:8000/docs for the API interface
3. Configure your API keys in `.env` file

## Features

- **AI Chat**: Claude and OpenAI integration
- **Document Processing**: PDF, DOCX, and text file analysis
- **RAG System**: Upload and search documents
- **REST API**: Full FastAPI interface
- **Windows Optimized**: Native Windows paths and compatibility

## API Endpoints

- `GET /` - Platform status
- `POST /api/v1/ai/generate` - AI text generation
- `POST /api/v1/documents/upload` - Upload and analyze documents
- `GET /api/v1/documents/search` - Search uploaded documents
- `GET /api/v1/health` - Health check

## Configuration

Edit `.env` file with your API keys:
```
ANTHROPIC_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here
LOG_LEVEL=INFO
```

## Requirements

- Python 3.8+
- Windows 10/11
- API keys (Anthropic/OpenAI)