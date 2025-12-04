# Análise RFV: Aplicação de Segmentação de Clientes
## Apresentação Técnica - Storytelling

---

## 📖 Seção 1: O Problema que Resolvemos

### A Jornada do Cliente no E-commerce

Imagine que você é gestor de uma empresa de e-commerce com milhares de clientes. Todos os dias, você recebe dados de transações: quem comprou, quando comprou, quanto gastou. Mas como transformar essa montanha de dados em ações estratégicas?

**O desafio:** Como identificar quais clientes são mais valiosos? Quem está em risco de churn? Quem tem potencial de crescimento? Como personalizar estratégias de marketing para cada perfil?

### A Solução: Análise RFV

A análise RFV (Recency, Frequency, Monetary Value) é uma metodologia clássica de segmentação de clientes que responde exatamente a essas perguntas. Nossa aplicação automatiza esse processo, transformando dados brutos em insights acionáveis.

---

## 🎯 Seção 2: O que é RFV e Por que Importa

### Os Três Pilares da Análise RFV

**R - Recency (Recência):** Quando foi a última compra do cliente?
- Clientes que compraram recentemente são mais engajados
- Quanto mais tempo desde a última compra, maior o risco de churn

**F - Frequency (Frequência):** Com que frequência o cliente compra?
- Clientes frequentes têm maior lifetime value
- Frequência indica lealdade e satisfação

**V - Monetary Value (Valor Monetário):** Quanto o cliente gasta?
- Identifica clientes de alto valor
- Ajuda a priorizar investimentos em marketing

### Por que RFV Funciona?

A combinação desses três fatores cria uma matriz de segmentação poderosa. Cada cliente recebe um score de 1 a 5 para cada dimensão, resultando em 125 combinações possíveis (5×5×5). Essas combinações são agrupadas em 9 segmentos estratégicos, cada um com um perfil comportamental distinto.

---

## 🏗️ Seção 3: Arquitetura da Aplicação

### Visão Geral: Arquitetura Cliente-Servidor

```
┌─────────────────┐         HTTP/REST         ┌─────────────────┐
│                 │ ◄──────────────────────► │                 │
│   Frontend      │                           │    Backend      │
│   (React)       │                           │   (FastAPI)     │
│                 │                           │                 │
│  - Interface    │                           │  - Processamento│
│  - Visualização │                           │  - Cálculos RFV │
│  - Upload CSV   │                           │  - Geração PDF  │
└─────────────────┘                           └─────────────────┘
```

### Stack Tecnológico

**Frontend:**
- **React + Vite:** Framework moderno para interface reativa
- **Tailwind CSS:** Estilização utilitária e responsiva
- **Recharts:** Visualizações interativas de dados
- **Axios:** Comunicação HTTP com o backend

**Backend:**
- **FastAPI:** Framework Python assíncrono e performático
- **Pandas:** Manipulação e análise de dados
- **NumPy:** Cálculos numéricos otimizados
- **ReportLab:** Geração de relatórios PDF profissionais

### Por que essa Stack?

- **React:** Componentização facilita manutenção e escalabilidade
- **FastAPI:** Performance comparável a Node.js/Go, com tipagem estática via Pydantic
- **Pandas:** Biblioteca padrão para análise de dados em Python
- **Arquitetura separada:** Permite escalar frontend e backend independentemente

---

## 🔄 Seção 4: Fluxo de Processamento de Dados

### Jornada Completa: Do CSV ao Insight

#### Etapa 1: Upload e Mapeamento
```
CSV Bruto → Upload → Mapeamento de Colunas
```
- Usuário faz upload de arquivo CSV
- Sistema detecta colunas automaticamente
- Usuário mapeia: ID Cliente, ID Transação, Data, Valor
- **Desafio técnico:** Parsing flexível de diferentes formatos de data

