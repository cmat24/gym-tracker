from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Session(db.Model):
    """One gym visit — has many SetEntries."""
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)

    # "One session has many set entries."
    # backref='session' means each SetEntry automatically gets a
    # `.session` attribute pointing back to its parent Session —
    # similar to the @ManyToOne link in the Java version.
    # cascade="all, delete-orphan" means: deleting a Session deletes
    # its SetEntries too.
    set_entries = db.relationship(
        "SetEntry", backref="session", cascade="all, delete-orphan"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "date": self.date.isoformat(),
            "set_entries": [s.to_dict() for s in self.set_entries],
        }


class SetEntry(db.Model):
    """One individual set within a session (e.g. Bench Press, set 1)."""
    id = db.Column(db.Integer, primary_key=True)
    exercise_name = db.Column(db.String(100), nullable=False)
    set_number = db.Column(db.Integer, nullable=False)
    reps = db.Column(db.Integer, nullable=False)
    weight = db.Column(db.Float, nullable=False)

    # The foreign key — links this row back to its parent Session.
    session_id = db.Column(db.Integer, db.ForeignKey("session.id"), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "exercise_name": self.exercise_name,
            "set_number": self.set_number,
            "reps": self.reps,
            "weight": self.weight,
        }
