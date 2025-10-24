from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

app = FastAPI(title="Simple Test", description="Test interface without TTS")

@app.get("/")
async def read_root():
    """Serve the main HTML client"""
    return FileResponse("index.html", media_type="text/html")

@app.get("/voices-select")
async def get_voices_for_select():
    """Mock voices for testing"""
    return {"voices": ["Test Voice 1", "Test Voice 2", "Test Voice 3"]}

@app.get("/health")
async def health_check():
    """Health check"""
    return {"status": "healthy", "mode": "test"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
