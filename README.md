# TechFlow Tasks

Sistema web de gerenciamento de tarefas desenvolvido para a **TechFlow Solutions**
(empresa fictícia) como projeto da disciplina de Engenharia de Software.

## Objetivo
Permitir que uma startup de logística acompanhe o fluxo de trabalho em um quadro
Kanban, priorize tarefas críticas e monitore o andamento da equipe.

## Escopo inicial
- CRUD de tarefas (criar, listar, atualizar, remover)
- Quadro com três colunas: A Fazer, Em Progresso e Concluído
- API REST + interface web simples

## Metodologia
**Kanban** com ciclos curtos inspirados no Scrum. O planejamento é feito na aba
**Projects** do GitHub (To Do / In Progress / Done), e cada card vira um ou mais
commits semânticos (`feat:`, `fix:`, `test:`, `docs:`, `ci:`).

## Tecnologias
Python 3.12, Flask, SQLite, pytest, flake8 e GitHub Actions.

## Como executar
```bash
pip install -r requirements.txt
python src/app.py          # abre em http://127.0.0.1:5000
```

## Testes e qualidade
```bash
pytest -v
flake8 src tests
```
O pipeline em `.github/workflows/ci.yml` roda os dois comandos a cada push/PR.

## Estrutura
```
src/         código da aplicação
tests/       testes automatizados
docs/        diagramas UML e prints
.github/     workflow de CI
```

## Gestão de mudanças
_(preencher na etapa de mudança de escopo: o que mudou, por quê e qual card foi criado)_
