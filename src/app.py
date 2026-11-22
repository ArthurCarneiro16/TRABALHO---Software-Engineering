"""TechFlow Tasks - API e interface web para gerenciamento de tarefas (CRUD)."""
import sqlite3

from flask import Flask, jsonify, render_template, request

STATUS_VALIDOS = ("todo", "in_progress", "done")
PRIORIDADES_VALIDAS = ("baixa", "media", "alta")
TITULO_MAX = 100


def validar_tarefa(dados, parcial=False):
    """Valida os dados de uma tarefa. Retorna uma lista de erros (vazia se ok)."""
    erros = []
    if not isinstance(dados, dict):
        return ["Corpo da requisição inválido"]

    if "title" in dados or not parcial:
        titulo = dados.get("title")
        if not isinstance(titulo, str) or not titulo.strip():
            erros.append("O título é obrigatório")
        elif len(titulo.strip()) > TITULO_MAX:
            erros.append(f"O título deve ter no máximo {TITULO_MAX} caracteres")

    if "status" in dados and dados["status"] not in STATUS_VALIDOS:
        erros.append("Status inválido")

    if "priority" in dados and dados["priority"] not in PRIORIDADES_VALIDAS:
        erros.append("Prioridade inválida")
    return erros


def create_app(db_path="tasks.db"):
    """Cria e configura a aplicação Flask."""
    app = Flask(__name__)
    app.config["DB_PATH"] = db_path

    def get_db():
        conn = sqlite3.connect(app.config["DB_PATH"])
        conn.row_factory = sqlite3.Row
        return conn

    with get_db() as conn:
        conn.execute(
            """CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT DEFAULT '',
                status TEXT NOT NULL DEFAULT 'todo',
                priority TEXT NOT NULL DEFAULT 'media'
            )"""
        )
        # Migração: bancos criados antes da mudança de escopo não têm a coluna
        colunas = [c["name"] for c in conn.execute("PRAGMA table_info(tasks)")]
        if "priority" not in colunas:
            conn.execute(
                "ALTER TABLE tasks ADD COLUMN priority TEXT NOT NULL DEFAULT 'media'"
            )

    @app.get("/")
    def index():
        return render_template("index.html")

    # CREATE
    @app.post("/api/tasks")
    def criar_tarefa():
        dados = request.get_json(silent=True) or {}
        erros = validar_tarefa(dados)
        if erros:
            return jsonify({"errors": erros}), 400
        with get_db() as conn:
            cur = conn.execute(
                "INSERT INTO tasks (title, description, status, priority) "
                "VALUES (?, ?, ?, ?)",
                (dados["title"].strip(), dados.get("description", ""),
                 dados.get("status", "todo"), dados.get("priority", "media")),
            )
            tarefa = conn.execute(
                "SELECT * FROM tasks WHERE id = ?", (cur.lastrowid,)
            ).fetchone()
        return jsonify(dict(tarefa)), 201

    # READ (lista)
    @app.get("/api/tasks")
    def listar_tarefas():
        with get_db() as conn:
            linhas = conn.execute(
                "SELECT * FROM tasks ORDER BY CASE priority "
                "WHEN 'alta' THEN 0 WHEN 'media' THEN 1 ELSE 2 END, id"
            ).fetchall()
        return jsonify([dict(linha) for linha in linhas])

    # READ (uma)
    @app.get("/api/tasks/<int:task_id>")
    def obter_tarefa(task_id):
        with get_db() as conn:
            tarefa = conn.execute(
                "SELECT * FROM tasks WHERE id = ?", (task_id,)
            ).fetchone()
        if tarefa is None:
            return jsonify({"errors": ["Tarefa não encontrada"]}), 404
        return jsonify(dict(tarefa))

    # UPDATE
    @app.put("/api/tasks/<int:task_id>")
    def atualizar_tarefa(task_id):
        dados = request.get_json(silent=True) or {}
        erros = validar_tarefa(dados, parcial=True)
        if erros:
            return jsonify({"errors": erros}), 400
        with get_db() as conn:
            atual = conn.execute(
                "SELECT * FROM tasks WHERE id = ?", (task_id,)
            ).fetchone()
            if atual is None:
                return jsonify({"errors": ["Tarefa não encontrada"]}), 404
            conn.execute(
                "UPDATE tasks SET title = ?, description = ?, status = ?, "
                "priority = ? WHERE id = ?",
                (dados.get("title", atual["title"]).strip(),
                 dados.get("description", atual["description"]),
                 dados.get("status", atual["status"]),
                 dados.get("priority", atual["priority"]), task_id),
            )
            tarefa = conn.execute(
                "SELECT * FROM tasks WHERE id = ?", (task_id,)
            ).fetchone()
        return jsonify(dict(tarefa))

    # DELETE
    @app.delete("/api/tasks/<int:task_id>")
    def remover_tarefa(task_id):
        with get_db() as conn:
            cur = conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        if cur.rowcount == 0:
            return jsonify({"errors": ["Tarefa não encontrada"]}), 404
        return "", 204

    return app


if __name__ == "__main__":
    create_app().run(debug=True)
