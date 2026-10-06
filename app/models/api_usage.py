from sqlalchemy import Column, Integer, String, DateTime, JSON
from sqlalchemy.sql import func
from app.core.database import Base

class APIUsage(Base):
    __tablename__ = "api_usage"

    # Primary Key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # API Details
    endpoint = Column(String(100), nullable=False, index=True)
    provider = Column(String(50), nullable=False, index=True)  # SECTORS_API | GEMINI
    tokens_used = Column(Integer, nullable=False, default=0)

    # Request Info
    request_params = Column(JSON, nullable=True)

    # Timestamp
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    def to_dict(self):
        return {
            "id": self.id,
            "endpoint": self.endpoint,
            "provider": self.provider,
            "tokens_used": self.tokens_used,
            "request_params": self.request_params,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None
        }
