# Main FastAPI Application Entry Point
# This file imports and runs the Clean Architecture application

from app.presentation import app

if __name__ == "__main__":
    import uvicorn
    import os
    
    uvicorn.run(
        "main:app",
        host=os.getenv("API_HOST", "0.0.0.0"),
        port=int(os.getenv("API_PORT", "8000")),
        reload=os.getenv("API_RELOAD", "true").lower() == "true",
        log_level=os.getenv("API_LOG_LEVEL", "info").lower()
    )
