from sqlalchemy import Column, String, Float, DateTime, JSON
from sqlalchemy.sql import func
from app.core.database import Base

class AnomalyScore(Base):
    __tablename__ = "anomaly_scores"

    # Primary Key
    ticker = Column(String(20), primary_key=True, index=True)

    # Anomaly Scores
    anomaly_score = Column(Float, nullable=False)  # 0-1, higher = more anomalous
    isolation_forest_score = Column(Float, nullable=True)

    # Features Used for Detection
    features_used = Column(JSON, nullable=True)

    # Timestamp
    detected_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def to_dict(self):
        return {
            "ticker": self.ticker,
            "anomaly_score": self.anomaly_score,
            "isolation_forest_score": self.isolation_forest_score,
            "features_used": self.features_used,
            "detected_at": self.detected_at.isoformat() if self.detected_at else None
        }
