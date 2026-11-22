"""Testes automatizados do CRUD de tarefas."""
import pytest

from app import create_app, validar_tarefa


@pytest.fixture
def client(tmp_path):
    app = create_app(str(tmp_path / "test.db"))
    app.config["TESTING"] = True
    return app.test_client()


def test_validar_titulo_vazio():
    assert validar_tarefa({"title": "   "}) == ["O título é obrigatório"]


def test_validar_titulo_muito_longo():
    assert validar_tarefa({"title": "a" * 101})


def test_validar_status_invalido():
    assert validar_tarefa({"title": "ok", "status": "x"}, parcial=True)


def test_criar_e_listar(client):
    r = client.post("/api/tasks", json={"title": "Configurar CI"})
    assert r.status_code == 201
    assert r.get_json()["status"] == "todo"
    assert len(client.get("/api/tasks").get_json()) == 1


def test_criar_sem_titulo_retorna_400(client):
    assert client.post("/api/tasks", json={}).status_code == 400


def test_atualizar_status(client):
    tid = client.post("/api/tasks", json={"title": "A"}).get_json()["id"]
    r = client.put(f"/api/tasks/{tid}", json={"status": "done"})
    assert r.status_code == 200
    assert r.get_json()["status"] == "done"


def test_remover(client):
    tid = client.post("/api/tasks", json={"title": "A"}).get_json()["id"]
    assert client.delete(f"/api/tasks/{tid}").status_code == 204
    assert client.get(f"/api/tasks/{tid}").status_code == 404


def test_tarefa_inexistente(client):
    assert client.put("/api/tasks/999", json={"title": "x"}).status_code == 404
