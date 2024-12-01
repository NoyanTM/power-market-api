from enum import Enum
from pathlib import Path


class AvailableModel(str, Enum):
    SARIMA = "SARIMA"
    FB_PROPHET = "FB_PROPHET"
    XGBOOST = "XGBOOST"


class FileType(str, Enum):
    CSV = "csv"
    JSON = "json"
    EXCEL = "excel"


class FileMimeType(str, Enum):
    CSV = "text/csv"
    JSON = "application/json"
    EXCEL = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


BASE_DIR = Path(__file__).resolve().parent.parent

SQLITE_URL = f"sqlite:///{BASE_DIR}/database.db"
