import datetime
from typing import List

import sqlalchemy as sa
from aiogram import Dispatcher
from gino import Gino
from sqlalchemy import Column, DateTime, BigInteger, String, sql, ForeignKey, UniqueConstraint

from data import config

db = Gino()


class BaseModel(db.Model):
    __abstract__ = True

    def __str__(self):
        model = self.__class__.__name__
        table: sa.Table = sa.inspect(self.__class__)
        primary_key_columns: List[sa.Column] = table.primary_key.columns
        values = {
            column.name: getattr(self, self._column_name_map[column.name])
            for column in primary_key_columns
        }
        values_str = " ".join(f"{name}={value!r}" for name, value in values.items())
        return f"<{model} {values_str}>"


class TimeBaseModel(BaseModel):
    __abstract__ = True

    created_at = Column(DateTime(True), server_default=db.func.now())
    updated_at = Column(DateTime(True),
                        default=datetime.datetime.utcnow,
                        onupdate=datetime.datetime.utcnow,
                        server_default=db.func.now())


async def on_startup(dispatcher: Dispatcher):
    print("Установка связи с PostgreSQL")
    await db.set_bind(config.POSTGRES_URL)
    print("Готово")
    print("Создаем таблицу")
    await db.gino.create_all()
    print("Готово")
