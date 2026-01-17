"""Application Tracker API Endpoints"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List
from datetime import datetime
import re

from backend.database import get_db
from backend.models.application import (
    Application,
    ApplicationDocument,
    ApplicationStatusHistory,
    ApplicationChatMessage
)
from backend.models.user import User
from backend.schemas.application import (
    ApplicationResponse,
    ApplicationDetailResponse,
    StatusUpdateRequest,
    ChatMessageRequest,
    ChatMessageResponse,
    GenerateReportRequest,
    ReportResponse
)
from backend.services.application_service import DocumentParser, guess_doc_type
from backend.services.vector_service import VectorService
from backend.services.llm_gateway import llm_gateway
from backend.auth.dependencies import current_active_user

router = APIRouter()


@router.get("/overview", response_model=List[ApplicationResponse])
async def get_applications_overview(
    user: User = Depends(current_active_user),
    db: Session = Depends(get_db)
):
    """Get overview of all applications with document counts"""
    applications = db.query(Application).filter(Application.user_id == user.id).all()

    result = []
    for app in applications:
        doc_count = db.query(ApplicationDocument).filter(
            ApplicationDocument.application_id == app.id
        ).count()

        result.append(ApplicationResponse(
            id=app.id,
            user_id=app.user_id,
            company_name=app.company_name,
            position=app.position,
            status=app.status,
            notes=app.notes,
            upload_path=app.upload_path,
            created_at=app.created_at,
            updated_at=app.updated_at,
            document_count=doc_count
        ))

    return result


@router.get("/{application_id}", response_model=ApplicationDetailResponse)
async def get_application_detail(
    application_id: int,
    user: User = Depends(current_active_user),
    db: Session = Depends(get_db)
):
    """Get detailed application info with documents and status history"""
    app = db.query(Application).filter(
        Application.id == application_id,
        Application.user_id == user.id
    ).first()

    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    documents = db.query(ApplicationDocument).filter(
        ApplicationDocument.application_id == application_id
    ).all()

    history = db.query(ApplicationStatusHistory).filter(
        ApplicationStatusHistory.application_id == application_id
    ).order_by(ApplicationStatusHistory.changed_at.desc()).all()

    return ApplicationDetailResponse(
        id=app.id,
        user_id=app.user_id,
        company_name=app.company_name,
        position=app.position,
        status=app.status,
        notes=app.notes,
        upload_path=app.upload_path,
        created_at=app.created_at,
        updated_at=app.updated_at,
        document_count=len(documents),
        documents=documents,
        status_history=history
    )


@router.patch("/{application_id}/status")
async def update_application_status(
    application_id: int,
    status_update: StatusUpdateRequest,
    user: User = Depends(current_active_user),
    db: Session = Depends(get_db)
):
    """Update application status and log to history"""
    app = db.query(Application).filter(
        Application.id == application_id,
        Application.user_id == user.id
    ).first()

    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    history_entry = ApplicationStatusHistory(
        application_id=application_id,
        old_status=app.status,
        new_status=status_update.status,
        notes=status_update.notes
    )
    db.add(history_entry)

    app.status = status_update.status
    app.updated_at = datetime.utcnow()

    db.commit()

    return {
        "success": True,
        "application_id": application_id,
        "old_status": history_entry.old_status,
        "new_status": history_entry.new_status
    }


@router.delete("/{application_id}")
async def delete_application(
    application_id: int,
    user: User = Depends(current_active_user),
    db: Session = Depends(get_db)
):
    """Delete application and all associated documents (CASCADE)"""
    app = db.query(Application).filter(
        Application.id == application_id,
        Application.user_id == user.id
    ).first()

    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    company_name = app.company_name
    db.delete(app)
    db.commit()

    return {
        "success": True,
        "message": f"Application for {company_name} deleted successfully"
    }


@router.post("/upload/directory")
async def upload_application_directory(
    file: UploadFile = File(...),
    company_name: str = Form(...),
    position: str = Form(None),
    user: User = Depends(current_active_user),
    db: Session = Depends(get_db)
):
    """Upload a ZIP file containing application documents"""
    if not file.filename.endswith('.zip'):
        raise HTTPException(status_code=400, detail="Only ZIP files are supported")

    application = Application(
        user_id=user.id,
        company_name=company_name,
        position=position,
        status="uploaded",
        upload_path=file.filename
    )
    db.add(application)
    db.commit()
    db.refresh(application)

    content = await file.read()
    parser = DocumentParser()
    vector_service = VectorService()

    processed_files = []
    errors = []

    try:
        files = await parser.extract_zip(content)

        for file_path, filename, file_data in files:
            try:
                doc_type = guess_doc_type(file_path)
                extracted_text = await parser.parse_file(filename, file_data)
                embedding = await vector_service.generate_embedding(extracted_text)

                document = ApplicationDocument(
                    application_id=application.id,
                    filename=filename,
                    file_path=file_path,
                    doc_type=doc_type,
                    content=extracted_text,
                    embedding=embedding
                )
                db.add(document)

                processed_files.append({
                    "filename": filename,
                    "type": doc_type,
                    "chars": len(extracted_text) if extracted_text else 0
                })

            except Exception as e:
                errors.append({"filename": file_path, "error": str(e)})

        db.commit()

    except Exception as e:
        db.rollback()
        db.delete(application)
        db.commit()
        raise HTTPException(status_code=400, detail=f"ZIP processing failed: {str(e)}")

    return {
        "success": True,
        "application_id": application.id,
        "company_name": company_name,
        "processed_files": processed_files,
        "total_files": len(processed_files),
        "errors": errors
    }


@router.post("/chat/message", response_model=ChatMessageResponse)
async def send_chat_message(
    request: ChatMessageRequest,
    user: User = Depends(current_active_user),
    db: Session = Depends(get_db)
):
    """Send chat message and get response with RAG"""
    user_message = ApplicationChatMessage(
        user_id=user.id,
        role="user",
        content=request.message
    )
    db.add(user_message)
    db.commit()

    action_taken = await _check_status_update(request.message, user.id, db)

    vector_service = VectorService()
    query_embedding = await vector_service.generate_embedding(request.message)

    documents = db.query(ApplicationDocument).join(Application).filter(
        Application.user_id == user.id
    ).all()

    relevant_docs = []
    for doc in documents:
        if doc.embedding:
            similarity = vector_service.cosine_similarity(query_embedding, doc.embedding)
            if similarity > 0.3:
                relevant_docs.append({
                    "id": doc.id,
                    "filename": doc.filename,
                    "similarity": similarity,
                    "content": doc.content[:500] if doc.content else ""
                })

    relevant_docs.sort(key=lambda x: x["similarity"], reverse=True)
    relevant_docs = relevant_docs[:5]

    applications = db.query(Application).filter(Application.user_id == user.id).all()
    app_summary = "\n".join([
        f"- {app.company_name} ({app.position or 'N/A'}): {app.status}"
        for app in applications
    ])

    context_parts = []
    if app_summary:
        context_parts.append(f"=== Bewerbungen ===\n{app_summary}")
    if relevant_docs:
        docs_text = "\n\n".join([
            f"Dokument: {doc['filename']} (Relevanz: {doc['similarity']:.2f})\n{doc['content']}"
            for doc in relevant_docs
        ])
        context_parts.append(f"=== Relevante Dokumente ===\n{docs_text}")

    context = "\n\n".join(context_parts)

    system_prompt = """Du bist ein intelligenter Assistent für Bewerbungsmanagement.
