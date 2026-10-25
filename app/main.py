from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from . import crud, models, schemas
from .database import Base, engine, get_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="CMDB API",
    description="Простая CMDB: серверы, сервисы и окружения",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/environments", response_model=list[schemas.EnvironmentOut])
def get_environments(db: Session = Depends(get_db)):
    return crud.list_environments(db)


@app.post(
    "/environments",
    response_model=schemas.EnvironmentOut,
    status_code=status.HTTP_201_CREATED,
)
def post_environment(
    data: schemas.EnvironmentCreate,
    db: Session = Depends(get_db),
):
    try:
        return crud.create_environment(db, data)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Environment already exists")


@app.get("/environments/{environment_id}", response_model=schemas.EnvironmentOut)
def get_environment(environment_id: int, db: Session = Depends(get_db)):
    obj = crud.get_environment(db, environment_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Environment not found")
    return obj


@app.delete("/environments/{environment_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_environment(environment_id: int, db: Session = Depends(get_db)):
    if not crud.delete_environment(db, environment_id):
        raise HTTPException(status_code=404, detail="Environment not found")


@app.get("/servers", response_model=list[schemas.ServerOut])
def get_servers(
    hostname: str | None = Query(default=None),
    status_filter: str | None = Query(default=None, alias="status"),
    db: Session = Depends(get_db),
):
    return crud.list_servers(db, hostname=hostname, status=status_filter)


@app.post(
    "/servers",
    response_model=schemas.ServerOut,
    status_code=status.HTTP_201_CREATED,
)
def post_server(data: schemas.ServerCreate, db: Session = Depends(get_db)):
    try:
        return crud.create_server(db, data)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Server hostname already exists")


@app.get("/servers/{server_id}", response_model=schemas.ServerOut)
def get_server(server_id: int, db: Session = Depends(get_db)):
    obj = crud.get_server(db, server_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Server not found")
    return obj


@app.patch("/servers/{server_id}", response_model=schemas.ServerOut)
def patch_server(
    server_id: int,
    data: schemas.ServerUpdate,
    db: Session = Depends(get_db),
):
    obj = crud.get_server(db, server_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Server not found")

    try:
        return crud.update_server(db, obj, data)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Update conflicts with existing record")


@app.delete("/servers/{server_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_server(server_id: int, db: Session = Depends(get_db)):
    if not crud.delete_server(db, server_id):
        raise HTTPException(status_code=404, detail="Server not found")


@app.get("/services", response_model=list[schemas.ServiceOut])
def get_services(
    environment_id: int | None = None,
    server_id: int | None = None,
    status_filter: str | None = Query(default=None, alias="status"),
    db: Session = Depends(get_db),
):
    return crud.list_services(
        db,
        environment_id=environment_id,
        server_id=server_id,
        status=status_filter,
    )


@app.post(
    "/services",
    response_model=schemas.ServiceOut,
    status_code=status.HTTP_201_CREATED,
)
def post_service(data: schemas.ServiceCreate, db: Session = Depends(get_db)):
    try:
        return crud.create_service(db, data)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Service already exists")


@app.get("/services/{service_id}", response_model=schemas.ServiceOut)
def get_service(service_id: int, db: Session = Depends(get_db)):
    obj = crud.get_service(db, service_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Service not found")
    return obj


@app.patch("/services/{service_id}", response_model=schemas.ServiceOut)
def patch_service(
    service_id: int,
    data: schemas.ServiceUpdate,
    db: Session = Depends(get_db),
):
    obj = crud.get_service(db, service_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Service not found")

    try:
        return crud.update_service(db, obj, data)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.delete("/services/{service_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_service(service_id: int, db: Session = Depends(get_db)):
    if not crud.delete_service(db, service_id):
        raise HTTPException(status_code=404, detail="Service not found")
