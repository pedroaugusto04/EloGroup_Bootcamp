"""
src/api/routes/deliverables.py
Rotas para listagem, leitura e edição dos documentos e relatórios entregáveis
do Bootcamp EloGroup 2026 localizados em docs/entregaveis/.
"""

import os
from datetime import datetime
from pathlib import Path
from typing import List
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter(prefix="/deliverables", tags=["deliverables"])


def get_docs_dir() -> Path:
    """Resolve o diretório docs/entregaveis com fallback para Docker e ambiente local."""
    # 1. Variável de ambiente explícita
    env_docs = os.getenv("DOCS_DIR")
    if env_docs:
        p = Path(env_docs)
        if p.exists():
            return p

    # 2. Resolução relativa a partir de src/api/routes/deliverables.py
    try:
        base_dir = Path(__file__).resolve().parent.parent.parent.parent
        cand1 = base_dir / "docs" / "entregaveis"
        if cand1.exists():
            return cand1
    except Exception:
        pass

    # 3. Caminho padrão do contêiner Docker (/app/docs/entregaveis)
    cand2 = Path("/app/docs/entregaveis")
    if cand2.exists():
        return cand2

    # 4. Caminho relativo ao diretório de trabalho atual (CWD)
    cand3 = Path.cwd() / "docs" / "entregaveis"
    if cand3.exists():
        return cand3

    return Path(__file__).resolve().parent.parent.parent.parent / "docs" / "entregaveis"

# Catálogo fixo e ordenado dos entregáveis com metadados executivos
DELIVERABLES_CATALOG = [
    {
        "id": "01_relatorio_diagnostico_estrategico",
        "filename": "01_relatorio_diagnostico_estrategico.md",
        "title": "Diagnóstico Executivo e Hipóteses",
        "subtitle": "",
        "tag": "Estratégia",
        "order": 1,
    },
    {
        "id": "02_business_case_modelagem_financeira",
        "filename": "02_business_case_modelagem_financeira.md",
        "title": "Business Case e Modelagem Financeira",
        "subtitle": "",
        "tag": "Finanças",
        "order": 2,
    },
    {
        "id": "03_auditoria_dados_memoria_calculo",
        "filename": "03_auditoria_dados_memoria_calculo.md",
        "title": "Auditoria de Dados",
        "subtitle": "",
        "tag": "Auditoria",
        "order": 3,
    },
    {
        "id": "04_arquitetura_ia_governanca",
        "filename": "04_arquitetura_ia_governanca.md",
        "title": "Arquitetura de IA e Governança Técnica",
        "subtitle": "",
        "tag": "Tech & IA",
        "order": 4,
    },
    {
        "id": "05_desenvolvimento_e_metodologia",
        "filename": "DEVELOPMENT.md",
        "title": "Desenvolvimento e Racional Metodológico",
        "subtitle": "",
        "tag": "Metodologia",
        "order": 5,
    },
]


class DeliverableMeta(BaseModel):
    id: str
    filename: str
    title: str
    subtitle: str
    tag: str
    order: int
    word_count: int
    updated_at: str


class DeliverableDetail(DeliverableMeta):
    content: str


class DeliverableUpdateRequest(BaseModel):
    content: str = Field(..., description="Novo conteúdo em Markdown do documento")


def _get_file_path(doc_id: str) -> Path:
    meta = next((item for item in DELIVERABLES_CATALOG if item["id"] == doc_id), None)
    if not meta:
        raise HTTPException(status_code=404, detail=f"Entregável '{doc_id}' não encontrado no catálogo.")
    docs_dir = get_docs_dir()
    file_path = docs_dir / meta["filename"]
    if not file_path.exists():
        # Fallback to repo root or parent of docs
        repo_root = docs_dir.parent.parent if docs_dir.name == "entregaveis" else docs_dir.parent
        alt_path = repo_root / meta["filename"]
        if alt_path.exists():
            return alt_path
        cand_root = Path(__file__).resolve().parent.parent.parent.parent / meta["filename"]
        if cand_root.exists():
            return cand_root
        raise HTTPException(status_code=404, detail=f"Arquivo '{meta['filename']}' não encontrado em {docs_dir}.")
    return file_path


@router.get("", response_model=List[DeliverableMeta])
def list_deliverables():
    """Retorna o catálogo de documentos entregáveis com metadados e estatísticas."""
    result = []
    for item in sorted(DELIVERABLES_CATALOG, key=lambda x: x["order"]):
        try:
            file_path = _get_file_path(item["id"])
            content = file_path.read_text(encoding="utf-8")
            word_count = len(content.split())
            mtime = datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
        except HTTPException:
            word_count = 0
            mtime = datetime.now().isoformat()

        result.append(
            DeliverableMeta(
                id=item["id"],
                filename=item["filename"],
                title=item["title"],
                subtitle=item["subtitle"],
                tag=item["tag"],
                order=item["order"],
                word_count=word_count,
                updated_at=mtime,
            )
        )
    return result


