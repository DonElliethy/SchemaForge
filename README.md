# SchemaForge

A schema-aware SQL sandbox and critique engine, built in Python to go deep on database design theory and backend engineering fundamentals — not an LLM wrapper.

You give it a schema (as raw DDL, or an English description), and it: generates realistic, referentially-consistent fake data for it; lets you query it in plain English; and — the core of the project — critiques the schema itself: normalization issues, missing indexes, and whether it can even answer the queries you actually need it to.

## Why this project exists

Most "AI schema tool" demos lean entirely on an LLM to do the reasoning. This one deliberately doesn't. The LLM is scoped to exactly two narrow jobs — translating an English schema description into DDL, and translating an English question into SQL. Everything that actually reasons about the schema (normalization checking, index recommendations, query-coverage analysis) is handwritten, grounded in real database theory, and tested.

## Status: in progress

This is being built in public, phase by phase. Current state:

- [x] **Phase 0 — Ingestion**: Pydantic schema models (`Column`, `Table`, `ForeignKey`, `Schema`) with validation rules (no blank names, primary keys can't be nullable, foreign keys must reference real columns)
- [x] **Phase 0 — DDL Parser**: Postgres-dialect `CREATE TABLE` parsing via `sqlglot`, converting raw SQL into the schema models above
- [x] **Phase 0b — FK Dependency Graph**: `networkx`-based directed graph of foreign key relationships, topologically sorted into valid data-generation order (parents before children), with cycle detection
- [ ] **Phase 0b — Fake Data Generator**: `Faker`-based synthetic data generation respecting referential integrity
- [ ] **Phase 0c — NL → DDL**: optional entry point letting users describe a schema in plain English instead of writing SQL
- [ ] **Phase 1 — NL-to-SQL Sandbox**: ask questions about the data in English, get them run against DuckDB
- [ ] **Phase 2 — Critique Engine**: functional dependency analysis, normalization checking (1NF–BCNF), query-to-schema coverage checks, index recommendations backed by real `EXPLAIN ANALYZE` timing
- [ ] **Phase 3 — Warehouse Validator**: star/snowflake schema detection for dimensional modeling

## Architecture

```
ingestion/   → parse a schema (DDL or NL) into typed Python objects
data_gen/    → build the FK dependency graph, generate consistent fake data
querying/    → NL-to-SQL sandbox, query execution, guardrails
critique/    → normalization checks, index recommendations, query coverage
warehouse/   → star/snowflake schema validation
```

Dependency direction is one-way: `ingestion → data_gen → querying → critique → warehouse`. Nothing earlier in the chain imports from something later.

## Tech stack

| Purpose | Tool |
|---|---|
| Package management | `uv` |
| Schema representation | `Pydantic` |
| SQL parsing (DDL + queries) | `sqlglot` |
| FK dependency ordering | `networkx` |
| Synthetic data | `Faker` |
| Query execution | `DuckDB` |
| NL-to-SQL / NL-to-DDL | `DSPy` + `Ollama` (local model) |
| API | `FastAPI` |
| Testing | `pytest` |

## Key design decisions

- **Postgres dialect only (v1 scope)** — not trying to support every SQL dialect; scoped deliberately to keep the project shippable
- **Single-column primary keys only (v1 scope)** — composite keys are a known, deliberate simplification for now
- **Foreign keys as a separate model from `Column`**, not bolted onto it — avoids every column carrying mostly-unused nullable FK fields, and mirrors how FK constraints actually work in SQL
- **`data_type` stored as a raw string**, not a structured type object — downstream features that need to reason about type (e.g. "is this numeric") inspect the string on demand, rather than paying the cost of full type modeling upfront for something not yet needed
- **LLM usage is intentionally minimal** — confined to two narrow translation tasks (NL→DDL, NL→SQL); all schema reasoning is handwritten and tested

## Getting started

```bash
git clone git@github.com:DonElliethy/SchemaForge.git
cd SchemaForge
uv sync
uv run pytest -v
```

## Running tests

```bash
uv run pytest tests/ -v
```

---

*Built as a hands-on deep dive into database theory (functional dependencies, normalization, indexing, dimensional modeling) through real, tested Python code — not as a portfolio piece leaning on an LLM to do the thinking.*
