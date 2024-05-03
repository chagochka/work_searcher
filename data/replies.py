"""Модель для работы с SQL-таблицей reports"""

import datetime

import sqlalchemy
from sqlalchemy import orm
from flask_login import UserMixin

from .db_session import SqlAlchemyBase


class Reply(SqlAlchemyBase, UserMixin):
    """Работа с информацией о пользователях"""

    __tablename__ = 'replies'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    worker_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'))
    order_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('orders.id'))
    title = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    status = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    descr = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)

    users = orm.relationship('User', back_populates="replies")
    orders = orm.relationship('Order', back_populates="replies")

    def to_dict(self):
        """Преобразование объекта Reply в словарь"""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns if not c.name.startswith('_')}
