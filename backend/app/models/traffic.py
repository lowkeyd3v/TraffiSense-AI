from sqlalchemy import Column, DateTime, Float, ForeignKey, Index, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Traffic(Base):
    __tablename__ = "traffic"

    __table_args__ = (
        Index("idx_location", "location"),
        Index("idx_congestion_level", "congestion_level"),
        Index("idx_weather_condition", "weather_condition"),
        Index("idx_road_status", "road_status"),
        Index("idx_road_type", "road_type"),
        Index("idx_timestamp", "timestamp"),
        Index("idx_created_by", "created_by"),
    )

    id = Column(Integer, primary_key=True, index=True)

    location = Column(String(100), nullable=False)

    vehicle_count = Column(Integer, nullable=False)

    average_speed = Column(Float, nullable=False)

    congestion_level = Column(String(20), nullable=False)

    weather_condition = Column(String(50), nullable=False)

    road_status = Column(String(50), nullable=False)

    road_type = Column(String(50), nullable=False)

    timestamp = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    created_by = Column(Integer, ForeignKey("users.id"))

    user = relationship(
        "User",
        back_populates="traffic_records",
    )

    prediction = relationship(
        "Prediction",
        back_populates="traffic",
        uselist=False,
        cascade="all, delete-orphan",
    )