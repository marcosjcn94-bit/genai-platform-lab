# Decisões arquiteturais

1. **Fonte de consumo:** LiteLLM/PostgreSQL; exportações e Parquet são derivados reconstruíveis. Não há ledger próprio.
2. **Identidade:** credencial externa identifica aplicação no servidor; uma chave virtual por aplicação. Cliente não escolhe identidade, provedor nem política de retry.
3. **Custo:** mock e Ollama locais por padrão; nenhuma criação AWS autorizada. Recursos regionais declarativos somente em us-east-2.
4. **Confiabilidade:** retries e fallback no gateway, sem repetição na API. Teto pretendido de quatro tentativas será comprovado por integração.
5. **Privacidade:** observabilidade usa atributos permitidos explicitamente. Nenhum conteúdo de mensagens ou credenciais em telemetria.
6. **Interface:** Swagger, Grafana, Jaeger e relatório administrativo; sem frontend próprio.
7. **Execução:** repositório novo na branch implementation, sem outra linha de trabalho a isolar. Orientação LOW já confirmada no plano.
