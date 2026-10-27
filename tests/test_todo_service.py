import pytest

from app.services import todo_service
from app.services.todo_service import TodoNotFound, ValidationError


@pytest.fixture
def ctx(app):
    with app.app_context():
        yield


def test_create_strips_title(ctx):
    todo = todo_service.create_todo("  Buy milk  ")
    assert todo.title == "Buy milk"
    assert todo.done is False


@pytest.mark.parametrize("title", [None, "", "   ", "x" * 201])
def test_create_rejects_invalid_title(ctx, title):
    with pytest.raises(ValidationError):
        todo_service.create_todo(title)
    assert todo_service.list_todos() == []


def test_list_filters_and_stats(ctx):
    finished = todo_service.create_todo("Finished")
    todo_service.create_todo("Pending")
    todo_service.toggle_todo(finished.id)

    assert [t.title for t in todo_service.list_todos("active")] == ["Pending"]
    assert [t.title for t in todo_service.list_todos("done")] == ["Finished"]
    assert [t.title for t in todo_service.list_todos("all")] == ["Pending", "Finished"]
    assert todo_service.get_stats() == (1, 1)


def test_update_and_delete(ctx):
    todo = todo_service.create_todo("Old")
    assert todo_service.update_todo(todo.id, "New").title == "New"
    todo_service.delete_todo(todo.id)
    assert todo_service.list_todos() == []


def test_clear_completed_returns_count(ctx):
    for title in ("a", "b", "c"):
        todo_service.toggle_todo(todo_service.create_todo(title).id)
    todo_service.create_todo("keep")
    assert todo_service.clear_completed() == 3
    assert [t.title for t in todo_service.list_todos()] == ["keep"]


def test_missing_todo_raises(ctx):
    with pytest.raises(TodoNotFound):
        todo_service.get_todo(999)
    with pytest.raises(TodoNotFound):
        todo_service.toggle_todo(999)


@pytest.mark.parametrize("value, expected", [("done", "done"), ("bogus", "all"), (None, "all")])
def test_normalize_filter(value, expected):
    assert todo_service.normalize_filter(value) == expected