import io
import zipfile
from fastapi.responses import Response, FileResponse


@router.get("/export/zip")
def download_all_deliverables_zip():
    """Gera e retorna um arquivo .zip contendo todos os documentos entregáveis em Markdown."""
    docs_dir = get_docs_dir()
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for item in sorted(DELIVERABLES_CATALOG, key=lambda x: x["order"]):
            try:
                file_path = _get_file_path(item["id"])
                if file_path.exists():
                    zip_file.write(file_path, arcname=item["filename"])
            except HTTPException:
                pass
        # Inclui também assets visuais (ex: arvore_hipoteses.svg)
        assets_dir = docs_dir.parent / "assets"
        if assets_dir.exists():
            for asset_file in assets_dir.glob("*"):
                if asset_file.is_file():
                    zip_file.write(asset_file, arcname=f"assets/{asset_file.name}")
        # Inclui também guia de submissão se existir
        guia = docs_dir / "00_guia_de_submissao_e_links.md"
        if guia.exists():
            zip_file.write(guia, arcname="00_guia_de_submissao_e_links.md")

    zip_buffer.seek(0)
    return Response(
        content=zip_buffer.getvalue(),
        media_type="application/zip",
        headers={
            "Content-Disposition": "attachment; filename=vertice-documentos-executivos.zip"
        },
    )


@router.get("/assets/{filename}")
def get_deliverable_asset(filename: str):
    """Serve arquivos de assets estáticos dos entregáveis (ex: arvore_hipoteses.svg)."""
    docs_dir = get_docs_dir()
    asset_path = docs_dir.parent / "assets" / filename
    if not asset_path.exists():
        asset_path = docs_dir.parent.parent / "frontend" / "public" / "assets" / filename
    if asset_path.exists():
        media_type = "image/svg+xml" if filename.endswith(".svg") else "application/octet-stream"
        return FileResponse(path=str(asset_path), media_type=media_type)
    raise HTTPException(status_code=404, detail=f"Asset '{filename}' não encontrado.")


@router.get("/{doc_id}/download")
def download_deliverable_file(doc_id: str):
    """Retorna o arquivo Markdown individual do entregável para download direto."""
    file_path = _get_file_path(doc_id)
    return FileResponse(
        path=str(file_path),
        filename=file_path.name,
        media_type="text/markdown; charset=utf-8",
        headers={
            "Content-Disposition": f"attachment; filename={file_path.name}"
        },
    )


@router.get("/{doc_id}", response_model=DeliverableDetail)
def get_deliverable(doc_id: str):
    """Retorna o conteúdo completo e os metadados de um entregável específico."""
    meta = next((item for item in DELIVERABLES_CATALOG if item["id"] == doc_id), None)
    if not meta:
        raise HTTPException(status_code=404, detail=f"Entregável '{doc_id}' não encontrado.")

    file_path = _get_file_path(doc_id)
    content = file_path.read_text(encoding="utf-8")
    word_count = len(content.split())
    mtime = datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()

    return DeliverableDetail(
        id=meta["id"],
        filename=meta["filename"],
        title=meta["title"],
        subtitle=meta["subtitle"],
        tag=meta["tag"],
        order=meta["order"],
        word_count=word_count,
        updated_at=mtime,
        content=content,
    )


@router.put("/{doc_id}", response_model=DeliverableDetail)
def update_deliverable(doc_id: str, body: DeliverableUpdateRequest):
    """Atualiza o conteúdo Markdown de um documento entregável."""
    meta = next((item for item in DELIVERABLES_CATALOG if item["id"] == doc_id), None)
    if not meta:
        raise HTTPException(status_code=404, detail=f"Entregável '{doc_id}' não encontrado.")

    file_path = _get_file_path(doc_id)
    # Grava o conteúdo atualizado com codificação UTF-8
    file_path.write_text(body.content, encoding="utf-8")

    # Sincroniza cópia na raiz do repositório se for DEVELOPMENT.md
    if meta["filename"] == "DEVELOPMENT.md":
        try:
            docs_dir = get_docs_dir()
            repo_root = docs_dir.parent.parent if docs_dir.name == "entregaveis" else docs_dir.parent
            root_file = repo_root / "DEVELOPMENT.md"
            if root_file.exists() and root_file.resolve() != file_path.resolve():
                root_file.write_text(body.content, encoding="utf-8")
        except Exception:
            pass

    word_count = len(body.content.split())
    mtime = datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()

    return DeliverableDetail(
        id=meta["id"],
        filename=meta["filename"],
        title=meta["title"],
        subtitle=meta["subtitle"],
        tag=meta["tag"],
        order=meta["order"],
        word_count=word_count,
        updated_at=mtime,
        content=body.content,
    )