#### Etapa 2: Análise de Outliers
```
Dados → Detecção (Box Plot/IQR) → Tratamento
```
- Identifica valores atípicos usando método IQR (Interquartile Range)
- Visualização via Box Plot para decisão informada
- Tratamento: Manter, Winsorizar (limitar extremos), ou Remover
- **Por que importante:** Outliers distorcem cálculos de quintis e segmentação

#### Etapa 3: Cálculo RFV Dinâmico
```
Transações → Agregação por Cliente → Cálculo de Quintis → Scores RFV
```

**Processo detalhado:**

1. **Agregação:**
   - Agrupa transações por cliente
   - Calcula: última data de compra, total de compras, valor total gasto
   - Filtra últimos 12 meses (janela móvel)

2. **Cálculo de Quintis (Dinâmico):**
   ```python
   # Exemplo: Recência
   quintis = df['recencia_dias'].quantile([0.2, 0.4, 0.6, 0.8])
   # Resultado: [45, 90, 135, 180] dias
   ```
   - **Por que quintis?** Divide dados em 5 grupos iguais (20% cada)
   - **Por que dinâmico?** Cada base de dados tem distribuições diferentes
   - Adapta-se automaticamente ao perfil dos clientes

3. **Atribuição de Scores:**
   - **Recência:** Quanto maior o tempo, menor o score (1 = muito tempo, 5 = recente)
   - **Frequência:** Quanto mais compras, maior o score (1 = poucas, 5 = muitas)
   - **Valor:** Quanto mais gastou, maior o score (1 = pouco, 5 = muito)

#### Etapa 4: Segmentação Inteligente
```
Scores RFV → Regras de Negócio → 9 Segmentos
```

**Lógica de Priorização:**
- Cliente pode se encaixar em múltiplos segmentos
- Sistema aplica regras em ordem de prioridade (código 1 a 9)
- **Menor código sempre vence** (ex: NOVOS tem prioridade sobre CAMPEÃO)

**Os 9 Segmentos:**
1. **NOVOS** - Primeira compra nos últimos 60 dias
2. **CAMPEÃO** - R=5, F≥3, V=5 (clientes ideais)
3. **LEAIS** - R=3 ou 4, média F+V≥3
4. **POTENCIAIS** - Alto valor, baixa frequência
5. **PROMISSORES** - Recentes, mas baixo engajamento
6. **HIBERNANDO** - R=2, média F+V<4
7. **PREOCUPANTES** - R=2, média F+V≥4 (risco de churn)
8. **RISCO** - R=1, média F+V<4 (churn provável)
9. **NÃO PODEMOS PERDER** - R=1, média F+V≥4 (recuperação urgente)

---

## 📊 Seção 5: Features Principais

### 1. Dashboard Interativo

**KPIs em Tempo Real:**
- Total de Clientes
- Receita Total (12 meses)
- Distribuição por Segmento (tabela e gráficos)

**Visualizações:**
- Gráfico de barras por segmento
- Gráfico de pizza (percentuais)
- Tabela detalhada com preview dos dados

### 2. Análise de Outliers com Box Plot

**Tecnicamente:**
- Cálculo de IQR: `Q3 - Q1`
- Limites: `Q1 - 1.5×IQR` e `Q3 + 1.5×IQR`
- Visualização interativa para decisão informada
- Três estratégias de tratamento

### 3. Processamento RFV Automatizado

**Algoritmo:**
1. Normalização de datas (múltiplos formatos)
2. Agregação eficiente com Pandas (groupby)
3. Cálculo de quintis dinâmicos (quantile)
4. Aplicação de funções de scoring (vectorized)
5. Segmentação com regras condicionais (apply)

**Performance:**
- Processa milhares de transações em segundos
- Otimizado com operações vetorizadas do Pandas
- Sem loops Python puros (usa NumPy/Pandas nativo)

### 4. Geração de Relatórios PDF

