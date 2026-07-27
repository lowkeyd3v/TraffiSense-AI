from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)

    traffic_id = Column(Integer, ForeignKey("traffic.id"), nullable=False)

    predicted_congestion = Column(String(20), nullable=False)

    risk_score = Column(Float, nullable=False)

    recommended_action = Column(String(255), nullable=False)

    incident_type = Column(String(50), nullable=True)

    prediction_time = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    traffic = relationship(
        "Traffic",
        back_populates="prediction",
    )