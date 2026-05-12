from datetime import datetime
from typing import List, Optional, Any
from sqlalchemy import String, Integer, Float, Boolean, ForeignKey, DateTime, JSON
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.sql import func

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    owned_datasets: Mapped[List["Dataset"]] = relationship(back_populates="owner", cascade="all, delete-orphan")
    uploaded_images: Mapped[List["DatasetImage"]] = relationship(back_populates="uploader")
    generated_codes: Mapped[List["CollaboratorCode"]] = relationship(back_populates="generator")
    collaborations: Mapped[List["Collaboration"]] = relationship(back_populates="user", cascade="all, delete-orphan")


class Dataset(Base):
    __tablename__ = "datasets"

    dataset_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(500))
    visibility: Mapped[bool] = mapped_column(Boolean, default=True) # EER'deki alan
    is_labeled: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    owner: Mapped["User"] = relationship(back_populates="owned_datasets")
    images: Mapped[List["DatasetImage"]] = relationship(back_populates="dataset", cascade="all, delete-orphan")
    collaborator_codes: Mapped[List["CollaboratorCode"]] = relationship(back_populates="dataset", cascade="all, delete-orphan")
    collaborations: Mapped[List["Collaboration"]] = relationship(back_populates="dataset", cascade="all, delete-orphan")
    labels: Mapped[List["Label"]] = relationship(back_populates="dataset", cascade="all, delete-orphan")
    analysis_results: Mapped[List["AnalysisResult"]] = relationship(back_populates="dataset", cascade="all, delete-orphan")
    data_files: Mapped[List["DataFile"]] = relationship(back_populates="dataset", cascade="all, delete-orphan")


class DatasetImage(Base):
    __tablename__ = "dataset_images"

    image_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    dataset_id: Mapped[int] = mapped_column(ForeignKey("datasets.dataset_id"), nullable=False)
    cloud_path: Mapped[str] = mapped_column(String(255), nullable=False)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_type: Mapped[str] = mapped_column(String(50), nullable=False)
    is_labeled: Mapped[bool] = mapped_column(Boolean, default=False)
    uploaded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    uploaded_by: Mapped[int] = mapped_column(ForeignKey("users.user_id"), nullable=False)

    # Relationships
    dataset: Mapped["Dataset"] = relationship(back_populates="images")
    uploader: Mapped["User"] = relationship(back_populates="uploaded_images")


class CollaboratorCode(Base):
    __tablename__ = "collaborator_codes"

    code_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    dataset_id: Mapped[int] = mapped_column(ForeignKey("datasets.dataset_id"), nullable=False)
    generated_by: Mapped[int] = mapped_column(ForeignKey("users.user_id"), nullable=False)
    code_value: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    used_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # Relationships
    dataset: Mapped["Dataset"] = relationship(back_populates="collaborator_codes")
    generator: Mapped["User"] = relationship(back_populates="generated_codes")


class Collaboration(Base):
    __tablename__ = "collaborations"

    collaboration_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    dataset_id: Mapped[int] = mapped_column(ForeignKey("datasets.dataset_id"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"), nullable=False)
    role: Mapped[str] = mapped_column(String(50), nullable=False) # örn: 'editor', 'viewer'
    joined_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    dataset: Mapped["Dataset"] = relationship(back_populates="collaborations")
    user: Mapped["User"] = relationship(back_populates="collaborations")


class Label(Base):
    __tablename__ = "labels"

    label_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    dataset_id: Mapped[int] = mapped_column(ForeignKey("datasets.dataset_id"), nullable=False)
    label_name: Mapped[str] = mapped_column(String(100), nullable=False)
    frequency: Mapped[int] = mapped_column(Integer, default=0)

    # Relationships
    dataset: Mapped["Dataset"] = relationship(back_populates="labels")


class AnalysisResult(Base):
    __tablename__ = "analysis_results"

    analysis_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    dataset_id: Mapped[int] = mapped_column(ForeignKey("datasets.dataset_id"), nullable=False)
    
    # EER'deki Analiz Metrikleri
    brightness_score: Mapped[float] = mapped_column(Float, nullable=False)
    contrast_score: Mapped[float] = mapped_column(Float, nullable=False)
    blurriness_score: Mapped[float] = mapped_column(Float, nullable=False)
    avg_object_count: Mapped[float] = mapped_column(Float, nullable=False)
    
    # Sınıf dağılımı için JSON alan
    class_distribution: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Özel CV analizleri için esneklik bayrakları
    is_bbox_active: Mapped[bool] = mapped_column(Boolean, default=False)
    is_segmentation_active: Mapped[bool] = mapped_column(Boolean, default=False)

    # Relationships
    dataset: Mapped["Dataset"] = relationship(back_populates="analysis_results")
    bboxes: Mapped[List["BoundingBox"]] = relationship(back_populates="analysis_result", cascade="all, delete-orphan")


class BoundingBox(Base):
    """
    Spesifik görsel verilerindeki tespitler için ayrılmış esnek tablo.
    """
    __tablename__ = "bounding_boxes"

    bbox_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    analysis_id: Mapped[int] = mapped_column(ForeignKey("analysis_results.analysis_id"), nullable=False)
    
    x_min: Mapped[float] = mapped_column(Float, nullable=False)
    y_min: Mapped[float] = mapped_column(Float, nullable=False)
    width: Mapped[float] = mapped_column(Float, nullable=False)
    height: Mapped[float] = mapped_column(Float, nullable=False)
    
    label_name: Mapped[str] = mapped_column(String(50), nullable=False)
    confidence_score: Mapped[Optional[float]] = mapped_column(Float)

    # Relationships
    analysis_result: Mapped["AnalysisResult"] = relationship(back_populates="bboxes")


class DataFile(Base):
    """
    Represents text files containing image data and labels stored in Cloudinary.
    All files are public and users can upload/delete their own files.
    """
    __tablename__ = "data_files"

    file_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    dataset_id: Mapped[int] = mapped_column(ForeignKey("datasets.dataset_id"), nullable=False)
    uploaded_by: Mapped[int] = mapped_column(ForeignKey("users.user_id"), nullable=False)
    
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_type: Mapped[str] = mapped_column(String(50), nullable=False)  # e.g., 'txt', 'csv', 'json'
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)  # size in bytes
    
    # Cloudinary storage information
    cloud_id: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    cloud_url: Mapped[str] = mapped_column(String(500), nullable=False)
    
    # Content metadata
    content_type: Mapped[str] = mapped_column(String(50), nullable=False)  # 'image_data', 'labels', 'mixed'
    description: Mapped[Optional[str]] = mapped_column(String(500))
    
    is_public: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    dataset: Mapped["Dataset"] = relationship()
    uploader: Mapped["User"] = relationship()