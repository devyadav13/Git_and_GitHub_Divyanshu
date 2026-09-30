"""
Flask + MongoDB Atlas Project
Author: Divyanshu Yadav

Features:
1. /api route -> reads a JSON list from a backend file (data.json) and returns it as a JSON response.
2. / route -> renders an HTML form.
3. /submit route -> accepts the form POST data, validates it, and inserts it into MongoDB Atlas.
   - On success  -> redirects to /success ("Data submitted successfully")
   - On error    -> re-renders the SAME form page with the error message (no redirection)
"""

import os
import json
from flask import Flask, jsonify, render_template, request, redirect, url_for
from pymongo import MongoClient
from pymongo.errors import PyMongoError, ConnectionFailure, ConfigurationError
from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------
load_dotenv()  # loads MONGO_URI from a local .env file (not committed to git)

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "data.json")

MONGO_URI = os.environ.get("MONGO_URI", "")
DB_NAME = os.environ.get("DB_NAME", "flask_mongo_db")
COLLECTION_NAME = os.environ.get("COLLECTION_NAME", "submissions")

client = None
collection = None
mongo_connect_error = None

try:
    if MONGO_URI:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        client.admin.command("ping")  # verifies the connection immediately
        db = client[DB_NAME]
        collection = db[COLLECTION_NAME]
    else:
        mongo_connect_error = "MONGO_URI is not set. Add it to your .env file."
except (ConnectionFailure, ConfigurationError, PyMongoError) as exc:
    mongo_connect_error = f"Could not connect to MongoDB Atlas: {exc}"


# ---------------------------------------------------------------------------
# Task 1: JSON API route
# ---------------------------------------------------------------------------
@app.route("/api", methods=["GET"])
def api():
    """Reads the JSON list from the backend file and returns it as a response."""
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return jsonify(data), 200
    except FileNotFoundError:
        return jsonify({"error": "data.json not found on the server"}), 404
    except json.JSONDecodeError:
        return jsonify({"error": "data.json is not valid JSON"}), 500


# ---------------------------------------------------------------------------
# Task 2: Frontend form + MongoDB Atlas insert
# ---------------------------------------------------------------------------
@app.route("/", methods=["GET"])
def index():
    """Renders the form. error/old_data are passed only when we bounce back
    from a failed submission so the page can show the error inline."""
    return render_template("index.html", error=None, old_data={})


@app.route("/submit", methods=["POST"])
def submit():
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()
    message = request.form.get("message", "").strip()

    old_data = {"name": name, "email": email, "message": message}

    # ---- basic server-side validation ----
    if not name or not email or not message:
        return render_template(
            "index.html",
            error="All fields are required. Please fill in name, email and message.",
            old_data=old_data,
        ), 400

    if "@" not in email or "." not in email:
        return render_template(
            "index.html",
            error="Please enter a valid email address.",
            old_data=old_data,
        ), 400

    # ---- MongoDB availability check ----
    if collection is None:
        return render_template(
            "index.html",
            error=f"Database error: {mongo_connect_error}",
            old_data=old_data,
        ), 500

    # ---- insert into MongoDB Atlas ----
    try:
        document = {"name": name, "email": email, "message": message}
        collection.insert_one(document)
    except PyMongoError as exc:
        # Stay on the SAME page and show the error, no redirection.
        return render_template(
            "index.html",
            error=f"Failed to save data to MongoDB Atlas: {exc}",
            old_data=old_data,
        ), 500

    # Success -> redirect to a different page
    return redirect(url_for("success"))


@app.route("/success", methods=["GET"])
def success():
    return render_template("success.html")


if __name__ == "__main__":
    # debug=True is fine for local development on Windows; turn off in production
    app.run(debug=True)
