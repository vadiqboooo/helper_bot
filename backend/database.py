from sqlalchemy import create_engine, Column, Integer, Text, DateTime, Boolean, BigInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

Base = declarative_base()


class Solution(Base):
    """Модель эталонного решения"""
    __tablename__ = 'solutions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(Integer, nullable=False, index=True)
    solution = Column(Text, nullable=False)
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.now)

    def __repr__(self):
        return f"<Solution(id={self.id}, task_id={self.task_id})>"


class Hint(Base):
    """Модель подсказки пользователя"""
    __tablename__ = 'hints'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, nullable=False, index=True)  # Telegram user ID
    task_id = Column(Integer, nullable=False, index=True)
    hint_text = Column(Text, nullable=False)
    hint_type = Column(Text, nullable=False)  # 'start' или 'analyze'
    was_helpful = Column(Boolean, nullable=True, default=None)  # None = не оценено
    created_at = Column(DateTime, default=datetime.now, index=True)

    def __repr__(self):
        return f"<Hint(id={self.id}, user_id={self.user_id}, task_id={self.task_id})>"


class Homework(Base):
    """Модель домашней работы"""
    __tablename__ = 'homeworks'

    id = Column(Integer, primary_key=True, autoincrement=True)
    kim = Column(Integer, nullable=False, unique=True, index=True)  # ID варианта
    title = Column(Text, nullable=True)  # Название (опционально)
    is_active = Column(Boolean, default=True, nullable=False)  # Доступна ли работа
    created_at = Column(DateTime, default=datetime.now)

    def __repr__(self):
        return f"<Homework(id={self.id}, kim={self.kim}, active={self.is_active})>"


# Создание движка БД
import os
DB_PATH = os.getenv('DB_PATH', '/app/data/homework_bot.db')
engine = create_engine(f'sqlite:///{DB_PATH}', echo=False)

# Создание таблиц
Base.metadata.create_all(engine)

# Создание сессии
SessionLocal = sessionmaker(bind=engine)


def get_db():
    """Получить сессию БД"""
    db = SessionLocal()
    try:
        return db
    finally:
        pass
