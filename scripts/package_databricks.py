"""Build one importable notebook from the canonical job and synthetic fixture."""

import json
from pathlib import Path


def main():
    module = Path("data/jobs/aggregate_usage.py").read_text(encoding="utf-8")
    definitions = module.split("\ndef main():", 1)[0]
    fixture = json.loads(Path("data/fixtures/usage-v1.json").read_text(encoding="utf-8"))
    cells = [
        (
            "markdown",
            "# GenAI Platform Lab: validação Databricks\n"
            "Notebook gerado do job canônico e fixture sintética. Não requer AWS, "
            "segredos ou upload adicional. Execute em Free Edition.\n"
            "A última célula cria/reutiliza o Volume `genai_platform_lab` no catálogo/schema "
            "atual e sobrescreve somente sua pasta `fixture_daily`.",
        ),
        ("code", definitions),
        (
            "code",
            "fixture = " + repr(fixture) + "\n"
            "for event in fixture['events']:\n"
            "    if event['duration_ms'] is not None:\n"
            "        event['duration_ms'] = float(event['duration_ms'])\n"
            "frame = spark.createDataFrame(fixture['events'], EVENT_SCHEMA)\n"
            "result = aggregate_usage(frame)\n"
            "display(result.orderBy('day', 'application', 'model'))",
        ),
        (
            "code",
            "rows = {(str(r.day), r.application, r.model): r.asDict() "
            "for r in result.collect()}\n"
            "a = rows[('2026-01-01', 'app-a', 'primary')]\n"
            "b = rows[('2026-01-01', 'app-b', 'reserve')]\n"
            "assert a['requests'] == 2 and a['total_tokens'] == 30\n"
            "assert str(a['spend']) == '0.300000000000'\n"
            "assert a['status_known'] == 1 and a['errors'] == 0\n"
            "assert a['latency_mean_ms'] == 1500\n"
            "assert b['spend'] is None and b['spend_known'] == 0 and b['errors'] == 1\n"
            "print('DATABRICKS_FIXTURE_OK: resultados iguais ao PySpark local')",
        ),
        (
            "code",
            "namespace = spark.sql('SELECT current_catalog() AS catalog, "
            "current_schema() AS schema').first()\n"
            "spark.sql('CREATE VOLUME IF NOT EXISTS genai_platform_lab')\n"
            "output = (f'/Volumes/{namespace.catalog}/{namespace.schema}/'\n"
            "          'genai_platform_lab/fixture_daily')\n"
            "result.write.mode('overwrite').parquet(output)\n"
            "first = sorted(str(r) for r in spark.read.parquet(output).collect())\n"
            "result.write.mode('overwrite').parquet(output)\n"
            "assert first == sorted(str(r) for r in spark.read.parquet(output).collect())\n"
            "print('DATABRICKS_PARQUET_OK: reexecução idempotente')",
        ),
    ]
    notebook = {
        "nbformat": 4,
        "nbformat_minor": 5,
        "metadata": {
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"}
        },
        "cells": [],
    }
    for index, (kind, source) in enumerate(cells):
        cell = {
            "cell_type": kind,
            "id": f"lab-{index}",
            "metadata": {},
            "source": source.splitlines(keepends=True),
        }
        if kind == "code":
            compile(source, f"cell-{index}", "exec")
            cell.update(execution_count=None, outputs=[])
        notebook["cells"].append(cell)
    target = Path("data/databricks_demo.ipynb")
    target.write_text(json.dumps(notebook, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("Notebook sintético gerado; células Python compiladas; execução remota pendente.")


if __name__ == "__main__":
    main()
