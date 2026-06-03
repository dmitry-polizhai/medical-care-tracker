from fastapi import FastAPI, HTTPException
from sqlalchemy.orm import Session

from database import SessionLocal, engine
from models import Base, VisitDB

from pydantic import BaseModel, Field, ConfigDict
from datetime import date

Base.metadata.create_all(bind=engine)

app = FastAPI()

class VisitCreate(BaseModel):
    visit_date: date = Field(
        ...,
        example="2026-05-27",
        description="Дата посещения врача"
    )
    
    doctor: str = Field(
        ...,
        min_length=2,
        max_length=100,
        example="Кардиолог",
        description="Специализация врача"
    )

    clinic: str = Field(
        ...,
        min_length=2,
        max_length=100,
        example="Евромед",
        description="Название клиники"
    )

    reason: str = Field(
        example="Боль в груди",
        description="Причина обращения"
    )

    treatment: str = Field(
        example="Таблетки, упражения",
        description="Назначенное лечение"
    )

    next_visit: str | None = Field(
        default=None,
        max_length=1000,
        example="2026-06-15",
        description="Дата следующего посещения специалиста"
    )

class VisitUpdate(BaseModel):
    visit_date: date | None = None
    doctor: str | None = None
    clinic: str | None = None
    reason: str | None = None
    treatment: str | None = None
    next_visit: str | None = None

class VisitResponse(BaseModel):
    id: int
    visit_date: date
    doctor: str
    clinic: str
    reason: str
    treatment: str
    next_visit: str | None = None

    class Config:
        from_attributes = True

class ErrorResponse(BaseModel):
    detail: str

@app.get("/")
def root():
    return {"message": "Medical Care Tracker API"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post(
        "/visits",
        response_model=VisitResponse,
        tags=["Visits"],
        summary="Создание медицинского визита",
        description="Создает новую запись о посещении врача",
        response_description="Создание новой записи о визите",
        status_code=201
)
def create_visit(visit: VisitCreate):
    db: Session = SessionLocal()

    db_visit = VisitDB(
        visit_date=visit.visit_date,
        doctor=visit.doctor,
        clinic=visit.clinic,
        reason=visit.reason,
        treatment=visit.treatment,
        next_visit=visit.next_visit,
    )

    db.add(db_visit)
    db.commit()
    db.refresh(db_visit)

    return db_visit

@app.get(
        "/visits",
        response_model=list[VisitResponse],
        tags=["Visits"],
        summary="Получения всего списка записей",
        description="Получения списка всех посещений к врачам",
        response_description="Результат запроса")
def get_visits():
    db: Session = SessionLocal()

    visits = db.query(VisitDB).all()

    return visits

@app.get(
    "/visits/{visit_id}",
    response_model=VisitResponse,
    responses={
        404: {"model": ErrorResponse}
    },
    tags=["Visits"],
    summary="Получение конкретного визита",
    description="Получение информации о посещении врача по ID",
    response_description="Информация о визите"
)
def get_visit(visit_id: int):
    db: Session = SessionLocal()

    try:
        visit = db.query(VisitDB).filter(VisitDB.id == visit_id).first()

        if not visit:
            raise HTTPException(
                status_code=404,
                detail=f"Визит с ID {visit_id} не найден"
            )

        return visit
    
    finally:
        db.close()

@app.patch(
    "/visits/{visit_id}",
    response_model=VisitResponse,
    responses={
        404: {"model": ErrorResponse}
    },
    tags=["Visits"],
    summary="Обновление медицинского визита",
    description="Частичное обновление информации о визите",
    response_description="Обновленный визит"
)
def update_visit(visit_id: int, updated_data: VisitUpdate):
    db: Session = SessionLocal()

    try:
        visit = db.query(VisitDB).filter(VisitDB.id == visit_id).first()

        if not visit:
            raise HTTPException(
                status_code=404,
                detail=f"Визит с ID {visit_id} не найден"
            )

        update_data = updated_data.model_dump(exclude_unset=True)

        for key, value in update_data.items():
            setattr(visit, key, value)

        db.commit()
        db.refresh(visit)

        return visit

    finally:
        db.close()

@app.delete(
    "/visits/{visit_id}",
    status_code=204,
    responses={
        404: {"model": ErrorResponse}
    },
    tags=["Visits"],
    summary="Удаление медицинского визита",
    description="Удаляет запись о посещении врача по ID",
    response_description="Результат удаления"
)
def delete_visit(visit_id: int):
    db: Session = SessionLocal()

    visit = db.query(VisitDB).filter(VisitDB.id == visit_id).first()

    if not visit:
        raise HTTPException(
            status_code=404,
            detail=f"Визит с ID {visit_id} не найден"
    )

    db.delete(visit)
    db.commit()

    return {
        "message": f"Визит с ID {visit_id} успешно удален"
    }