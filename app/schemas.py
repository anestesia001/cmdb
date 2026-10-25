from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class EnvironmentBase(BaseModel):
    name: str = Field(min_length=1, max_length=64)
    description: str | None = None


class EnvironmentCreate(EnvironmentBase):
    pass


class EnvironmentOut(EnvironmentBase):
    model_config = ConfigDict(from_attributes=True)

    id: int


class ServerBase(BaseModel):
    hostname: str = Field(min_length=1, max_length=255)
    ip_address: str = Field(min_length=7, max_length=45)
    os: str | None = None
    cpu_cores: int | None = Field(default=None, ge=1)
    memory_mb: int | None = Field(default=None, ge=1)
    disk_gb: int | None = Field(default=None, ge=1)
    status: str = "active"
    is_virtual: bool = True
    notes: str | None = None


class ServerCreate(ServerBase):
    pass


class ServerUpdate(BaseModel):
    ip_address: str | None = None
    os: str | None = None
    cpu_cores: int | None = None
    memory_mb: int | None = None
    disk_gb: int | None = None
    status: str | None = None
    is_virtual: bool | None = None
    notes: str | None = None


class ServerOut(ServerBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class ServiceBase(BaseModel):
    name: str = Field(min_length=1, max_length=128)
    environment_id: int
    server_id: int | None = None
    port: int | None = Field(default=None, ge=1, le=65535)
    version: str | None = None
    status: str = "active"
    description: str | None = None


class ServiceCreate(ServiceBase):
    pass


class ServiceUpdate(BaseModel):
    server_id: int | None = None
    port: int | None = None
    version: str | None = None
    status: str | None = None
    description: str | None = None


class ServiceOut(ServiceBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
