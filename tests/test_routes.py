from app import db
from app.models import Todo


def _todos(app):
    with app.app_context():
        return [(t.title, t.done) for t in db.session.scalars(db.select(Todo).order_by(Todo.id))]


def test_index_empty(client):
    res = client.get("/")
    assert res.status_code == 200
    assert "No tasks here" in res.get_data(as_text=True)


def test_create(app, client):
    res = client.post("/todos", data={"title": "  Buy milk  "}, follow_redirects=True)
    assert res.status_code == 200
    assert "Buy milk" in res.get_data(as_text=True)
    assert _todos(app) == [("Buy milk", False)]


def test_create_rejects_empty_and_long(app, client):
    client.post("/todos", data={"title": "   "})
    client.post("/todos", data={"title": "x" * 201})
    assert _todos(app) == []


def test_toggle(app, client):
    client.post("/todos", data={"title": "Task"})
    client.post("/todos/1/toggle")
    assert _todos(app) == [("Task", True)]
    client.post("/todos/1/toggle")
    assert _todos(app) == [("Task", False)]


def test_edit(app, client):
    client.post("/todos", data={"title": "Old"})
    assert client.get("/todos/1/edit").status_code == 200
    client.post("/todos/1/edit", data={"title": "New"})
    assert _todos(app) == [("New", False)]
    assert client.post("/todos/1/edit", data={"title": ""}).status_code == 400
    assert _todos(app) == [("New", False)]


def test_delete(app, client):
    client.post("/todos", data={"title": "Delete me"})
    client.post("/todos/1/delete")
    assert _todos(app) == []


def test_filters_and_clear_done(app, client):
    client.post("/todos", data={"title": "Finished"})
    client.post("/todos", data={"title": "Pending"})
    client.post("/todos/1/toggle")

    active = client.get("/?filter=active").get_data(as_text=True)
    assert "Pending" in active and "Finished" not in active
    done = client.get("/?filter=done").get_data(as_text=True)
    assert "Finished" in done and "Pending" not in done

    client.post("/todos/clear-done")
    assert _todos(app) == [("Pending", False)]


def test_missing_todo_404(client):
    assert client.post("/todos/999/toggle").status_code == 404
    assert client.get("/todos/999/edit").status_code == 404


def test_about_and_health(client):
    assert client.get("/about").status_code == 200
    assert client.get("/api/health").json == {"status": "ok"}
