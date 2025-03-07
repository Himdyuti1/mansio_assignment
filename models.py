from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base

Base=declarative_base()
    
class Property(Base):
    __tablename__="properties"

    id=Column(Integer, primary_key=True, index=True)
    title=Column(String,nullable=False)
    description=Column(String,nullable=True)
    price=Column(Float,nullable=False)
    status=Column(String,default="available")
    ai_keywords=Column(String,nullable=True)
    stripe_product_id=Column(String,nullable=True)