**Conteúdo do Relatório:**
- Conceitos RFV explicados
- Tabelas com intervalos dinâmicos (quintis calculados)
- Estatísticas gerais
- Distribuição por segmento
- Definições detalhadas de cada segmento

**Tecnologia:**
- ReportLab para geração programática
- Layout profissional com cores e estilos
- Tabelas formatadas automaticamente

### 5. Download de Resultados

- CSV processado com scores e segmentos
- PDF completo com análise
- Dados prontos para importação em outras ferramentas

---

## 🎨 Seção 6: Decisões de Design Técnico

### Por que FastAPI?

1. **Performance:** Assíncrono nativo, comparável a Node.js
2. **Tipagem:** Validação automática com Pydantic
3. **Documentação:** Swagger/OpenAPI automático
4. **Moderno:** Suporta async/await, WebSockets, etc.

### Por que React?

1. **Componentização:** Código reutilizável e manutenível
2. **Estado Reativo:** UI atualiza automaticamente
3. **Ecossistema:** Bibliotecas maduras (Recharts, Axios)
4. **Developer Experience:** Hot reload, ferramentas de debug

### Por que Quintis Dinâmicos?

**Problema:** Bases diferentes têm distribuições diferentes
- Base A: Clientes gastam R$ 50-500
- Base B: Clientes gastam R$ 500-5000

**Solução:** Quintis adaptam-se aos dados
- Base A: Quintis em R$ 100, 200, 300, 400
- Base B: Quintis em R$ 1000, 2000, 3000, 4000

**Resultado:** Segmentação justa e relevante para cada contexto

### Por que Segmentação com Prioridade?

**Cenário:** Cliente com R=5, F=5, V=5, primeira compra há 30 dias
- Se encaixa em: NOVOS (código 1) e CAMPEÃO (código 2)
- **Solução:** Menor código vence → NOVOS

**Lógica:** Cliente novo precisa de estratégia diferente, mesmo sendo valioso

---

## 🚀 Seção 7: Fluxo de Uso da Aplicação

### Passo a Passo Técnico

1. **Inicialização:**
   ```bash
   # Backend
   cd backend
   python main.py  # Inicia servidor FastAPI na porta 8000
   
   # Frontend
   cd frontend
   npm run dev  # Inicia servidor Vite na porta 5173
   ```

2. **Upload de Dados:**
   - Usuário seleciona arquivo CSV
   - Frontend envia via `multipart/form-data` para `/upload`
   - Backend salva temporariamente e retorna `file_id`

3. **Mapeamento:**
   - Frontend lê cabeçalhos do CSV
   - Usuário mapeia colunas via interface
   - Dados são validados no backend

4. **Análise de Outliers:**
   - Backend calcula estatísticas (IQR, limites)
   - Frontend exibe Box Plot via Recharts
   - Usuário escolhe tratamento
   - Decisão enviada para `/analyze-outliers`

5. **Processamento RFV:**
   - Backend executa pipeline completo:
     - Tratamento de outliers
     - Agregação por cliente
     - Cálculo de quintis
     - Atribuição de scores
     - Segmentação
   - Resultados salvos em CSV temporário
   - Quintis salvos em JSON separado

6. **Visualização:**
   - Frontend recebe estatísticas e preview
   - Renderiza dashboard com gráficos
   - Exibe tabela de distribuição

7. **Download:**
   - CSV: `/download/{file_id}` retorna arquivo processado
   - PDF: `/generate-pdf/{file_id}` gera relatório completo

---

## 🔧 Seção 8: Detalhes Técnicos de Implementação

### Tratamento de Dados

**Parsing de Datas:**
```python
# Suporta múltiplos formatos
pd.to_datetime(df['data'], format='mixed', dayfirst=True)
```
- Detecta automaticamente formato (DD/MM/YYYY, YYYY-MM-DD, etc.)
- Trata timezone e horários

