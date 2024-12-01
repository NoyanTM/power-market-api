from typing import Annotated

from sqlalchemy.orm import Session
from fastapi import Depends

from src.database import get_session

DBSessionDep = Annotated[Session, Depends(get_session)]
