"""
src/api/main.py
Servidor FastAPI da aplicação Vértice Analytics (EloGroup Bootcamp).
Expõe endpoints analíticos com DuckDB e o Copiloto de Estoque com LangGraph.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes.analytics import router as analytics_router
from src.api.routes.audit import router as audit_router
from src.api.routes.copilot import router as copilot_router
from src.api.routes.roadmap import router as roadmap_router

app = FastAPI(
    title="Vértice Analytics API",
    description="Backend analítico minimalista para o case Vértice Retail (EloGroup Bootcamp 2026)",
    version="2.0.0"
)

# Configuração de CORS para permitir consumo do frontend Vite / React
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em ambiente local / dev permite todas as origens
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclusão dos routers
app.include_router(analytics_router, prefix="/api")
app.include_router(audit_router, prefix="/api")
app.include_router(copilot_router, prefix="/api")
app.include_router(roadmap_router, prefix="/api")


@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "app": "Vértice Analytics API",
        "version": "2.0.0"
    }


# Montagem do Frontend Estático (quando compilado para produção no Docker)
from pathlib import Path
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

FRONTEND_DIST = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"

if FRONTEND_DIST.exists():
    # Serve assets estáticos
    assets_dir = FRONTEND_DIST / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        # Se for uma chamada de API não capturada, deixa o FastAPI retornar 404
        if full_path.startswith("api/"):
            return FileResponse(FRONTEND_DIST / "index.html", status_code=404)
        
        target_file = FRONTEND_DIST / full_path
        if target_file.is_file():
            return FileResponse(target_file)
        return FileResponse(FRONTEND_DIST / "index.html")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.api.main:app", host="0.0.0.0", port=8501, reload=True)
