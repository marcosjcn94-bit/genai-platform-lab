# Contratos v1

## HTTP
POST /v1/chat/completions: Bearer obrigatório; model (alias permitido), messages
(1–20 objetos role=system/user/assistant, content textual não vazio), max_tokens
(1–256, padrão 128). Corpo máximo 32768 bytes; campos desconhecidos rejeitados.
Sem streaming, app_id, provider, headers arbitrários ou retries no payload.
Resposta: id, object, created, model atendente, choices e usage do gateway.
Erros: error.code, error.message segura, error.request_id gerado no servidor.
GET /health/live não consulta dependências; /health/ready verifica gateway e DB
sem inferência. /metrics exige credencial interna própria.

## Identidade e administração
Duas aplicações sintéticas app-a e app-b. Credenciais e chaves internas diferentes.
Master key somente no gateway e processo administrativo. Bootstrap determinístico,
idempotente; não recriar chave em erro de rede ou autenticação.
Relatório usa identidade persistida da chave, nunca app_id do request.

## Exportação v1
JSON com schema_version=1, coverage, extracted_at, start, end, events e aggregates.
Intervalo UTC [start,end); fonte /spend/logs/v2; paginar até página vazia,
deduplicar request_id; falha da fonte é indisponibilidade, não sucesso vazio.
Eventos: record_id, timestamp, application, model, status (nullable), prompt_tokens,
completion_tokens, total_tokens, duration_ms e spend (decimal textual, nullable).
Campos ausentes ficam null. Conteúdo, chaves e metadados brutos são descartados.
Agregados indicam quantidade de valores conhecidos para custo/erros/tokens/latência.
Fixture sintética e exportação sanitizada alimentam o mesmo job PySpark.
