from typing import NamedTuple

from sqlalchemy import func

from .. import db
from ..models import TITLE_MAX_LENGTH, Todo

FILTERS = ("all", "active", "done")


class ValidationError(ValueError):
    """User input breaks a business rule; the message is safe to show."""


class TodoNotFound(LookupError):
    """No todo exists with the requested id."""


class TodoStats(NamedTuple):
    remaining: int
    completed: int


def normalize_filter(value):
    return value if value in FILTERS else "all"


def list_todos(status="all"):
    query = db.select(Todo)
    if status == "active":
        query = query.where(Todo.done.is_(False))
    elif status == "done":
        query = query.where(Todo.done.is_(True))
    return db.session.scalars(query.order_by(Todo.done, Todo.created_at.desc())).all()


def get_stats():
    counts = dict(db.session.execute(db.select(Todo.done, func.count()).group_by(Todo.done)).all())
    return TodoStats(remaining=counts.get(False, 0), completed=counts.get(True, 0))


def get_todo(todo_id):
    todo = db.session.get(Todo, todo_id)
    if todo is None:
        raise TodoNotFound(todo_id)
    return todo


def create_todo(title):
    todo = Todo(title=_clean_title(title))
    db.session.add(todo)
    db.session.commit()
    return todo


def update_todo(todo_id, title):
    todo = get_todo(todo_id)
    todo.title = _clean_title(title)
    db.session.commit()
    return todo


def toggle_todo(todo_id):
    todo = get_todo(todo_id)
    todo.done = not todo.done
    db.session.commit()
    return todo


def delete_todo(todo_id):
    db.session.delete(get_todo(todo_id))
    db.session.commit()


def clear_completed():
    """Delete every finished todo and return how many were removed."""
    result = db.session.execute(db.delete(Todo).where(Todo.done.is_(True)))
    db.session.commit()
    return result.rowcount


def _clean_title(raw):
    title = (raw or "").strip()
    if not title:
        raise ValidationError("Please enter a task title.")
    if len(title) > TITLE_MAX_LENGTH:
        raise ValidationError(f"Title must be at most {TITLE_MAX_LENGTH} characters.")
    return title
