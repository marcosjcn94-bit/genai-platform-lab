# Decisões arquiteturais

1. **Fonte de consumo:** LiteLLM/PostgreSQL; exportações e Parquet são derivados reconstruíveis. Não há ledger próprio.
2. **Identidade:** credencial externa identifica aplicação no servidor; uma chave virtual por aplicação. Cliente não escolhe identidade, provedor nem política de retry.
3. **Custo:** mock e Ollama locais por padrão. Exceção de 2026-10-02: demo AWS autorizada por até quatro horas, com reserva operacional de US$ 2 em créditos e snapshot final retido. Recursos regionais somente em us-east-2; reserva não é teto automático.
4. **Confiabilidade:** retries e fallback no gateway, sem repetição na API. Teto de quatro tentativas comprovado por integração com contadores do mock.
5. **Privacidade:** observabilidade usa atributos permitidos explicitamente. Nenhum conteúdo de mensagens ou credenciais em telemetria.
6. **Interface:** Swagger, Grafana, Jaeger e relatório administrativo; sem frontend próprio.
7. **Execução:** repositório novo na branch implementation, sem outra linha de trabalho a isolar. Orientação LOW já confirmada no plano.
8. **Benchmark:** p95 usa nearest rank; latências Ollama incluem apenas respostas bem-sucedidas do primário, com primeira chamada separada. Não tratar fallback como sucesso do modelo medido.
9. **Databricks:** notebook único gerado do job canônico e fixture sintética, evitando ajustes manuais de imports e uploads. Execução local da transformação não comprova execução na Free Edition.
10. **Avaliação AWS:** manter a demo temporária com mock e acesso interno ECS Exec; custo estimado não autoriza provisionamento. Resolver pendências de logs/administração/banco/limpeza e revisar plano antes de criar recursos. Apresentação do portfólio após a etapa AWS, por orientação do usuário.
11. **Preparação AWS:** admin em container opcional da mesma task, desativado por padrão e removido por redeploy após bootstrap/export; API sem master key. PostgreSQL 16.15, readiness dependente do DB, exclusão protegida e snapshot com sufixo único. Testes usam provider simulado; plano privado com digests placeholder não autoriza aplicação.
