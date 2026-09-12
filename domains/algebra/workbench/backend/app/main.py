import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.config import STATIC_DIR
from app.db.session import engine, Base, SessionLocal
from app.db.seed import seed_db
from app.routers import chapters, items, review, export, documents

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure database schema exists and seed database if empty
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_db(db)
    finally:
        db.close()
    yield

app = FastAPI(
    title="Algebra EKC Workbench API",
    description="Human review and certification surface for Empirical Knowledge Compilation",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_no_cache_headers(request, call_next):
    response = await call_next(request)
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

# Include API routers
app.include_router(chapters.router)
app.include_router(items.router)
app.include_router(review.router)
app.include_router(export.router)
app.include_router(documents.router)


@app.get("/assets/{filename:path}", include_in_schema=False)
async def serve_asset(filename: str):
    asset_file = os.path.join(STATIC_DIR, "assets", filename)
    if os.path.isfile(asset_file):
        return FileResponse(asset_file)

    # If an old cached JS bundle is requested, fallback to serving the active JS bundle
    if filename.endswith(".js"):
        js_files = list((STATIC_DIR / "assets").glob("*.js"))
        if js_files:
            return FileResponse(js_files[0], media_type="application/javascript")

    raise HTTPException(status_code=404, detail="Asset not found")

if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/{full_path:path}", include_in_schema=False)
async def serve_spa(full_path: str):
    if full_path.startswith("api/"):
        raise HTTPException(status_code=404, detail="Not Found")

    # Serve requested static file if it exists directly in STATIC_DIR
    target_file = os.path.join(STATIC_DIR, full_path)
    if full_path and os.path.isfile(target_file):
        return FileResponse(target_file)

    if full_path.startswith("assets/"):
        raise HTTPException(status_code=404, detail="Asset not found")

    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(
            index_path,
            headers={"Cache-Control": "no-cache, no-store, must-revalidate"}
        )
    return {"message": "Algebra EKC Workbench API running. Frontend assets not yet built."}



