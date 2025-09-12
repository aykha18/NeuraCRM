#!/usr/bin/env python3
"""
Simple test server to verify basic functionality.
"""

from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Simple server is running"}

@app.get("/api/ping")
def ping():
    return {"status": "ok", "message": "pong"}

@app.get("/health")
def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    print("Starting simple server...")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
