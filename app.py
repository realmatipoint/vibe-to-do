## vibe coded by matipoint (:

from flask import Flask, render_template, request, jsonify
import json
import os
from datetime import datetime

app = Flask(__name__)
TASKS_FILE = "tasks.json"


def load_data():
    if os.path.exists(TASKS_FILE):
        try:
            with open(TASKS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                # Ensure structure
                if "active" not in data:
                    data["active"] = []
                if "trash" not in data:
                    data["trash"] = []
                return data
        except:
            pass
    return {"active": [], "trash": []}


def save_data(data):
    with open(TASKS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/tasks", methods=["GET", "POST", "DELETE"])
def tasks():
    data = load_data()

    if request.method == "GET":
        return jsonify(data["active"])

    elif request.method == "POST":
        new_task = {
            "id": int(datetime.now().timestamp() * 1000),
            "text": request.json["text"],
            "done": False,
            "created": datetime.now().isoformat()
        }
        data["active"].append(new_task)
        save_data(data)
        return jsonify(new_task), 201

    elif request.method == "DELETE":
        task_id = int(request.args.get("id"))
        task = next((t for t in data["active"] if t["id"] == task_id), None)
        if task:
            task["deleted_at"] = datetime.now().isoformat()
            data["active"] = [t for t in data["active"] if t["id"] != task_id]
            data["trash"].append(task)
            save_data(data)
        return jsonify({"success": True})


@app.route("/toggle/<int:task_id>", methods=["POST"])
def toggle(task_id):
    data = load_data()
    for t in data["active"]:
        if t["id"] == task_id:
            t["done"] = not t["done"]
            break
    save_data(data)
    return jsonify({"success": True})


@app.route("/trash", methods=["GET"])
def trash():
    data = load_data()
    return jsonify(data["trash"])


@app.route("/restore/<int:task_id>", methods=["POST"])
def restore(task_id):
    data = load_data()
    task = next((t for t in data["trash"] if t["id"] == task_id), None)
    if task:
        data["trash"] = [t for t in data["trash"] if t["id"] != task_id]
        del task["deleted_at"]
        data["active"].append(task)
        save_data(data)
    return jsonify({"success": True})


@app.route("/permadelete/<int:task_id>", methods=["DELETE"])
def permadelete(task_id):
    data = load_data()
    data["trash"] = [t for t in data["trash"] if t["id"] != task_id]
    save_data(data)
    return jsonify({"success": True})


if __name__ == "__main__":
    app.run(debug=True)