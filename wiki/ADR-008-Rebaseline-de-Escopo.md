# ADR-008 — Rebaseline de escopo e separação backend × frontend na documentação

**Status:** Aceito · **Data:** 2026-07-30 · **Decisores:** Equipe 01

## Contexto

Três fatos mudaram depois que o planejamento inicial foi escrito:

1. **O prazo encolheu.** A entrega é **10/08** e as reuniões só começam em **31/07**, com
   encontros às segundas, quartas, sextas e sábados. São **8 dias corridos de trabalho**, não
   duas semanas cheias.
2. **A equipe encolheu.** Jonatha da Silva Fernandes saiu do grupo. Ele era o responsável
   nomeado por três dos cinco entregáveis de Engenharia (arquitetura MVC, Clean Code e Design
   Patterns). Restam **6 pessoas**.
3. **O planejamento inflou.** O board chegou a **82 itens**, cobrindo 16 User Stories e 15
   regras de negócio. O professor foi explícito de que *"não é um projeto tão grande e
   complexo, essa não é a ideia"*. Planejar 82 itens para 8 dias garante que a maior parte
   não seja feita — e um board com dois terços em "To Do" na apresentação vale menos do que um
   board menor e concluído.

Além disso, dois problemas de qualidade da própria documentação foram identificados:

- **A arquitetura MVC estava documentada como se backend e frontend fossem um único MVC**, com
  a pasta `frontend/` no papel de "View". São duas aplicações, com stacks, builds e ciclos de
  vida separados. A mesma mistura contaminava Clean Code, Design Patterns e testes unitários,
  que apareciam como um conjunto único em vez de práticas atribuídas a cada stack.
- **As atividades do board não eram autocontidas.** O critério de aceite, a regra de negócio e
  a Definition of Done ficavam em `docs/` e a issue trazia apenas um link. Quem pegava a
  atividade precisava abrir dois ou três documentos e correlacionar à mão para saber o que
  fazer e quando parar.

## Decisão

### 1. Rebaseline do escopo para "MVP enxuto"

O escopo passa a ser **exatamente as 13 funcionalidades dos dois perfis do enunciado, mais
autenticação**. Nada além disso entra sem aprovação do PO em Planning.

**Mantido (14 User Stories, US-00 a US-13).** Autenticação; cadastro de especialidade, médico,
paciente e agenda pelo atendente; atualização dos próprios dados pelo paciente; consulta de
médicos, especialidades e horários livres; solicitação de consulta pelo paciente; agendamento
pelo atendente; visualização de consultas; cancelamento pelos dois perfis; confirmação e
finalização pelo atendente.

**Removido do MVP e registrado em [`15-melhorias-futuras.md`](Melhorias-Futuras):**

| Item | Por que sai |
|---|---|
| US-14 — Agenda geral consolidada da clínica | Não está na lista de funcionalidades do enunciado. Era classificada como *Desejável* |
| US-15 — Tela de cadastro de atendente | Não está na lista do enunciado. O primeiro atendente vem do seed (ADR-004), que é o suficiente para a demo. A RN14 continua valendo como regra |
| Edição e exclusão de especialidade | O enunciado pede "cadastrar especialidades", não gerenciá-las. CRUD completo é 4 telas a mais |
| Edição e inativação de médico | Mesma razão |
| Edição de paciente pelo atendente | O enunciado pede que **o paciente** atualize os próprios dados (US-04), e isso permanece |
| Exclusão de slot de horário livre | Não está no enunciado. Slot errado se resolve recriando a agenda |

**Autenticação permanece no MVP.** O enunciado exige dois perfis com permissões distintas; sem
login não há como demonstrar isso, e o backend de autenticação já está implementado e testado —
removê-lo seria descartar trabalho pronto e enfraquecer a demonstração.

**As 15 regras de negócio permanecem.** RN01 a RN06 são obrigatórias do enunciado; RN07 a RN15
já estão implementadas e testadas no backend, e nenhuma delas gera tela nova ou trabalho
adicional. Cortá-las reduziria a cobertura de teste sem economizar tempo.

### 2. Estratégia de entrega: fatias verticais completas

Cada User Story é entregue **ponta a ponta** — backend, frontend, teste unitário e caso de
teste executado — antes de a próxima começar. Se o prazo apertar, **corta-se a User Story
inteira**, não a metade frontend dela.

Motivo: o QA precisa de um fluxo navegável para executar caso de teste e sessão exploratória
com evidência. Meia dúzia de endpoints sem tela não produz evidência de teste, e evidência de
teste é entregável avaliado.

Ordem de corte, se necessário — de baixo para cima:

| Prioridade | User Stories | Justificativa |
|---|---|---|
| **P0 — não corta** | US-00, US-01, US-02, US-03, US-05, US-08, US-11 | Sem isso não há RN01–RN05 demonstrável |
| **P1** | US-07, US-09, US-12, US-13 | Completam a RN06 e o fluxo do atendente |
| **P2 — corta primeiro** | US-04, US-06, US-10 | Importantes, contornáveis na demonstração |

Nunca se corta: teste unitário de RN, evidência de caso de teste, ou o job `docker` do CI.

### 3. Documentação separada por aplicação

A partir daqui, todo documento que fala de código trata **backend e frontend como aplicações
distintas**:

