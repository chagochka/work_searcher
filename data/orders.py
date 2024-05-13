import datetime

import sqlalchemy
from sqlalchemy import orm
from flask_login import UserMixin

from .db_session import SqlAlchemyBase


class Order(SqlAlchemyBase, UserMixin):
    """Работа с информацией об отчётах"""

    __tablename__ = 'orders'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    hirer_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'))
    title = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    price = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    descr = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    status = sqlalchemy.Column(sqlalchemy.String, nullable=False, default='not_done')
    date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)

    users = orm.relationship('User', back_populates="orders")
    replies = orm.relationship('Reply', back_populates="orders")

    def to_dict(self):
        """Преобразование объекта Order в словарь"""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns if not c.name.startswith('_')}
