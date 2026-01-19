from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import Optional, List
from uuid import UUID


class ApplicationBase(BaseModel):
    company_name: str
    position: Optional[str] = None
    status: str = "uploaded"
    notes: Optional[str] = None


class ApplicationCreate(ApplicationBase):
    pass


class ApplicationUpdate(BaseModel):
    company_name: Optional[str] = None
    position: Optional[str] = None
    status: Optional[str] = None
    notes: Optional[str] = None


class ApplicationDocumentResponse(BaseModel):
    id: int
    filename: str
    doc_type: Optional[str] = None
    indexed: bool = False
    created_at: datetime

    @field_validator('indexed', mode='before')
    @classmethod
    def handle_none_indexed(cls, v):
        # Convert None to False for backwards compatibility
        return False if v is None else v

    class Config:
        from_attributes = True


class RenameApplicationRequest(BaseModel):
    new_name: str


class FolderResponse(BaseModel):
    id: int
    application_id: int
    name: str
    parent_id: Optional[int] = None
    path: str
    level: int
    created_at: datetime

    # Application tracking attributes
    is_bewerbung: Optional[bool] = False
    status: Optional[str] = None
    gehaltsangabe: Optional[float] = None
    gehaltsvorgabe: Optional[float] = None
    gehalt_schaetzung: Optional[float] = None

    class Config:
        from_attributes = True


class CreateFolderRequest(BaseModel):
    name: str
    parent_id: Optional[int] = None  # None = root level


class RenameFolderRequest(BaseModel):
    new_name: str


class MoveFolderRequest(BaseModel):
    target_parent_id: Optional[int] = None  # None = move to root


class UpdateFolderAttributesRequest(BaseModel):
    is_bewerbung: Optional[bool] = None
    status: Optional[str] = None
    gehaltsangabe: Optional[float] = None
    gehaltsvorgabe: Optional[float] = None
    gehalt_schaetzung: Optional[float] = None


class MoveDocumentRequest(BaseModel):
    target_folder_id: Optional[int] = None  # None = root level of application


class ApplicationStatusHistoryResponse(BaseModel):
    id: int
    old_status: Optional[str]
    new_status: str
    notes: Optional[str]
    changed_at: datetime

    class Config:
        from_attributes = True


class ApplicationResponse(ApplicationBase):
    id: int
    user_id: UUID
    upload_path: Optional[str]
    created_at: datetime
    updated_at: datetime
    document_count: int = 0
    # Document type breakdown for better overview
    cv_file: Optional[str] = None
    cv_document_id: Optional[int] = None
    cover_letter_file: Optional[str] = None
    cover_letter_document_id: Optional[int] = None
    job_description_file: Optional[str] = None
    job_description_document_id: Optional[int] = None
    other_files_count: int = 0

    class Config:
        from_attributes = True


class ApplicationDetailResponse(ApplicationResponse):
    documents: List[ApplicationDocumentResponse]
    status_history: List[ApplicationStatusHistoryResponse]


class StatusUpdateRequest(BaseModel):
    status: str
    notes: Optional[str] = None


class ChatMessageRequest(BaseModel):
    message: str
    provider: str = "ollama"


class ChatMessageResponse(BaseModel):
    message: str
    context_used: List[dict] = []
    action_taken: Optional[dict] = None


class ReportColumn(BaseModel):
    name: str
    type: str = "text"
    prompt: Optional[str] = None


class GenerateReportRequest(BaseModel):
    columns: List[str] = ["company_name", "position", "status", "document_count", "created_at"]
    custom_columns: List[ReportColumn] = []
    provider: str = "ollama"


class ReportResponse(BaseModel):
    columns: List[str]
    rows: List[dict]
    total_rows: int
    generated_at: datetime
