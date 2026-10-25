from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from . import models, schemas


def list_environments(db: Session):
    return db.scalars(select(models.Environment).order_by(models.Environment.name)).all()


def create_environment(db: Session, data: schemas.EnvironmentCreate):
    obj = models.Environment(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def get_environment(db: Session, environment_id: int):
    return db.get(models.Environment, environment_id)


def delete_environment(db: Session, environment_id: int) -> bool:
    obj = db.get(models.Environment, environment_id)
    if not obj:
        return False
    db.delete(obj)
    db.commit()
    return True


def list_servers(db: Session, hostname: str | None = None, status: str | None = None):
    stmt = select(models.Server).order_by(models.Server.hostname)

    if hostname:
        stmt = stmt.where(models.Server.hostname.ilike(f"%{hostname}%"))
    if status:
        stmt = stmt.where(models.Server.status == status)

    return db.scalars(stmt).all()


def get_server(db: Session, server_id: int):
    return db.get(models.Server, server_id)


def create_server(db: Session, data: schemas.ServerCreate):
    obj = models.Server(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def update_server(db: Session, server: models.Server, data: schemas.ServerUpdate):
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(server, field, value)

    db.commit()
    db.refresh(server)
    return server


def delete_server(db: Session, server_id: int) -> bool:
    obj = db.get(models.Server, server_id)
    if not obj:
        return False
    db.delete(obj)
    db.commit()
    return True


def list_services(
    db: Session,
    environment_id: int | None = None,
    server_id: int | None = None,
    status: str | None = None,
):
    stmt = select(models.Service).order_by(models.Service.name)

    if environment_id:
        stmt = stmt.where(models.Service.environment_id == environment_id)
    if server_id:
        stmt = stmt.where(models.Service.server_id == server_id)
    if status:
        stmt = stmt.where(models.Service.status == status)

    return db.scalars(stmt).all()


def get_service(db: Session, service_id: int):
    return db.get(models.Service, service_id)


def create_service(db: Session, data: schemas.ServiceCreate):
    if not db.get(models.Environment, data.environment_id):
        raise ValueError("environment not found")

    if data.server_id and not db.get(models.Server, data.server_id):
        raise ValueError("server not found")

    obj = models.Service(**data.model_dump())
    db.add(obj)

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise ValueError("service already exists in this environment") from exc

    db.refresh(obj)
    return obj


def update_service(db: Session, service: models.Service, data: schemas.ServiceUpdate):
    values = data.model_dump(exclude_unset=True)

    if "server_id" in values and values["server_id"] is not None:
        if not db.get(models.Server, values["server_id"]):
            raise ValueError("server not found")

    for field, value in values.items():
        setattr(service, field, value)

    db.commit()
    db.refresh(service)
    return service


def delete_service(db: Session, service_id: int) -> bool:
    obj = db.get(models.Service, service_id)
    if not obj:
        return False
    db.delete(obj)
    db.commit()
    return True
