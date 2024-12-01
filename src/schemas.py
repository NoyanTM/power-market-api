from datetime import datetime, date
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict

from src.constants import AvailableModel, FileType


class DataFormat(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    date: datetime # datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    object_name: str = Field(description="Названия объекта, к примеру Zadarya Solar PV Park")
    plan: float = Field(description="Планируемая выроботка")
    fact: float = Field(description="Фактическая выроботка")
    unit: str = Field(description="Единицы измерения, к примеру MWh")
    cloudiness: float = Field(description="Облачность")
    temperature: float = Field(description="Температура в градусах °C")
    wind_speed: float = Field(description="Скорость ветра")


class DataRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    data_id: str
    uri_path: str
    data_type: FileType
    original_name: str
    size: int
    created_at: datetime
    updated_at: datetime
    

class AnalysisFilterParams(BaseModel):
    start_date: datetime | None = None # mindate=datetime(2023, 1, 1),
    end_date: datetime | None = None # maxdate=datetime(2024, 7, 1)
    object_name: str | None = None
    

class PredictionConfig(BaseModel):
    # data_id: UUID
    model_type: AvailableModel
    forecast_horizon: int = Field(default=48, ge=24, le=128, description="Горизонт прогнозирования в часах")


# class PredictionRead:
