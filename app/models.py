from datetime import datetime, timezone

from . import db

TITLE_MAX_LENGTH = 200


class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(TITLE_MAX_LENGTH), nullable=False)
    done = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, nullable=False,
                           default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"<Todo {self.id} {self.title!r}>"
