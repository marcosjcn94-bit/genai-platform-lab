# Conclusão do GenAI Platform Lab

Plano aprovado em 2026-10-02; execução na branch `implementation` a partir de `fc9ccf1`.
Repositório público: https://github.com/marcosjcn94-bit/genai-platform-lab

## Critérios

- [ ] Stack local e acesso Git/Docker recuperados; segredos e PostgreSQL preservados.
- [ ] API, identidade, consumo e persistência após reinício validados.
- [ ] Fallback, falha total e deadlines com tentativas limitadas comprovados.
- [ ] Traces correlacionados e telemetria sem conteúdo sensível comprovados.
- [ ] Carga mock de 60 s/concorrência 4 e Ollama medidos.
- [ ] Fixture e exportação sanitizada reconciliadas no PySpark.
- [ ] Databricks executado ou bloqueio externo documentado com instruções concretas.
- [ ] Terraform/imagem AWS validados sem provisionamento; CI pública verde.
- [ ] Recuperação/rollback demonstrados, documentação atualizada e commits publicados.

## Registro

- Pre-flight: API e testes consomem os contratos HTTP/exportação v1 existentes;
  CI precisa da observabilidade antes de executar o teste de traces.
- Decisão: manter a branch de implementação existente e os volumes da demo;
  outro worktree não resolve o acesso ao Docker e dividiria a evidência de runtime.
- Docker acessível fora do sandbox; serviços antigos parados e API em `Created`.
- Baseline: `uv run --frozen pytest -q`: 26 passed, 6 deselected;
  aviso de depreciação do Starlette/AnyIO registrado, sem alteração de dependências.
- Ollama HTTP respondeu; `qwen3:4b` e `llama3.2:3b` disponíveis.
- GitHub público já contém `fc9ccf1`; publicar somente por fast-forward.
- AWS continua sem autorização de provisionamento.
