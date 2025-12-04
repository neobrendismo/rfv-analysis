
````markdown
# Análise RFV - Aplicação Web Completa 🛍️

Aplicação web completa para análise de **RFV** (Recência, Frequência, Valor Monetário) com backend em [Python](https://www.python.org/)/[FastAPI](https://fastapi.tiangolo.com/) e frontend em [React](https://react.dev/).

**## Tecnologias**

| Área | Tecnologia | Versão/Detalhe |
| :--- | :--- | :--- |
| **Backend** | Python 3.10+ | - |
| **Backend** | FastAPI | Framework Web |
| **Backend** | Pandas | Manipulação de Dados |
| **Backend** | NumPy | Computação Numérica |
| **Frontend** | React 18 | - |
| **Frontend** | Vite | Tooling |
| **Frontend** | Tailwind CSS | Estilização |
| **Frontend** | Recharts | Gráficos |
| **Frontend** | Axios | Requisições HTTP |

**## Requisitos**

Para rodar a aplicação, você precisa ter instalado:
* **Python 3.10** ou superior (Baixe [aqui](https://www.python.org/))
* **Node.js 18** ou superior (Baixe [aqui](https://nodejs.org/en))
* **npm** ou **yarn**

**## Início Rápido**

**### Método Automático (Recomendado)**

Basta **clicar duas vezes** no arquivo `iniciar_aplicacao.bat` (somente para Windows).

> ℹ️ Isso iniciará automaticamente o backend e o frontend em janelas separadas.

**### Método Manual**

Siga os passos abaixo em terminais separados para o Backend e Frontend.

**Backend:**
```bash
# 1. Entre na pasta do backend
cd backend
# 2. Instale as dependências (somente na primeira vez)
pip install -r requirements.txt
# 3. Inicie o servidor
python main.py
````

**Frontend:**

```bash
# 1. Entre na pasta do frontend
cd frontend
# 2. Instale as dependências (somente na primeira vez)
npm install
# 3. Inicie a aplicação em modo desenvolvimento
npm run dev
```

**Acesse a aplicação no navegador:**
👉 [http://localhost:5173](https://www.google.com/search?q=http://localhost:5173)

**\#\#\# Parar a Aplicação**

  * **Clique duas vezes** em `parar_aplicacao.bat` (Windows)
  * Ou pressione `Ctrl + C` nos terminais onde os processos estão rodando.

**\#\# Como Usar**

1.  **Upload de Arquivo CSV** - Faça upload de um arquivo CSV com dados de transações.
2.  **Mapeamento de Colunas** - Selecione as colunas correspondentes (**ID Cliente, Data, Valor**, etc.) na interface.
3.  **Análise de Outliers** - Visualize e escolha como tratar valores extremos.
4.  **Dashboard** - Visualize os resultados da segmentação, gráficos e baixe o **CSV/PDF** processado.

**\#\# Regras de Segmentação RFV**

**Nota:** Os intervalos de **Recência**, **Frequência** e **Valor** são calculados dinamicamente usando **quintis** da base de dados analisada.

**\#\#\# Scores**

| Score | Descrição | Base de Cálculo |
| :--- | :--- | :--- |
| **Recência (R)** | Dias desde a última compra. | Quintis dos dias. |
| **Frequência (F)** | Quantidade de compras (últimos 12 meses). | Quintis da quantidade. |
| **Valor Monetário (V)** | Valor total gasto (últimos 12 meses). | Quintis do valor. |

**\#\#\# Segmentos**

| Segmento | Regra | R | F | V | Detalhe |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **NOVOS** | 1ª compra nos últimos 60 dias | - | - | - | Não são pontuados com R, F, V. |
| **CAMPEÃO** | R=5, F≥3, V=5 | 5 | ≥3 | 5 | Clientes mais valiosos. |
| **LEAIS** | R=3/4, Média(F+V)≥3 | 3/4 | ≥3 | - | Compram regularmente. |
| **POTENCIAIS** | (R=5, Média≥3, V≥3) OU (R=4, Média≥2, V=3/4) | 5 ou 4 | ≥3 ou ≥2 | ≥3 ou 3/4 | Alto potencial. |
| **PROMISSORES** | R≥4, Média≥2, Média\<3 | ≥4 | ≥2 | ≥2 | Recentes, mas precisam de mais F/V. |
| **HIBERNANDO** | R=2, Média \< 4 | 2 | \<4 | \<4 | Risco de se tornarem inativos. |
| **PREOCUPANTES** | R=2, Média ≥ 4 | 2 | ≥4 | ≥4 | Não compram há um tempo, mas eram bons clientes. |
| **RISCO** | R=1, Média \< 4 | 1 | \<4 | \<4 | Clientes inativos e de baixo valor. |
| **NAO\_PODEMOS\_PERDER** | R=1, Média ≥ 4 | 1 | ≥4 | ≥4 | Clientes valiosos que estão inativos. |

**\#\# Estrutura do Projeto**

```
RFV_2/
├── backend/
│   ├── main.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── UploadArea.jsx
│   │   │   ├── ColumnMapper.jsx
│   │   │   ├── OutlierSettings.jsx
│   │   │   ├── BoxPlot.jsx
│   │   │   └── Dashboard.jsx
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   └── index.css
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   └── postcss.config.js
└── README.md
```

**\#\# Endpoints da API**

| Método | Endpoint | Descrição |
| :--- | :--- | :--- |
| `POST` | `/upload` | Upload de arquivo CSV para processamento. |
| `POST` | `/analyze-outliers` | Análise e visualização de valores extremos (outliers). |
| `POST` | `/process-rfv` | Execução do cálculo e segmentação RFV. |
| `GET` | `/download/{file_id}` | Download do CSV processado com scores e segmentos. |
| `GET` | `/generate-pdf/{file_id}` | Download do relatório PDF completo. |

**\#\# Formato do CSV**

O arquivo CSV de entrada deve conter as seguintes colunas. Os nomes das colunas podem ser flexíveis, pois serão mapeados na interface:

  * **ID do Cliente**
  * **ID da Transação**
  * **Data** (formato flexível, será detectado automaticamente)
  * **Valor Monetário**

**\#\# Troubleshooting**

### Porta 8000 ocupada (Backend)

Se o servidor backend (FastAPI) não iniciar por causa da porta 8000:

```bash
# 1. Encontre o processo que está usando a porta
netstat -ano | findstr :8000
# 2. Encerre o processo (substitua <PID> pelo número encontrado)
taskkill /F /PID <PID>
# 3. Ou use o script dedicado (Windows)
# backend/start_server.bat
```

### Dependências não instaladas

Verifique se as dependências do ambiente foram instaladas:

```bash
# Backend
cd backend
pip install -r requirements.txt

# Frontend
cd frontend
npm install
```

### Erro de política PowerShell

Se encontrar problemas de execução de scripts no PowerShell:

  * Use o arquivo `frontend/start_frontend.cmd` (clique duas vezes).
  * Ou utilize o **Prompt de Comando (CMD)** em vez do PowerShell para rodar os comandos manuais.

**\#\# Licença**

Este projeto é de código aberto e está disponível para uso livre.

