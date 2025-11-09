from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3

app = Flask(__name__)
CORS(app)  # Permite que o frontend acesse o backend de qualquer origem

# Criar banco de dados e tabela
def init_db():
    conn = sqlite3.connect("links.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS links (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            turma TEXT NOT NULL,
            link TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.route("/add_link", methods=["POST"])
def add_link():
    data = request.json
    turma = data.get("turma")
    link = data.get("link")

    if turma and link:
        conn = sqlite3.connect("links.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO links (turma, link) VALUES (?, ?)", (turma, link))
        conn.commit()
        conn.close()
        return jsonify({"message": "Link salvo!"}), 201
    return jsonify({"error": "Dados inválidos"}), 400

@app.route("/get_links", methods=["GET"])
def get_links():
    conn = sqlite3.connect("links.db")
    cursor = conn.cursor()
    cursor.execute("SELECT turma, link FROM links")
    data = cursor.fetchall()
    conn.close()

    links_por_turma = {}
    for turma, link in data:
        if turma not in links_por_turma:
            links_por_turma[turma] = []
        links_por_turma[turma].append(link)

    return jsonify(links_por_turma)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
