from sqlalchemy import Column, Integer, String, TIMESTAMP, text, BigInteger
from app.database import Base

class original_img(Base):
    __tablename__ = "original_imgs"

    id= Column(Integer, primary_key=True, nullable=False)
    actual_filename= Column(String, nullable=False)
    stored_filename= Column(String, nullable=False)
    file_size = Column(BigInteger, nullable=False)
    s3_path = Column(String, nullable=False)
    file_format = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable = False, server_default = text('now()'))