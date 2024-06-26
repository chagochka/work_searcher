"""Сессия для работы с базой данных"""

import sqlalchemy as sa
import sqlalchemy.orm as orm
from sqlalchemy.orm import Session, DeclarativeBase


class SqlAlchemyBase(DeclarativeBase): pass


__factory = None


def global_init(adress):
	"""Инициализация базы данных"""

	global __factory

	if __factory:
		return

	if not adress:
		raise Exception('Необходимо указать адрес базы данных.')

	conn_str = f'postgresql://{adress}'
	print(f'Подключение к базе данных по адресу {conn_str}')

	engine = sa.create_engine(conn_str, echo=False)
	__factory = orm.sessionmaker(bind=engine)

	# noinspection PyUnresolvedReferences
	from . import __all_models

	SqlAlchemyBase.metadata.create_all(engine)


def create_session() -> Session:
	"""Создание сессии подключения к базе данных"""
	global __factory
	return __factory()
