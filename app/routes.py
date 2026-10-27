from flask import Blueprint, flash, jsonify, redirect, render_template, request, url_for
from werkzeug.exceptions import NotFound

from .models import TITLE_MAX_LENGTH
from .services import todo_service
from .services.todo_service import TodoNotFound, ValidationError

main = Blueprint("main", __name__)


@main.errorhandler(TodoNotFound)
def todo_not_found(_error):
    return NotFound()


@main.app_context_processor
def inject_limits():
    return {"title_max_length": TITLE_MAX_LENGTH}


def _current_filter():
    return todo_service.normalize_filter(request.args.get("filter"))


def _back_to_list():
    return redirect(url_for("main.index", filter=_current_filter()))


@main.get("/")
def index():
    current = _current_filter()
    stats = todo_service.get_stats()
    return render_template("index.html", title="My Tasks",
                           todos=todo_service.list_todos(current), current=current,
                           remaining=stats.remaining, completed=stats.completed)


@main.post("/todos")
def create():
    try:
        todo_service.create_todo(request.form.get("title"))
    except ValidationError as error:
        flash(str(error), "error")
    else:
        flash("Task added.", "success")
    return _back_to_list()


@main.post("/todos/<int:todo_id>/toggle")
def toggle(todo_id):
    todo_service.toggle_todo(todo_id)
    return _back_to_list()


@main.route("/todos/<int:todo_id>/edit", methods=["GET", "POST"])
def edit(todo_id):
    todo = todo_service.get_todo(todo_id)
    if request.method == "POST":
        try:
            todo_service.update_todo(todo_id, request.form.get("title"))
        except ValidationError as error:
            flash(str(error), "error")
            return render_template("edit.html", title="Edit Task", todo=todo), 400
        flash("Task updated.", "success")
        return redirect(url_for("main.index"))
    return render_template("edit.html", title="Edit Task", todo=todo)


@main.post("/todos/<int:todo_id>/delete")
def delete(todo_id):
    todo_service.delete_todo(todo_id)
    flash("Task deleted.", "success")
    return _back_to_list()


@main.post("/todos/clear-done")
def clear_done():
    count = todo_service.clear_completed()
    flash(f"Cleared {count} completed task{'' if count == 1 else 's'}.", "success")
    return _back_to_list()


@main.get("/about")
def about():
    return render_template("about.html", title="About")


@main.get("/api/health")
def health():
    return jsonify(status="ok")
