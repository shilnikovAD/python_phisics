"""
FastAPI Application for GitHub Repository Search
"""

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from endpoints.search import router as search_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager"""
    # Create static directory if it doesn't exist
    os.makedirs("static", exist_ok=True)
    yield


app = FastAPI(
    title="GitHub Repository Search API",
    description="API for searching GitHub repositories and exporting results to CSV",
    version="1.0.0",
    lifespan=lifespan,
)

# Include routers
app.include_router(search_router, prefix="/api", tags=["search"])


@app.get("/")
async def root():
    """Root endpoint"""
    return JSONResponse(
        content={
            "message": "GitHub Repository Search API",
            "docs": "/docs",
            "endpoints": {
                "search": "/api/search",
            },
        }
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
