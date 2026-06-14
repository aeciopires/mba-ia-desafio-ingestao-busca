AGENTS.md

Instruções para agentes/IA que ajudarão a trabalhar neste repositório.

Objetivo do agente

- Ajudar a manter e evoluir a solução de ingestão e busca semântica.

Tarefas permitidas

- Rodar e validar `src/ingest.py`, `src/search.py`, `src/chat.py`.
- Atualizar documentação e scripts para compatibilidade com dependências.
- Sugerir fixes quando houver incompatibilidades de pacotes.

Regras importantes

- Nunca exponha chaves de API em commits. Use `openai.yaml`, `gemini.yaml` ou variáveis de ambiente.
- Mantenha comportamento do chat: responder apenas com base no CONTEXTO extraído.
- Ao modificar dependências, garanta versões compatíveis com Python 3.10/3.11.

Onde procurar informações

- `TASK.md` — requisitos do desafio.
- `PLAN.md` — plano de implementação.
- `README.md` — instruções de uso do projeto.
