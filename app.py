from flask import Flask, request, jsonify
import sqlite3
import os

app = Flask(__name__)
DB_PATH = os.getenv("BOOK_DB_PATH", "/data/books.db")
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            author TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

@app.route("/books", methods=["GET"])
def get_books():
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        "SELECT id, name, author FROM books"
    ).fetchall()
    conn.close()

    return jsonify([
        {"id": r[0], "name": r[1], "author": r[2]}
        for r in rows
    ])

@app.route("/books", methods=["POST"])
def add_book():
    data = request.get_json()

    if not data or not data.get("name") or not data.get("author"):
        return jsonify({"error": "Name and author required"}), 400

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.execute(
        "INSERT INTO books (name, author) VALUES (?, ?)",
        (data["name"], data["author"])
    )
    conn.commit()
    book_id = cursor.lastrowid
    conn.close()

    return jsonify({
        "message": "Book added successfully",
        "id": book_id
    }), 201

@app.route("/books/<int:book_id>", methods=["GET"])
def get_book(book_id):
    conn = sqlite3.connect(DB_PATH)
    row = conn.execute(
        "SELECT id, name, author FROM books WHERE id = ?",
        (book_id,)
    ).fetchone()
    conn.close()

    if not row:
        return jsonify({"error": "Book not found"}), 404

    return jsonify({
        "id": row[0],
        "name": row[1],
        "author": row[2]
    })

init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
