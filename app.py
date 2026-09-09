from datetime import date as date_type
from flask import Flask, request, jsonify
from models import db, Session, SetEntry

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///gym_tracker.db"
db.init_app(app)

with app.app_context():
    db.create_all()


# ---------- Log a new session ----------
# Expects JSON like:
# {
#   "date": "2026-09-09",
#   "exercises": [
#     {"exercise_name": "Bench Press", "set_number": 1, "reps": 8, "weight": 60},
#     {"exercise_name": "Bench Press", "set_number": 2, "reps": 8, "weight": 60}
#   ]
# }
@app.route("/sessions", methods=["POST"])
def create_session():
    data = request.get_json()

    session_date = date_type.fromisoformat(data["date"])
    new_session = Session(date=session_date)

    for entry in data["exercises"]:
        set_entry = SetEntry(
            exercise_name=entry["exercise_name"],
            set_number=entry["set_number"],
            reps=entry["reps"],
            weight=entry["weight"],
        )
        new_session.set_entries.append(set_entry)

    db.session.add(new_session)
    db.session.commit()

    return jsonify(new_session.to_dict()), 201


# ---------- View full history, most recent first ----------
@app.route("/sessions", methods=["GET"])
def get_sessions():
    sessions = Session.query.order_by(Session.date.desc()).all()
    return jsonify([s.to_dict() for s in sessions])


# ---------- View one specific session ----------
@app.route("/sessions/<int:session_id>", methods=["GET"])
def get_session(session_id):
    session = Session.query.get_or_404(session_id)
    return jsonify(session.to_dict())


# ---------- Delete a session ----------
@app.route("/sessions/<int:session_id>", methods=["DELETE"])
def delete_session(session_id):
    session = Session.query.get_or_404(session_id)
    db.session.delete(session)
    db.session.commit()
    return jsonify({"message": "Session deleted"})


# ---------- Quick reference: last time you did an exercise ----------
@app.route("/exercises/<string:exercise_name>/last", methods=["GET"])
def get_last_entry(exercise_name):
    last_entry = (
        SetEntry.query.filter_by(exercise_name=exercise_name)
        .join(Session)
        .order_by(Session.date.desc())
        .first()
    )

    if last_entry is None:
        return jsonify({"message": "No history for this exercise yet"}), 404

    return jsonify(last_entry.to_dict())


# ---------- All-time personal record for an exercise ----------
# PR = highest weight ever lifted for that exercise (simple definition;
# could be made smarter later, e.g. weight x reps for volume PRs).
@app.route("/exercises/<string:exercise_name>/pr", methods=["GET"])
def get_pr(exercise_name):
    best_entry = (
        SetEntry.query.filter_by(exercise_name=exercise_name)
        .order_by(SetEntry.weight.desc())
        .first()
    )

    if best_entry is None:
        return jsonify({"message": "No history for this exercise yet"}), 404

    return jsonify(best_entry.to_dict())


# ---------- Suggested target for next session (progressive overload) ----------
# Simple rule-based logic to start:
# - Look at the last session for this exercise.
# - If every set hit >= 8 reps, suggest a small weight increase (+2.5kg).
# - Otherwise, suggest repeating the same weight to solidify it.
@app.route("/exercises/<string:exercise_name>/suggestion", methods=["GET"])
def get_suggestion(exercise_name):
    recent_entries = (
        SetEntry.query.filter_by(exercise_name=exercise_name)
        .join(Session)
        .order_by(Session.date.desc())
        .limit(5)  # last session's sets (assuming ~3-5 sets per session)
        .all()
    )

    if not recent_entries:
        return jsonify({"message": "No history for this exercise yet"}), 404

    last_weight = recent_entries[0].weight
    all_hit_target_reps = all(e.reps >= 8 for e in recent_entries)

    if all_hit_target_reps:
        suggested_weight = last_weight + 2.5
        reasoning = "You hit 8+ reps on every set last time — try increasing the weight slightly."
    else:
        suggested_weight = last_weight
        reasoning = "Not every set hit 8 reps last time — repeat this weight and aim to hit it."

    return jsonify({
        "exercise_name": exercise_name,
        "last_weight": last_weight,
        "suggested_weight": suggested_weight,
        "reasoning": reasoning,
    })


if __name__ == "__main__":
    app.run(debug=True)
