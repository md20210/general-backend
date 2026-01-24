"""Pydantic schemas for tax case management"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


# Tax Case Schemas
class TaxCaseCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    notes: Optional[str] = None


class TaxCaseUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    notes: Optional[str] = None
    status: Optional[str] = None


class TaxCaseResponse(BaseModel):
    id: int
    name: str
    status: str
    validated: bool
    document_count: int = 0
    created_at: datetime

    class Config:
        from_attributes = True


class TaxCaseDetailResponse(BaseModel):
    id: int
    name: str
    status: str
    validated: bool
    notes: Optional[str]
    document_count: int = 0
    extracted_data: Dict[str, Any] = {}
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Folder Schemas
class FolderCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    parent_id: Optional[int] = None


class FolderResponse(BaseModel):
    id: int
    tax_case_id: int
    name: str
    parent_id: Optional[int]
    path: str
    level: int
    created_at: datetime

    class Config:
        from_attributes = True


# Document Schemas
class DocumentResponse(BaseModel):
    id: int
    tax_case_id: int
    folder_id: Optional[int]
    filename: str
    doc_type: Optional[str]
    validated: bool
    created_at: datetime

    class Config:
        from_attributes = True


# Extracted Data Schemas
class ExtractedDataCreate(BaseModel):
    field_name: str
    field_value: str
    field_type: Optional[str] = None
    confidence: Optional[float] = None
    document_id: Optional[int] = None


class ExtractedDataUpdate(BaseModel):
    field_value: str
    confirmed: Optional[bool] = False


class ExtractedDataResponse(BaseModel):
    id: int
    tax_case_id: int
    document_id: Optional[int]
    field_name: str
    field_value: str
    field_type: Optional[str]
    confidence: Optional[float]
    confirmed: bool
    edited: bool
    original_value: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Authentication Schemas
class AuthRegisterRequest(BaseModel):
    email: str = Field(..., pattern=r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")


class AuthLoginRequest(BaseModel):
    email: str
    password: str


class AuthResponse(BaseModel):
    token: str
    email: str
    message: str


# Data Update Schema
class ExtractedDataBulkUpdate(BaseModel):
    data: Dict[str, Any]
