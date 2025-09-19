"""Main entry point for the backend application."""

if __name__ == "__main__":
    import uvicorn
    from server import app
    from config import settings
    
    uvicorn.run(
        app,
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )