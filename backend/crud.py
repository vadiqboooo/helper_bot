import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import List, Optional
from sqlalchemy.orm import Session
from backend.database import Solution, Hint, Homework, get_db
from datetime import datetime, timedelta


class SolutionCRUD:
    """CRUD операции для эталонных решений"""

    @staticmethod
    def add_solution(task_id: int, solution: str, comment: Optional[str] = None) -> Solution:
        """
        Добавить эталонное решение

        Args:
            task_id: ID задачи
            solution: Текст решения
            comment: Комментарий к решению (необязательно)

        Returns:
            Созданное решение
        """
        db = get_db()
        try:
            new_solution = Solution(
                task_id=task_id,
                solution=solution,
                comment=comment
            )
            db.add(new_solution)
            db.commit()
            db.refresh(new_solution)
            return new_solution
        finally:
            db.close()

    @staticmethod
    def get_solutions_by_task_id(task_id: int) -> List[Solution]:
        """
        Получить все решения для задачи

        Args:
            task_id: ID задачи

        Returns:
            Список решений
        """
        db = get_db()
        try:
            solutions = db.query(Solution).filter(
                Solution.task_id == task_id
            ).all()
            return solutions
        finally:
            db.close()

    @staticmethod
    def get_solution_by_id(solution_id: int) -> Optional[Solution]:
        """
        Получить решение по ID

        Args:
            solution_id: ID решения

        Returns:
            Решение или None
        """
        db = get_db()
        try:
            solution = db.query(Solution).filter(
                Solution.id == solution_id
            ).first()
            return solution
        finally:
            db.close()

    @staticmethod
    def update_solution(solution_id: int, solution: Optional[str] = None,
                       comment: Optional[str] = None) -> Optional[Solution]:
        """
        Обновить решение

        Args:
            solution_id: ID решения
            solution: Новый текст решения
            comment: Новый комментарий

        Returns:
            Обновленное решение или None
        """
        db = get_db()
        try:
            db_solution = db.query(Solution).filter(
                Solution.id == solution_id
            ).first()

            if db_solution:
                if solution is not None:
                    db_solution.solution = solution
                if comment is not None:
                    db_solution.comment = comment

                db.commit()
                db.refresh(db_solution)
                return db_solution
            return None
        finally:
            db.close()

    @staticmethod
    def delete_solution(solution_id: int) -> bool:
        """
        Удалить решение

        Args:
            solution_id: ID решения

        Returns:
            True если удалено, False если не найдено
        """
        db = get_db()
        try:
            db_solution = db.query(Solution).filter(
                Solution.id == solution_id
            ).first()

            if db_solution:
                db.delete(db_solution)
                db.commit()
                return True
            return False
        finally:
            db.close()

    @staticmethod
    def get_all_solutions() -> List[Solution]:
        """
        Получить все решения

        Returns:
            Список всех решений
        """
        db = get_db()
        try:
            solutions = db.query(Solution).all()
            return solutions
        finally:
            db.close()

    @staticmethod
    def count_solutions_by_task(task_id: int) -> int:
        """
        Подсчитать количество решений для задачи

        Args:
            task_id: ID задачи

        Returns:
            Количество решений
        """
        db = get_db()
        try:
            count = db.query(Solution).filter(
                Solution.task_id == task_id
            ).count()
            return count
        finally:
            db.close()


