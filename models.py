from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, Float, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class User(Base):
    __tablename__ = "users"
    
    user_id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    
    # Relationships
    outfits = relationship("Outfit", back_populates="user", cascade="all, delete-orphan")

class Outfit(Base):
    __tablename__ = "outfits"
    
    outfit_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"))
    photo_url = Column(Text, nullable=False)
    detected_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    
    # Relationships
    user = relationship("User", back_populates="outfits")
    clothing_items = relationship("ClothingItem", back_populates="outfit", cascade="all, delete-orphan")
    recommendations = relationship("Recommendation", back_populates="outfit", cascade="all, delete-orphan")

class ClothingItem(Base):
    __tablename__ = "clothing_items"
    
    item_id = Column(Integer, primary_key=True)
    outfit_id = Column(Integer, ForeignKey("outfits.outfit_id", ondelete="CASCADE"))
    type = Column(String(50), nullable=False)
    color_palette = Column(JSON)  # Store RGB values as JSON
    pattern = Column(String(50))
    bounding_box = Column(JSON)  # Store bounding box coordinates as JSON
    
    # Relationships
    outfit = relationship("Outfit", back_populates="clothing_items")

class FashionTrend(Base):
    __tablename__ = "fashion_trends"
    
    trend_id = Column(Integer, primary_key=True)
    season = Column(String(20))
    year = Column(Integer)
    clothing_type = Column(String(50))
    trending_colors = Column(JSON)
    popularity_score = Column(Float)

class Recommendation(Base):
    __tablename__ = "recommendations"
    
    rec_id = Column(Integer, primary_key=True)
    outfit_id = Column(Integer, ForeignKey("outfits.outfit_id", ondelete="CASCADE"))
    suggestion = Column(Text)
    reasoning = Column(Text)
    generated_image_url = Column(Text)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    
    # Relationships
    outfit = relationship("Outfit", back_populates="recommendations")
