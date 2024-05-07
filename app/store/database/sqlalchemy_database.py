from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, MappedAsDataclass


class BaseModel(AsyncAttrs, MappedAsDataclass, DeclarativeBase):
    pass
