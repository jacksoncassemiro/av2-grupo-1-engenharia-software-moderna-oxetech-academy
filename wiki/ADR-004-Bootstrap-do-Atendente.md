# ADR-004 — Bootstrap do primeiro atendente por seed idempotente

**Status:** Aceito · **Data:** 2026-07-29 · **Decisores:** Equipe 01

## Contexto

Problema do ovo e da galinha, **não previsto por nenhuma das fontes do enunciado**:

- Só o Atendente cadastra médicos, especialidades, horários e pacientes.
- Numa base recém-criada não existe nenhum atendente.
- Logo, o sistema recém-instalado é inutilizável: ninguém consegue fazer nada.

Uma proposta anterior sugeria popular um atendente por seed e paramos aqui: **se só existe o
seed, como se cria o segundo atendente?** Se a senha do seed vazar, ou a pessoa sair da
clínica, não há caminho de recuperação — e a funcionalidade "cadastrar atendente" simplesmente
não existe para demonstrar.

## Decisão

**Duas peças complementares.**

**1. Seed idempotente** (`backend/app/seeds/seed.py`) cria o primeiro atendente com
credenciais vindas do ambiente (`SEED_ATENDENTE_LOGIN`, `SEED_ATENDENTE_SENHA`), mais três
especialidades base para a demonstração.

Idempotente de verdade: `UsuarioRepository.existe_atendente()` é consultado antes de inserir.
Rodar dez vezes tem o mesmo efeito de rodar uma. O CI executa o seed **duas vezes** justamente
para provar isso.

```bash
make seed   # ou: docker compose exec backend python -m app.seeds.seed
```

**2. RN14** — *apenas usuários com perfil ATENDENTE podem criar outros ATENDENTE. Não existe
rota pública de cadastro de atendente.* Materializada em `POST /api/atendente/atendentes`
protegida por `Depends(exigir_atendente)`, e registrada como **US-15**.

## Consequências

**Positivas**

- Base nova fica utilizável em um comando, sem SQL manual.
- Existe caminho de crescimento: o atendente do seed cadastra os colegas pela UI.
- Nenhuma rota pública cria privilégio — não há escalonamento por auto-registro.
- Credenciais fora do código, em variável de ambiente (12-factor).
- A idempotência é testada no pipeline, não prometida no README.

**Negativas**

- Se a senha do seed nunca for trocada, é uma credencial conhecida. Mitigação: `.env.example`
  avisa explicitamente que é valor de desenvolvimento, e a senha é trocável por variável.
- Se **todos** os atendentes forem desativados, volta o impasse. Recuperação: rodar o seed de
  novo (`existe_atendente()` considera apenas o perfil, então convém checar `ativo` antes de
  desativar o último). Anotado como risco conhecido, aceito no escopo do MVP.
- Um perfil a menos de granularidade: o atendente acumula o papel de administrador.

## Alternativas

| Alternativa | Por que não |
|---|---|
| Só seed, sem RN14 | Sem caminho de recuperação nem funcionalidade demonstrável |
| Rota pública `POST /register` de atendente | Qualquer visitante viraria atendente e leria todos os prontuários — falha de segurança indefensável na avaliação |
| Perfil ADMIN separado | Conceitualmente melhor, mas adiciona terceiro perfil, telas, guards e testes a um MVP de 2 semanas. Registrado como evolução futura |
| Rota `/bootstrap-admin` protegida por token, ativa só com tabela vazia | Elegante, mas é mais código e mais teste para resolver o que o seed já resolve |
| INSERT manual no banco | Não reproduzível, não versionado, não testável |


---

> 📄 Esta página é gerada a partir de `docs/` no repositório. **Não edite aqui** — edite o arquivo correspondente e rode `scripts/publicar-wiki.sh`.
