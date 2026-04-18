from pydantic import BaseModel, Field
from typing import List, Optional, Literal

# Limites de tamanho para prevenir DoS por payloads grandes
MAX_ITEM = 1000
MAX_TEXT = 5000
MAX_TITLE = 200
MAX_RESEARCH_NOTES = 2000
MAX_PIR_QUESTION = 500
MAX_DATE = 50
MAX_LIST_ITEMS = 100

class Subject(BaseModel):
    what: str = Field(..., max_length=MAX_ITEM)
    who: str = Field(..., max_length=MAX_ITEM)
    where: str = Field(..., max_length=MAX_ITEM)

class TimeWindow(BaseModel):
    start: str = Field(..., max_length=MAX_DATE)
    end: str = Field(..., max_length=MAX_DATE)
    research_notes: Optional[str] = Field("", max_length=MAX_RESEARCH_NOTES)

class UserInfo(BaseModel):
    principal: str = Field(..., max_length=MAX_ITEM)
    others: Optional[str] = Field("", max_length=MAX_ITEM)
    depth: Literal["executivo","gerencial","tecnico"]
    secrecy: Literal["publico","restrito","confidencial","secreto"]

class Deadline(BaseModel):
    date: str = Field(..., max_length=MAX_DATE)
    urgency: Literal["baixa","media","alta","critica"]

class PIR(BaseModel):
    aspect_ref: Optional[int] = None
    question: str = Field(..., max_length=MAX_PIR_QUESTION)
    priority: Literal["baixa","media","alta","critica"] = "media"
    justification: Optional[str] = Field("", max_length=MAX_ITEM)

class CollectionTask(BaseModel):
    pir_index: int
    source: str = Field(..., max_length=MAX_ITEM)
    method: str = Field(..., max_length=MAX_ITEM)
    frequency: Literal["unico","diario","semanal","mensal"] = "unico"
    owner: str = Field(..., max_length=MAX_ITEM)
    sla_hours: int = 0

class EvidenceRead(BaseModel):
    id: int
    filename: str = Field(..., max_length=255)
    sha256: str = Field(..., max_length=64)
    size: int

class PlanBase(BaseModel):
    title: str = Field("Plano de Inteligência", max_length=MAX_TITLE)
    subject: Subject
    time_window: TimeWindow
    user: UserInfo
    purpose: str = Field(..., max_length=MAX_TEXT)
    deadline: Deadline
    aspects_essential: List[str] = Field(default_factory=list, max_length=MAX_LIST_ITEMS)
    aspects_known: List[str] = Field(default_factory=list, max_length=MAX_LIST_ITEMS)
    aspects_to_know: List[str] = Field(default_factory=list, max_length=MAX_LIST_ITEMS)
    pirs: List[PIR] = Field(default_factory=list, max_length=MAX_LIST_ITEMS)
    collection: List[CollectionTask] = Field(default_factory=list, max_length=MAX_LIST_ITEMS)
    extraordinary: List[str] = Field(default_factory=list, max_length=MAX_LIST_ITEMS)
    security: List[str] = Field(default_factory=list, max_length=MAX_LIST_ITEMS)

class PlanCreate(PlanBase):
    pass

class PlanRead(PlanBase):
    id: int
    evidences: List[EvidenceRead] = Field(default_factory=list)
    owner_id: Optional[int] = None
    class Config:
        from_attributes = True


class PlanVersionRead(BaseModel):
    id: int
    plan_id: int
    label: Optional[str] = None
    created_at: Optional[str] = None
    created_by_id: Optional[int] = None


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserCreate(BaseModel):
    email: str = Field(..., max_length=255)
    password: str = Field(..., min_length=8, max_length=128)
    role: Literal["admin", "editor", "viewer"] = "editor"


class UserRead(BaseModel):
    id: int
    email: str
    role: str
    class Config:
        from_attributes = True


class PlanUpdate(PlanBase):
    version_label: Optional[str] = Field(None, max_length=200)