**Agregação Eficiente:**
```python
df_agg = df.groupby('id_cliente').agg({
    'data': 'max',           # Última compra
    'id_transacao': 'count',  # Frequência
    'valor': 'sum'            # Valor total
})
```
- Operação vetorizada (rápida)
- Evita loops Python

**Cálculo de Quintis:**
```python
quintis = df['coluna'].quantile([0.2, 0.4, 0.6, 0.8])
```
- Usa algoritmo eficiente (O(n log n))
- Retorna 4 valores que dividem dados em 5 grupos iguais

### Segmentação com Regras Condicionais

**Estratégia:**
- Função `segmentar_cliente()` aplicada a cada linha
- Avalia condições em ordem de prioridade
- Retorna segmento assim que encontra match

**Otimização:**
- Usa `df.apply()` (mais legível que loops)
- Considera usar `np.select()` para performance em bases muito grandes

### Geração de PDF

**Estrutura:**
- ReportLab cria documento programaticamente
- Usa `SimpleDocTemplate` para layout
- `Table` para tabelas formatadas
- `Paragraph` para texto com formatação HTML

**Desafio:**
- Quintis dinâmicos inseridos no texto
- Formatação de números (moeda, decimais)
- Quebra de página automática

---

## 📈 Seção 9: Casos de Uso e Valor de Negócio

### Para Marketing

**Segmentação de Campanhas:**
- **CAMPEÃO:** Programa de fidelidade, upsell
- **PROMISSORES:** Campanhas de reativação, desconto
- **NÃO PODEMOS PERDER:** Recuperação urgente, ofertas especiais

### Para Vendas

**Priorização:**
- Focar em clientes de alto valor (V=5)
- Identificar oportunidades (POTENCIAIS)
- Evitar desperdício em clientes de baixo valor

### Para Análise

**Insights:**
- Distribuição de clientes por perfil
- Identificação de tendências (crescimento de segmentos)
- Análise de churn (segmentos RISCO, PREOCUPANTES)

---

## 🎯 Seção 10: Conclusão e Próximos Passos

### O que Construímos

Uma aplicação completa de análise RFV que:
- ✅ Processa dados brutos automaticamente
- ✅ Adapta-se a diferentes bases (quintis dinâmicos)
- ✅ Fornece insights acionáveis (9 segmentos)
- ✅ Gera relatórios profissionais (PDF)
- ✅ Interface intuitiva (React + Tailwind)

### Tecnologias Modernas

- **Backend:** FastAPI (Python assíncrono)
- **Frontend:** React + Vite (JavaScript moderno)
- **Dados:** Pandas + NumPy (análise eficiente)
- **Visualização:** Recharts (gráficos interativos)

### Possíveis Melhorias Futuras

1. **Machine Learning:** Previsão de churn baseada em RFV
2. **Real-time:** Atualização automática de segmentos
3. **Multi-tenant:** Suporte a múltiplas empresas
4. **API Externa:** Integração com CRMs, ERPs
5. **Histórico:** Tracking de mudanças de segmento ao longo do tempo

---

## 📚 Glossário Técnico

- **RFV:** Recency, Frequency, Monetary Value
- **IQR:** Interquartile Range (método de detecção de outliers)
- **Quintis:** Divisão de dados em 5 grupos iguais (20% cada)
- **Churn:** Perda de clientes
- **Lifetime Value:** Valor total que cliente gera ao longo do tempo
- **Vectorization:** Operações em arrays (mais rápidas que loops)

---

## 🎬 Finalização

Esta aplicação representa a união de **análise de dados clássica** com **tecnologias modernas**, criando uma ferramenta poderosa para tomada de decisão baseada em dados.

**O diferencial:** Não é apenas uma calculadora RFV, é um sistema completo que vai desde o upload de dados até a geração de relatórios profissionais, tudo com uma interface intuitiva e código manutenível.

**O resultado:** Transformar dados em estratégia, números em ações, e clientes em oportunidades.

---

*Desenvolvido com FastAPI, React, Pandas e muito café ☕*

