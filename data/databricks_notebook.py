# Databricks notebook source
# Importar este notebook e data/jobs/aggregate_usage.py no mesmo repositório.
# Somente fixture sintética. Confirmar Free Edition/runtime/cotas antes de executar.
# COMMAND ----------
from pathlib import Path
import sys

root = Path.cwd()
# Ajustar para a raiz do checkout no workspace Databricks, se necessário.
sys.path.insert(0, str(root / "data" / "jobs"))
from aggregate_usage import aggregate_usage, read_export

# COMMAND ----------
# Usar um Volume autorizado do Unity Catalog na Free Edition.
# Fazer upload de data/fixtures/usage-v1.json para o caminho abaixo.
dbutils.widgets.text("fixture_path", "/Volumes/workspace/default/lab/usage-v1.json")
dbutils.widgets.text("output_path", "/Volumes/workspace/default/lab/daily")
fixture_path = dbutils.widgets.get("fixture_path")
output_path = dbutils.widgets.get("output_path")
result = aggregate_usage(read_export(spark, fixture_path))
display(result.orderBy("day", "application", "model"))

# COMMAND ----------
rows = {(str(r.day), r.application): r.asDict() for r in result.collect()}
assert rows[("2026-01-01", "app-a")]["total_tokens"] == 30
assert str(rows[("2026-01-01", "app-a")]["spend"]) == "0.300000000000"
assert rows[("2026-01-01", "app-b")]["spend"] is None
assert rows[("2026-01-01", "app-b")]["errors"] == 1
result.write.mode("overwrite").parquet(output_path)
print("Comparação com fixture local aprovada.")
