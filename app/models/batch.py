import uuid
from datetime import datetime, timezone
from app.extensions import db

class Batch(db.Model):
    __tablename__ = "batches"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    total_hospitals = db.Column(db.Integer, nullable=False, default=0)
    processed_hospitals = db.Column(db.Integer, nullable=False, default=0)
    failed_hospitals = db.Column(db.Integer, nullable=False, default=0)
    processing_time_seconds = db.Column(db.Float, nullable=True)
    batch_activated = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    results = db.relationship("BatchHospitalResult", backref="batch", lazy=True, cascade="all, delete-orphan")

class BatchHospitalResult(db.Model):
    __tablename__ = "batch_hospital_results"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    batch_id = db.Column(db.String(36), db.ForeignKey("batches.id"), nullable=False)
    row = db.Column(db.Integer, nullable=False)
    hospital_id = db.Column(db.Integer, nullable=True)
    name = db.Column(db.String, nullable=False)
    status = db.Column(db.String(50), nullable=False)
    error_detail = db.Column(db.String, nullable=True)
