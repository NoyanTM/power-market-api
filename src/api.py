import json
import io
from typing import Annotated
from uuid import uuid4, UUID

from fastapi import (
    FastAPI,
    UploadFile,
    Request,
    BackgroundTasks,
    HTTPException,
    status,
    Query,
)
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select, insert
import pandas as pd

from src.constants import BASE_DIR, AvailableModel, FileMimeType, FileType
from src.schemas import DataFormat, DataRead, AnalysisFilterParams, PredictionConfig
from src.dependencies import DBSessionDep
from src.database import Data, Analysis, Prediction
from src.analysis import create_analysis
from src.model import create_prediction


app = FastAPI()
app.mount("/static", StaticFiles(directory=BASE_DIR / "static", html=True), name="static")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get(
    "/health",
    status_code=status.HTTP_200_OK,
    description="Check API status"
)
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.get(
    "/models",
    status_code=status.HTTP_200_OK,
    description="Получить список всех доступных моделей"
)
def get_list_of_models() -> dict[str, list]:
    return {
        "models": [
            AvailableModel.SARIMA,
            AvailableModel.FB_PROPHET,
            AvailableModel.XGBOOST
        ]
    }


@app.post(
    "/data/upload",
    description="""
- Загрузка файла формата .CSV, .JSON, .EXCEL с данными для анализа
- Либо загрузка данных вручную через body в формате JSON
- Обязательный формат данных указан в схеме FileFormat
    """
)
def upload_data(
    session: DBSessionDep,
    file_object: UploadFile, # | None = None,
    # file_body: DataFormat | None = None,
) -> DataRead:
    # if not (bool(file_object) or bool(file_body)):
    #     raise HTTPException(
    #         status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
    #         detail="Необходимо загрузить хотя бы один из параметров: file_object или file_body"
    #     )
    
    # if file_body and file_object: # TODO: refactor it, so it will be possible to upload both file and body
    #     raise HTTPException(
    #         status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
    #         detail="Нельзя одновременно загружать file_object или file_body - только одно из них за раз"
    #     )
    
    if file_object:
        if file_object.content_type not in [FileMimeType.CSV, FileMimeType.JSON, FileMimeType.EXCEL]:
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail="Допустимые форматы файла: csv, json, excel"
            )
        if not file_object.filename.endswith((FileType.CSV, FileType.JSON, FileType.EXCEL)):
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail="Допустимые расширения файла: .csv, .json, .xlsx. Расширение файла должно быть указано в названии файла"
            )
        
        if file_object.size is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Нельзя загружать пустой файл"
            )
        
        original_file_name = file_object.filename
        new_file_name = str(uuid4())
        extension = file_object.filename.split(".")[-1]
        file_uri = f"static/data/{new_file_name}.{extension}"
        file_location = BASE_DIR / file_uri
        file_size = file_object.size
        with open(file_location, "wb+") as file_data:
            file_data.write(file_object.file.read())
        
        stmt = (
            insert(Data)
            .values(
                id=new_file_name,
                uri=file_uri,
                extension=extension,
                original_name=original_file_name,
                size=file_size,
            )
            .returning(Data)
        )
        insert_data = session.execute(stmt)
        data_obj = insert_data.scalar_one_or_none()
        session.commit()
        
        # TODO: тут валидация падает с ошибкой, хотя никакой на этой причины нету и возвращается причем database.object с индексом
        # data_schema = DataRead.model_validate(data_orm)
        # поэтому пока такой костыль поставил
        data_schema = DataRead(
            data_id=data_obj.id,
            data_type=extension,
            uri_path=data_obj.uri,
            original_name=data_obj.original_name,
            size=data_obj.size,
            created_at=data_obj.created_at,
            updated_at=data_obj.updated_at,
        )
    
    # if file_body:
    #     pass

    return data_schema


@app.get(
    "/data/{data_id}",
    status_code=status.HTTP_200_OK,
    description="Скачать данные по идентификатору"
)
def get_data(
    session: DBSessionDep,
    data_id: UUID,
) -> FileResponse:
    stmt = select(Data).where(Data.id == str(data_id))
    select_data = session.execute(stmt)
    data_obj = select_data.scalar_one_or_none()
    if not data_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Данные по идентификатору не найдены"
        )
    # TODO: тут валидация объекта data_obj в pydantic из sqlalchemy
    return FileResponse(path = BASE_DIR / data_obj.uri) # TODO: filename, media_type, и т.д. на ответе


@app.get(
    "/data/{data_id}/analysis",
    description="Запустить анализ данных по идентификатору"
)
def get_analysis(
    data_id: UUID,
    session: DBSessionDep,
) -> HTMLResponse:
    stmt = select(Data).where(Data.id == str(data_id))
    select_data = session.execute(stmt)
    data_obj = select_data.scalar_one_or_none()
    if not data_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Данные по идентификатору не найдены"
        )
    
    with open(BASE_DIR / data_obj.uri, "rb") as file:
        file_io_data = io.BytesIO(file.read())
    
    if data_obj.extension == FileType.CSV:
        df = pd.read_csv(file_io_data, parse_dates=["date"]) # parse_dates=['date'] index_col='date', 
    elif data_obj.extension == FileType.JSON:
        df = pd.read_json(file_io_data, parse_dates=["date"]) # parse_dates=['date'] index_col='date',
    elif data_obj.extension == FileType.EXCEL:
        df = pd.read_excel(file_io_data, parse_dates=["date"]) # parse_dates=['date'] index_col='date', 
    
    html_content = create_analysis(df=df)
    
    return HTMLResponse(content=html_content)


@app.post(
    "/data/{data_id}/predictions/run",
    status_code=status.HTTP_201_CREATED,
    description="Запустить прогнозирование данных на одной из доступной модели"
)
def run_prediction(
    data_id: UUID,
    prediction_config: PredictionConfig,
    session: DBSessionDep,
) -> HTMLResponse:
    stmt = select(Data).where(Data.id == str(data_id))
    select_data = session.execute(stmt)
    data_obj = select_data.scalar_one_or_none()
    if not data_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Данные по идентификатору не найдены"
        )
    
    with open(BASE_DIR / data_obj.uri, "rb") as file:
        file_io_data = io.BytesIO(file.read())
    
    if data_obj.extension == FileType.CSV:
        df = pd.read_csv(file_io_data, parse_dates=["date"]) # parse_dates=['date'] index_col='date', 
    elif data_obj.extension == FileType.JSON:
        df = pd.read_json(file_io_data, parse_dates=["date"]) # parse_dates=['date'] index_col='date',
    elif data_obj.extension == FileType.EXCEL:
        df = pd.read_excel(file_io_data, parse_dates=["date"]) # parse_dates=['date'] index_col='date', 
    
    html_content = create_prediction(
        df=df,
        model_type=prediction_config.model_type,
        forecast_horizon=prediction_config.forecast_horizon,
    )
    
    return HTMLResponse(content=html_content)


# @app.get(
#     "/predictions/{prediction_id}",
# )
# def get_prediction(prediction_id: UUID):
#     pass
