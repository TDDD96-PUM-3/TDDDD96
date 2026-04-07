from flask import Flask, jsonify, request
import mysql.connector
import os

app = Flask(__name__)

def get_db():
    return mysql.connector.connect(
        host=os.environ["DB_HOST"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        database=os.environ["DB_NAME"],
    )

@app.route("/users", methods=["GET"])
def get_users():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(users)

@app.route("/users/<int:user_id>", methods=["GET"])
def get_user(user_id):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify(user)

@app.route("/users", methods=["POST"])
def create_user():
    data = request.get_json()
    if not data or not data.get("name") or not data.get("email"):
        return jsonify({"error": "name and email are required"}), 400
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "INSERT INTO users (name, email) VALUES (%s, %s)",
        (data["name"], data["email"]),
    )
    conn.commit()
    new_id = cursor.lastrowid
    cursor.execute("SELECT * FROM users WHERE id = %s", (new_id,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return jsonify(user), 201

@app.route("/users/<int:user_id>", methods=["PUT"])
def update_user(user_id):
    data = request.get_json()
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    if not cursor.fetchone():
        cursor.close()
        conn.close()
        return jsonify({"error": "User not found"}), 404
    fields = {k: v for k, v in data.items() if k in ("name", "email")}
    if not fields:
        return jsonify({"error": "Nothing to update"}), 400
    set_clause = ", ".join(f"{k} = %s" for k in fields)
    cursor.execute(
        f"UPDATE users SET {set_clause} WHERE id = %s",
        (*fields.values(), user_id),
    )
    conn.commit()
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return jsonify(user)

@app.route("/users/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE id = %s", (user_id,))
    if not cursor.fetchone():
        cursor.close()
        conn.close()
        return jsonify({"error": "User not found"}), 404
    cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": f"User {user_id} deleted"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
