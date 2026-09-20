# Antigravity: Na secao atendimento e ia, no card de resposta media, pode f... (2026-09-08)

---
id: "ba381bf1-46f0-41ef-95c8-1330f24fe207"
type: "event"
workspace: "workspace1"
source_channel: "ai-chat"
source_system: "antigravity"
event_type: "manual_note"
project: "elogroup-bootcamp"
kind: "note"
canonical_type: "event"
importance: "low"
status: "active"
tags: []
occurred_at: "2026-09-08T13:52:53.599Z"
related: []
---

# Antigravity: Na secao atendimento e ia, no card de resposta media, pode f... (2026-09-08)
Project: EloGroup_Bootcamp
Source: Antigravity

---

### 👤 User
Na secao atendimento e ia, no card de resposta media, pode fazer alguma observacao considerando a mediana? qual é?

### ✨ Assistant
Sim, a análise da **mediana** é fundamental aqui porque a métrica de **média (135 min / ~2h15)** mascara completamente o comportamento real da operação devido a uma forte assimetria por canal.

---

### 1. Qual é o valor da Mediana?
* **Mediana Geral de 1ª Resposta:** **`11,0 minutos`**
* **Média Geral de 1ª Resposta:** **`135,4 minutos`** (aproximadamente 2h 15min)

---

### 2. Por que a Mediana é tão diferente da Média? (Diagnóstico)

A distribuição dos tempos de resposta é **bimodal** e dividida rigidamente pelo canal de atendimento:

| Canal de Entrada | % do Volume | Total Tickets | Mediana de Resposta | Média de Resposta | Comportamento |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **ChatBot** | 20,0% | 7.170 | **1 min** | 1,5 min | Resposta instantânea |
| **WhatsApp** | 35,3% | 12.651 | **8 min** | 8,5 min | Resposta ágil (< 15 min) |
| **Telefone** | 11,6% | 4.160 | **11 min** | 11,5 min | Fila curta (< 20 min) |
| **E-mail** | 24,9% | 8.930 | **269 min (~4,5h)** | 269,6 min | Fila assíncrona longa |
| **Reclame Aqui** | 8,2% | 2.929 | **782 min (~13h)** | 778,3 min | Crítico / Cauda longa (até 24h) |

---

### 3. Observações de Negócio e Impacto

1. **A Média distorce a experiência do cliente:**
   - **66,9% dos clientes** (WhatsApp + ChatBot + Telefone) são atendidos em **até 11 minutos** (mediana).
   - Dizer ao C-Level que a resposta média é de 2h15 passa a falsa impressão de que a equipe de linha de frente é lenta, quando na verdade **a maioria esmagadora é atendida com rapidez**.

2. **O gargalo está isolado nos canais assíncronos:**
   - O tempo médio é puxado quase que exclusivamente por **E-mail (4,5h)** e **Reclame Aqui (13h)**.

---

### 4. Sugestão de Observação para o Card

No card do dashboard (`1ª Resposta Média`), podemos enriquecer a informação com:

> **Valor Principal:** `135 min (Média)`  
> **Subtítulo / Tooltip:** `Mediana de 11 min • 67% dos chamados via WhatsApp/ChatBot respondidos em < 15 min (média inflada por E-mail ~4,5h e Reclame Aqui ~13h)`

Deseja que atualizemos o card na interface [`frontend/src/components/views/SupportView.tsx`](file:///home/pedroduarte/Documents/GitHub/EloGroup_Bootcamp/frontend/src/components/views/SupportView.tsx) e na query SQL para exibir a mediana diretamente?

### 👤 User
sim

### ✨ Assistant
Atualização implementada com sucesso.

### Alterações Realizadas:

1. **Consulta SQL (`src/queries/atendimento/kpis_atendimento.sql`)**:
   - Adicionada a métrica `MEDIAN(tempo_primeira_resposta_minutos) AS tempo_resposta_mediana_min` via DuckDB.

2. **Tipagens Frontend (`frontend/src/types/analytics.ts`)**:
   - Atualizada a interface `SupportAnalyticsData.kpis` com o campo `tempo_resposta_mediana_min`.

3. **Interface Visual (`frontend/src/components/views/SupportView.tsx`)**:
   - **Card de 1ª Resposta**:
     - **Valor principal**: `135 min` (Média)
     - **Badge/Trend**: `Mediana: 11 min` (em destaque verde)
     - **Subtítulo**: `Mediana: 11 min (67% < 15m)`
     - **Tooltip / Help explicativo**: Detalha que a média é inflada pelos canais assíncronos (*E-mail ~4,5h* e *Reclame Aqui ~13h*), enquanto a operação síncrona (*WhatsApp* e *ChatBot*) responde a maioria dos chamados em menos de 15 minutos.