| Documento | O que muda |
|---|---|
| [`03-arquitetura.md`](Arquitetura) | §2 é o MVC do backend; §3 é a arquitetura de componentes do frontend; §4 é o contrato de integração. A "View" do MVC passa a ser a camada de schemas Pydantic, não o app React |
| [`05-clean-code.md`](Clean-Code-e-SOLID) | Cada uma das 3 práticas exigidas é demonstrada **nas duas stacks**, com exemplo ruim/bom em Python e em TypeScript |
| [`06-design-patterns.md`](Design-Patterns) | Strategy e Repository são declarados explicitamente como padrões **do backend**. O que o frontend usa aparece em seção própria, sem competir pela contagem |
| [`07-plano-de-testes.md`](Plano-de-Testes) e [`08-casos-de-teste.md`](Casos-de-Teste) | Testes unitários separados por stack: pytest no backend, Vitest no frontend, com contagem própria |

**Por que a View do MVC virou os schemas Pydantic.** Numa API REST não existe template
renderizado no servidor. Chamar o app React de "View do MVC" sugere que o Controller o
preenche, o que é falso: o React tem roteamento, estado e build próprios, e apenas *consome* a
API. Adotamos a mesma leitura do Django REST Framework, onde o `Serializer` ocupa o papel da
View. Assim o MVC se fecha dentro de `backend/`, que é onde ele de fato existe, e o frontend é
documentado com o vocabulário correto dele.

### 4. Correção dos ADR-001 a ADR-007 no lugar

Os sete ADRs anteriores foram redigidos **em um único commit de 29/07**, antes do kickoff, e
nunca passaram por revisão da equipe. Eram rascunho, não registro de decisão vivida — e a regra
de imutabilidade existe para proteger história, não rascunho. Por isso foram **corrigidos no
lugar**, cada um com a data da revisão no cabeçalho.

| ADR | O que estava errado | Correção |
|---|---|---|
| **ADR-002** | *"Mapeamento para o MVC: **View** = `frontend/src/app/`"* — contradizia diretamente a §3 desta decisão e o `03-arquitetura.md` reescrito | A View do MVC passa a ser `backend/app/schemas/`. O app Next.js é documentado como segunda aplicação |
| **ADR-003** | Analisava uma frase do Wiki afirmando que médicos logariam por e-mail. O Wiki foi republicado em 30/07 e essa versão não existe mais — ninguém consegue conferir a fonte | Parágrafo removido. **A decisão permanece:** médico é entidade de cadastro, não usuário. Registrado como MF09 |
| **ADR-006** | Afirmava "20 testes unitários... medido, não estimado". São **17**, contados no código | Número corrigido |
| **ADR-001, 002, 004** | "2 semanas" como restrição de contexto | Trocado pelo prazo real (11 dias, até 10/08) |

O mesmo tratamento foi dado ao `14-conflitos-e-decisoes.md`: o conflito C05 foi reescrito para
apoiar-se em F1 e F2 (o enunciado, que continua verificável) em vez de uma citação do Wiki, e o
cabeçalho passou a avisar que a fonte F3 não está mais disponível.

**A partir do kickoff de 31/07, a imutabilidade vale integralmente.** Este ADR-008 é o primeiro
sob a regra: para revertê-lo, escreve-se um ADR-009.

### 5. Atividades do board autocontidas

Toda issue passa a trazer **dentro do próprio corpo**: contexto, critério de aceite completo,
texto integral das regras de negócio envolvidas, Definition of Done da área e como testar.
Links para `docs/` continuam existindo, mas apenas como **referência complementar** — nunca
como pré-requisito para entender a tarefa.

Os três templates de issue (`bug.yml`, `funcionalidade.yml`, `melhoria.yml`) foram alinhados a
esse princípio, com os campos de severidade e prioridade separados conforme a ISO/IEC 29119-3.

## Consequências

**Positivas**

- Board vai de 82 para **57 itens** (14 User Stories + 28 tarefas de código + 15 de processo),
  com chance real de terminar até 10/08.
- Quem pega uma atividade sabe o que fazer sem abrir outro documento.
- A defesa da arquitetura na apresentação fica mais forte: o MVC é apontado num lugar só, em
  código que existe, em vez de espalhado por duas stacks.
- O que foi cortado não se perde — vira backlog de evolução documentado, que é resposta
  pronta para a pergunta "e o que faltou?".

**Negativas**

- Descrições de issue ficam longas e há duplicação entre a issue e `docs/`. Se divergirem,
  **`docs/` é a fonte da verdade** e a issue é corrigida.
- Recriar o board fecha as issues anteriores. O histórico e a autoria são preservados: as
  issues são fechadas com justificativa em comentário, nunca apagadas.
- Perdemos a agenda geral da clínica, que era um bom material visual para a demonstração.

## Alternativas

| Alternativa | Por que não |
|---|---|
| Manter os 82 itens e aceitar entregar parte | Board majoritariamente em "To Do" na apresentação sugere planejamento ruim, não escopo ambicioso |
| Cortar também a autenticação | O enunciado exige dois perfis com permissões distintas; o código já existe e está testado |
| Manter a documentação unificada e só explicar na apresentação | A avaliação lê o repositório antes da apresentação; a documentação precisa se sustentar sozinha |
| Renumerar as User Stories depois do corte | Quebraria a rastreabilidade já escrita em casos de teste, ADRs e nomes de branch, sem ganho real |


---

> 📄 Esta página é gerada a partir de `docs/` no repositório. **Não edite aqui** — edite o arquivo correspondente e rode `scripts/publicar-wiki.sh`.