class HintCRUD:
    """CRUD операции для подсказок"""

    @staticmethod
    def add_hint(user_id: int, task_id: int, hint_text: str, hint_type: str) -> Hint:
        """
        Добавить подсказку

        Args:
            user_id: ID пользователя Telegram
            task_id: ID задачи
            hint_text: Текст подсказки
            hint_type: Тип подсказки ('start' или 'analyze')

        Returns:
            Созданная подсказка
        """
        db = get_db()
        try:
            new_hint = Hint(
                user_id=user_id,
                task_id=task_id,
                hint_text=hint_text,
                hint_type=hint_type
            )
            db.add(new_hint)
            db.commit()
            db.refresh(new_hint)
            return new_hint
        finally:
            db.close()

    @staticmethod
    def mark_helpful(hint_id: int, was_helpful: bool) -> Optional[Hint]:
        """
        Отметить, была ли подсказка полезной

        Args:
            hint_id: ID подсказки
            was_helpful: True если помогла, False если нет

        Returns:
            Обновленная подсказка или None
        """
        db = get_db()
        try:
            hint = db.query(Hint).filter(Hint.id == hint_id).first()
            if hint:
                hint.was_helpful = was_helpful
                db.commit()
                db.refresh(hint)
                return hint
            return None
        finally:
            db.close()

    @staticmethod
    def get_user_hints(user_id: int, limit: int = 10) -> List[Hint]:
        """
        Получить подсказки пользователя

        Args:
            user_id: ID пользователя
            limit: Максимальное количество подсказок

        Returns:
            Список подсказок
        """
        db = get_db()
        try:
            hints = db.query(Hint).filter(
                Hint.user_id == user_id
            ).order_by(Hint.created_at.desc()).limit(limit).all()
            return hints
        finally:
            db.close()

    @staticmethod
    def get_task_hints(task_id: int) -> List[Hint]:
        """
        Получить все подсказки для задачи

        Args:
            task_id: ID задачи

        Returns:
            Список подсказок
        """
        db = get_db()
        try:
            hints = db.query(Hint).filter(
                Hint.task_id == task_id
            ).order_by(Hint.created_at.desc()).all()
            return hints
        finally:
            db.close()

    @staticmethod
    def get_hint_stats(days: int = 7) -> dict:
        """
        Получить статистику по подсказкам

        Args:
            days: За сколько дней показывать статистику

        Returns:
            Словарь со статистикой
        """
        db = get_db()
        try:
            since_date = datetime.now() - timedelta(days=days)

            total_hints = db.query(Hint).filter(
                Hint.created_at >= since_date
            ).count()

            helpful_hints = db.query(Hint).filter(
                Hint.created_at >= since_date,
                Hint.was_helpful == True
            ).count()

            not_helpful_hints = db.query(Hint).filter(
                Hint.created_at >= since_date,
                Hint.was_helpful == False
            ).count()

            return {
                'total': total_hints,
                'helpful': helpful_hints,
                'not_helpful': not_helpful_hints,
                'not_rated': total_hints - helpful_hints - not_helpful_hints,
                'days': days
            }
        finally:
            db.close()

    @staticmethod
    def get_latest_hint_for_user(user_id: int) -> Optional[Hint]:
        """
        Получить последнюю подсказку пользователя

        Args:
            user_id: ID пользователя

        Returns:
            Последняя подсказка или None
        """
        db = get_db()
        try:
            hint = db.query(Hint).filter(
                Hint.user_id == user_id
            ).order_by(Hint.created_at.desc()).first()
            return hint
        finally:
            db.close()


class HomeworkCRUD:
    """CRUD операции для домашних работ"""

    @staticmethod
    def add_homework(kim: int, title: Optional[str] = None, is_active: bool = True) -> Homework:
        """
        Добавить домашнюю работу

        Args:
            kim: ID варианта (KIM)
            title: Название работы (опционально)
            is_active: Активна ли работа

        Returns:
            Созданная домашняя работа
        """
        db = get_db()
        try:
            new_homework = Homework(
                kim=kim,
                title=title,
                is_active=is_active
            )
            db.add(new_homework)
            db.commit()
            db.refresh(new_homework)
            return new_homework
        finally:
            db.close()

    @staticmethod
    def get_all_homeworks() -> List[Homework]:
        """
        Получить все домашние работы

        Returns:
            Список всех домашних работ
        """
        db = get_db()
        try:
            homeworks = db.query(Homework).order_by(Homework.created_at.desc()).all()
            return homeworks
        finally:
            db.close()

    @staticmethod
    def get_active_homeworks() -> List[Homework]:
        """
        Получить активные домашние работы

        Returns:
            Список активных домашних работ
        """
        db = get_db()
        try:
            homeworks = db.query(Homework).filter(
                Homework.is_active == True
            ).order_by(Homework.created_at.desc()).all()
            return homeworks
        finally:
            db.close()

    @staticmethod
    def get_homework_by_kim(kim: int) -> Optional[Homework]:
        """
        Получить домашнюю работу по KIM

        Args:
            kim: ID варианта

        Returns:
            Домашняя работа или None
        """
        db = get_db()
        try:
            homework = db.query(Homework).filter(Homework.kim == kim).first()
            return homework
        finally:
            db.close()

    @staticmethod
    def toggle_homework_status(kim: int) -> Optional[Homework]:
        """
        Переключить статус домашней работы (активна/неактивна)

        Args:
            kim: ID варианта

        Returns:
            Обновленная домашняя работа или None
        """
        db = get_db()
        try:
            homework = db.query(Homework).filter(Homework.kim == kim).first()
            if homework:
                homework.is_active = not homework.is_active
                db.commit()
                db.refresh(homework)
                return homework
            return None
        finally:
            db.close()

    @staticmethod
    def delete_homework(kim: int) -> bool:
        """
        Удалить домашнюю работу

        Args:
            kim: ID варианта

        Returns:
            True если удалено, False если не найдено
        """
        db = get_db()
        try:
            homework = db.query(Homework).filter(Homework.kim == kim).first()
            if homework:
                db.delete(homework)
                db.commit()
                return True
            return False
        finally:
            db.close()

    @staticmethod
    def update_homework_title(kim: int, title: str) -> Optional[Homework]:
        """
        Обновить название домашней работы

        Args:
            kim: ID варианта
            title: Новое название

        Returns:
            Обновленная домашняя работа или None
        """
        db = get_db()
        try:
            homework = db.query(Homework).filter(Homework.kim == kim).first()
            if homework:
                homework.title = title
                db.commit()
                db.refresh(homework)
                return homework
            return None
        finally:
            db.close()
