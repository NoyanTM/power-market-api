from uuid import uuid4, UUID
from datetime import datetime

from sqlalchemy import create_engine, ForeignKey, String, JSON, DateTime, Integer
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Mapped, mapped_column, relationship
from fastapi import HTTPException, status

from src.constants import SQLITE_URL

engine = create_engine(url=SQLITE_URL)

Session = sessionmaker(engine)


def get_session():
    with Session() as session:
        try:
            yield session
        except SQLAlchemyError as e:
            session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error: {e}"
            )
        finally:
            session.close()


class Base(DeclarativeBase):
    pass


class TimeBasedMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), onupdate=datetime.now, default=datetime.now)


class Data(TimeBasedMixin, Base):
    __tablename__ = "data"
    
    id: Mapped[UUID] = mapped_column(String, primary_key=True, default=uuid4)
    uri: Mapped[str] = mapped_column(String)
    extension: Mapped[str] = mapped_column(String)
    original_name: Mapped[str] = mapped_column(String)
    size: Mapped[int] = mapped_column(Integer)

    analyses: Mapped["Analysis"] = relationship(back_populates="data")
    predictions: Mapped["Prediction"] = relationship(back_populates="data")


class Analysis(TimeBasedMixin, Base):
    __tablename__ = "analysis"
    
    id: Mapped[UUID] = mapped_column(String, primary_key=True, default=uuid4)
    results: Mapped[JSON] = mapped_column(JSON)
    
    data_id: Mapped[UUID] = mapped_column(String, ForeignKey("data.id"))
    data: Mapped["Data"] = relationship(back_populates="analyses")


class Prediction(TimeBasedMixin, Base):
    __tablename__ = "prediction"
    
    id: Mapped[UUID] = mapped_column(String, primary_key=True, default=uuid4)
    results: Mapped[JSON] = mapped_column(JSON)
    
    data_id: Mapped[UUID] = mapped_column(String, ForeignKey("data.id"))
    data: Mapped["Data"] = relationship(back_populates="predictions")
