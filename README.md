# 🏥 Sistema de Gestão de Clínica Médica (MVP)

---

## 👥 Equipe e Papéis

Nossa equipe foi dividida para cobrir todo o ciclo de vida do desenvolvimento de software:

*   👑 **Product Owner (PO):** Uanderson Henrique
*   💻 **Engenharia de Software:** Ronaldo de Melo, Jonatha da Silva, João Vitor, Antonio Andrade
*   🧪 **Quality Assurance (QA):** Jackson Douglas, Felipe da Silva

---

## 🛠️ Tecnologias Utilizadas

*   **Backend:** 
*   **Frontend:** React com TypeScript
*   **Banco de Dados:** 
*   **Integração Contínua (CI):** GitHub Actions
*   **Testes:** 

---

## 🏗️ Arquitetura e Engenharia

O projeto foi estruturado utilizando o padrão **MVC (Model-View-Controller)** para separar as regras de negócio da interface e do controle de fluxo.

### Padrões de Projeto (Design Patterns)
1.  **[NOME DO PADRÃO 1 ]:**
2.  **[NOME DO PADRÃO 2]:** 

### Práticas de Clean Code Aplicadas
1.  **[NOME DO Prática 1]:**.
2.  **[NOME DO Prática 2]:**.
3.  **[NOME DO Prática 3]:**.

---

## ✨ Funcionalidades (Requisitos Funcionais)

O sistema possui dois perfis de acesso distintos, cada um com suas próprias permissões e jornadas:

### 👤 Perfil: Paciente
*   Atualizar seus dados cadastrais.
*   Consultar médicos disponíveis.
*   Consultar especialidades oferecidas pela clínica.
*   Visualizar horários disponíveis para agendamento.
*   Visualizar o agendamento de uma consulta específica.
*   Visualizar o histórico e a lista de suas consultas.
*   Cancelar uma consulta (respeitando as regras de antecedência).

### 👩‍💻 Perfil: Atendente
*   Cadastrar novos pacientes.
*   Cadastrar médicos no sistema.
*   Cadastrar especialidades médicas.
*   Cadastrar horários disponíveis para os médicos.
*   Cadastrar (agendar) consultas para os pacientes.
*   Cadastrar e gerenciar a agenda geral.
*   Cancelar consultas.

---

## 📋 Regras de Negócio Implementadas

O MVP garante a integridade da clínica através das seguintes regras obrigatórias:

*   **RN01 (CPF):** Bloqueio de cadastro de pacientes com o mesmo CPF.
*   **RN02 (E-mail):** Bloqueio de usuários duplicados com o mesmo e-mail.
*   **RN03 (Horário):** Impedimento de reserva de horários já ocupados.
*   **RN04 (Cancelamento):** Cancelamento restrito a pedidos com no mínimo 24h de antecedência.
*   **RN05 (Agenda):** Bloqueio de alocação dupla para o mesmo médico no mesmo horário.
*   **RN06 (Status):** Gestão rigorosa dos status das consultas (SOLICITADA, CONFIRMADA, CANCELADA, FINALIZADA).

---

## 🧪 Testes e Qualidade (QA)

---

## 📚 Documentação Completa (Wiki)

A documentação detalhada do projeto foi construída na **Wiki do GitHub**. Lá você encontrará:
*   Histórias de Usuário e Critérios de Aceite.
*   Detalhamento do Plano de Testes.
*   Documentação aprofundada da Arquitetura.


---

## 🚀 Como executar o projeto localmente

Siga os passos abaixo para rodar a aplicação na sua máquina:

