CLAUDE.md

Instruções e contexto para uso com modelos Claude/Gemini.

- Objetivo: garantir que respostas sejam estritamente baseadas no CONTEXTO retornado pela busca vetorial.
- Prompt padrão: use o `PROMPT_TEMPLATE` em `src/search.py`.
- Regras de segurança: se a resposta não estiver no contexto, retornar exatamente: "Não tenho informações necessárias para responder sua pergunta.".

Informações técnicas

- Vetores armazenados em PostgreSQL com pgVector.
- Busca: `similarity_search_with_score(query, k=10)`.
- Prompt: concatene os 10 resultados (Fonte + texto) como `CONTEXTO`.
