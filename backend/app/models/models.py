from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from ..db.database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(32), nullable=False, default="editor")  # admin | editor | viewer
    is_active = Column(Integer, nullable=False, default=1)  # 1 = ativo (SQLite-friendly)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Plan(Base):
    __tablename__ = "plans"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), default="Plano de Inteligência")
    subject = Column(Text, nullable=False)
    time_window = Column(Text, nullable=False)
    user = Column(Text, nullable=False)
    purpose = Column(Text, nullable=False)
    deadline = Column(Text, nullable=False)
    aspects_essential = Column(Text, nullable=False)
    aspects_known = Column(Text, nullable=False)
    aspects_to_know = Column(Text, nullable=False)
    pirs = Column(Text, nullable=False, default="[]")
    collection = Column(Text, nullable=False, default="[]")
    extraordinary = Column(Text, nullable=True)
    security = Column(Text, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    share_token = Column(String(64), nullable=True, unique=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class PlanVersion(Base):
    __tablename__ = "plan_versions"
    id = Column(Integer, primary_key=True, index=True)
    plan_id = Column(Integer, ForeignKey("plans.id"), nullable=False, index=True)
    snapshot = Column(Text, nullable=False)  # JSON completo do plano antes do update
    label = Column(String(200), nullable=True)
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Evidence(Base):
    __tablename__ = "evidences"
    id = Column(Integer, primary_key=True, index=True)
    plan_id = Column(Integer, nullable=False, index=True)
    filename = Column(String(255), nullable=False)
    sha256 = Column(String(64), nullable=False)
    size = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
