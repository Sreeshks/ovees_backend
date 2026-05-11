from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv
load_dotenv()
from database import init_db
from routers import admin_router, public_router

# # Load environment variables
# load_dotenv()

# Lifespan context manager for startup/shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    init_db()
    print("✅ Database initialized successfully!")
    yield
    # Shutdown (cleanup if needed)
    print("👋 Shutting down...")

# Initialize FastAPI app
app = FastAPI(
    title="Ovees Jewelry Store API",
    description="Backend API for Ovees Jewelry E-commerce Platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS Configuration
origins = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(admin_router)
app.include_router(public_router)

# Serve static files (CSS/JS/images) for admin UI and any frontend
app.mount("/static", StaticFiles(directory="static"), name="static")

# Root endpoint
@app.get("/")
def root():
    return {
        "message": "Welcome to Ovees Backend API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }

# Health check
@app.get("/health")
def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