Beantworte Fragen zu Bewerbungen und Dokumenten präzise auf Deutsch."""

    full_prompt = f"Kontext:\n{context}\n\nFrage: {request.message}\n\nAntwort:"

    response_text = await llm_gateway.generate(
        message=full_prompt,
        system_prompt=system_prompt,
        llm_type=request.provider,
        temperature=0.7,
        max_tokens=1500
    )

    assistant_message = ApplicationChatMessage(
        user_id=user.id,
        role="assistant",
        content=response_text
    )
    db.add(assistant_message)
    db.commit()

    return ChatMessageResponse(
        message=response_text,
        context_used=relevant_docs,
        action_taken=action_taken
    )


async def _check_status_update(message: str, user_id, db: Session):
    """Check if message contains status update intent"""
    message_lower = message.lower()

    status_map = {
        'uploaded': ['hochgeladen', 'uploaded'],
        'applied': ['beworben', 'applied'],
        'interview': ['interview', 'gespräch'],
        'offer': ['zusage', 'offer'],
        'rejected': ['absage', 'rejected'],
        'accepted': ['angenommen', 'accepted']
    }

    patterns = [
        r'(?:status\s+)?([a-z0-9äöüß\s]+?)\s+(?:auf|to)\s+([a-z\s]+)',
        r'update\s+([a-z0-9äöüß\s]+?)\s+(?:auf|to)\s+([a-z\s]+)'
    ]

    for pattern in patterns:
        match = re.search(pattern, message_lower)
        if match:
            company_partial = match.group(1).strip()
            status_keyword = match.group(2).strip()

            new_status = None
            for status, keywords in status_map.items():
                if any(kw in status_keyword for kw in keywords):
                    new_status = status
                    break

            if new_status:
                apps = db.query(Application).filter(Application.user_id == user_id).all()
                for app in apps:
                    if company_partial in app.company_name.lower():
                        old_status = app.status
                        app.status = new_status
                        history = ApplicationStatusHistory(
                            application_id=app.id,
                            old_status=old_status,
                            new_status=new_status,
                            notes=f"Via chat: {message}"
                        )
                        db.add(history)
                        db.commit()
                        return {
                            "action": "status_update",
                            "company": app.company_name,
                            "old_status": old_status,
                            "new_status": new_status
                        }
    return None


@router.get("/reports/status")
async def get_status_report(
    user: User = Depends(current_active_user),
    db: Session = Depends(get_db)
):
    """Get status report"""
    status_counts = db.query(
        Application.status,
        func.count(Application.id).label('count')
    ).filter(Application.user_id == user.id).group_by(Application.status).all()

    total = db.query(func.count(Application.id)).filter(
        Application.user_id == user.id
    ).scalar()

    recent = db.query(ApplicationStatusHistory).join(Application).filter(
        Application.user_id == user.id
    ).order_by(desc(ApplicationStatusHistory.changed_at)).limit(10).all()

    return {
        "total_applications": total,
        "status_distribution": [{"status": s, "count": c} for s, c in status_counts],
        "recent_changes": [{
            "application_id": r.application_id,
            "old_status": r.old_status,
            "new_status": r.new_status,
            "changed_at": r.changed_at
        } for r in recent]
    }


@router.post("/reports/generate", response_model=ReportResponse)
async def generate_report(
    request: GenerateReportRequest,
    user: User = Depends(current_active_user),
    db: Session = Depends(get_db)
):
    """Generate custom report"""
    apps = db.query(Application).filter(Application.user_id == user.id).all()

    columns = request.columns + [c.name for c in request.custom_columns]
    rows = []

    for app in apps:
        row = {}
        doc_count = db.query(ApplicationDocument).filter(
            ApplicationDocument.application_id == app.id
        ).count()

        for col in request.columns:
            if col == "company_name": row[col] = app.company_name
            elif col == "position": row[col] = app.position or "N/A"
            elif col == "status": row[col] = app.status
            elif col == "document_count": row[col] = doc_count
            elif col == "created_at": row[col] = app.created_at.isoformat()

        for custom_col in request.custom_columns:
            if custom_col.prompt:
                docs = db.query(ApplicationDocument).filter(
                    ApplicationDocument.application_id == app.id
                ).limit(2).all()
                doc_text = "\n".join([d.content[:300] for d in docs if d.content])

                prompt = f"Firma: {app.company_name}\nPosition: {app.position}\nDokumente: {doc_text}\n\n{custom_col.prompt}"

                value = await llm_gateway.generate(
                    message=prompt,
                    llm_type=request.provider,
                    max_tokens=150
                )

                if custom_col.type == "number":
                    nums = re.findall(r'\d+', value)
                    row[custom_col.name] = int(nums[0]) if nums else 0
                else:
                    row[custom_col.name] = value.strip()
            else:
                row[custom_col.name] = ""

        rows.append(row)

    return ReportResponse(
        columns=columns,
        rows=rows,
        total_rows=len(rows),
        generated_at=datetime.utcnow()
    )
