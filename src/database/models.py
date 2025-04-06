from sqlalchemy import Integer, String, Date, Column
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class Contact(Base):
    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(200), nullable=False)
    phone = Column(String(50), nullable=False)
    birthday = Column(Date, nullable=False)
