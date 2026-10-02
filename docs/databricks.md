# Databricks Free Edition: uma única importação

Objetivo: executar a mesma transformação PySpark em outro ambiente e comparar
resultados. Não conectar AWS, não informar credenciais e não mudar de plano.

## Passo a passo

1. Entre no workspace da sua Databricks Free Edition.
2. Abra **Workspace**; no menu da pasta desejada, escolha **Import**.
3. Selecione **File** e o arquivo local `data/databricks_demo.ipynb`.
4. Abra o notebook importado e selecione o compute **Serverless** disponível.
5. Execute **Run all**. A fixture já está no notebook; não há upload adicional,
   configuração de caminhos ou clonagem de repositório.
6. Confirme as mensagens `DATABRICKS_FIXTURE_OK` e `DATABRICKS_PARQUET_OK`.
   Compartilhe somente essas mensagens ou o erro da célula, sem dados de login.

Resultados esperados: app-a tem 2 requisições, 30 tokens e custo sintético 0,3;
app-b preserva custo nulo e tem 1 erro. O custo da fixture é um exemplo numérico,
não uma cobrança. A última célula cria/reutiliza o Volume `genai_platform_lab`
no catálogo/schema atual e sobrescreve apenas sua pasta `fixture_daily`.

Se a criação de Volume for negada, escolha no workspace um catálogo/schema em
que você tenha permissão de criação e repita a última célula. Se não houver
permissão ou a cota de compute estiver esgotada, registre o bloqueio; não contrate
recursos pagos para concluir esta demonstração.

## Origem e validação

Gerado pelo comando `uv run python -m scripts.package_databricks` a partir de
`data/jobs/aggregate_usage.py` e da fixture versionada. Não editar a cópia gerada
da transformação: altere o job canônico e regenere o notebook.

Células Python compiladas e transformação/fixture executadas no Spark local.
A célula de Volume e a execução Databricks são validações remotas separadas.
Esta sessão não tem navegador conectado para realizar seu login ou executar o notebook.

Documentação oficial:
- [Importação de notebooks](https://docs.databricks.com/aws/en/notebooks/notebook-export-import)
- [Limitações da Free Edition](https://docs.databricks.com/aws/en/getting-started/free-edition-limitations)
