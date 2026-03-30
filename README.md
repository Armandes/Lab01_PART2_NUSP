# Lab01-B — Ingestão de Dados End-to-End Containerizada

**Aluno:** João Armandes Vieira Costa  
**Disciplina:** Engenharia de Dados — Pós-Graduação  
**Dataset:** [Gaming and Mental Health](https://www.kaggle.com) — 1.000.000 linhas × 39 colunas

---

## Arquitetura
```
CSV Original → Bronze (Raw) → Silver (Parquet) → Gold (PostgreSQL) → Metabase (BI)
```

### Infraestrutura Docker
```
docker-compose
├── container: lab01_postgres    → banco de dados PostgreSQL
├── container: lab01_pipeline    → scripts Python de ingestão
└── container: lab01_metabase    → dashboard de BI
        ↕               ↕               ↕
                lab01_network
              (rede Docker interna)
```

### Fluxo completo
```
[CSV Original]
      ↓
[Bronze] scripts/01_bronze.py
      ↓ data/raw/
[Silver] data/silver/cleaning.py + graphics.py
      ↓ data/silver/dataset_clean.parquet
[Validação] scripts/06_great_expectations.py
      ↓ relatório HTML
[Gold] data/gold/carga.py
      ↓ PostgreSQL (container Docker)
[BI] Metabase → localhost:3000
```

| Camada | Objetivo | Saída |
|--------|----------|-------|
| Bronze | Ingestão as-is, sem alterações | `data/raw/` + log |
| Silver | Limpeza, padronização e análise exploratória | `data/silver/*.parquet` |
| Gold | Modelagem Star Schema e carga no PostgreSQL | Tabelas no banco `lab01` |
| BI | Dashboard com 5 visualizações | Metabase em `localhost:3000` |

---

## Estrutura do Projeto
```
Lab01_PART2_NUSP/
├── data/
│   ├── raw/                        # CSV original + log de ingestão
│   ├── silver/
│   │   ├── check.py                # Verificação geral dos dados
│   │   ├── cleaning.py             # Limpeza e geração do Parquet
│   │   ├── graphics.py             # Gráficos e relatório Markdown
│   │   ├── dataset_clean.parquet   # Dataset limpo
│   │   └── graficos/               # Imagens dos gráficos
│   └── gold/
│       ├── carga.py                # Modelagem Star Schema + carga no Postgres
│       └── metricas.py             # 5 queries de métricas de negócio
├── scripts/
│   ├── 01_bronze.py                # Ingestão Bronze
│   └── 06_great_expectations.py    # Validação de dados
├── Dockerfile                      # Imagem do pipeline Python
├── docker-compose.yml              # Orquestração dos containers
├── pyproject.toml                  # Dependências do projeto (uv)
├── uv.lock                         # Versões travadas das dependências
├── .env                            # Credenciais do banco (não commitado)
├── .gitignore
└── README.md
```

---

## Pré-requisitos

- [Docker](https://www.docker.com/products/docker-desktop) instalado
- [uv](https://astral.sh/uv) instalado

### Instalar dependências localmente
```bash
uv sync
```

---

## Como Reproduzir o Ambiente

### 1. Clonar o repositório
```bash
git clone https://github.com/seu-usuario/Lab01_PART2_NUSP.git
cd Lab01_PART2_NUSP
```

### 2. Configurar o arquivo `.env`
Cria um arquivo `.env` na raiz do projeto:
```
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/lab01
```

### 3. Construir e subir os containers
```bash
docker-compose up -d --build
```

### 4. Verificar os containers
```bash
docker-compose ps
```

Os seguintes containers devem estar rodando:

| Container | Imagem | Porta |
|-----------|--------|-------|
| lab01_postgres | postgres:15 | 5432 |
| lab01_pipeline | imagem local (Dockerfile) | — |
| lab01_metabase | metabase/metabase:latest | 3000 |

### 5. Parar os containers
```bash
docker-compose down
```

---

## Ordem de Execução dos Scripts
```bash
# 1. Camada Bronze — verifica o CSV e gera log
python scripts/01_bronze.py

# 2. Camada Silver — checagem geral dos dados
python data/silver/check.py

# 3. Camada Silver — limpeza e geração do Parquet
python data/silver/cleaning.py

# 4. Camada Silver — gráficos e relatório Markdown
python data/silver/graphics.py

# 5. Camada Gold — carga no PostgreSQL em Star Schema
python data/gold/carga.py

# 6. Camada Gold — métricas de negócio
python data/gold/metricas.py

# 7. Validação de dados com Great Expectations
python scripts/06_great_expectations.py
```

> As etapas devem ser executadas **nessa ordem** — cada etapa depende da anterior.

---

## Great Expectations — Validação de Dados

### Como executar
```bash
python scripts/06_great_expectations.py
```

### Expectativas implementadas

| # | Expectativa | Coluna |
|---|-------------|--------|
| 1 | Valores não nulos | age, gender, anxiety_score, depression_score |
| 2 | Valores entre 0 e 10 | anxiety_score, depression_score, happiness_score, stress_level, addiction_level |
| 3 | Valores válidos | gender (Male, Female, Other) |
| 4 | Valores entre 0 e 24 | daily_gaming_hours |
| 5 | Total de linhas entre 100.000 e 2.000.000 | — |

### Problema de qualidade identificado

| Coluna | Problema | Ação |
|--------|----------|------|
| daily_gaming_hours | Valores acima de 24h encontrados — fisicamente impossível | Documentado como problema de qualidade. Recomenda-se filtrar na camada Silver em versões futuras. |

---

## Dashboard — Metabase

Após subir os containers, acessa em: `http://localhost:3000`
Dashboard com painéis criados: '[http://localhost:3000/dashboard/2-atividade-lab01-b](url)'

Credenciais de conexão usadas internamente pelo Metabase:

| Campo | Valor |
|-------|-------|
| Host | postgres |
| Port | 5432 |
| Database | lab01 |
| Username | postgres |
| Password | postgres |

### Visualizações criadas
1. Depressão por faixa etária
2. Depressão por gênero
3. Usa headset?
4. Renda média por faixa etária
5. Trabalhadores por faixa etária
6. Influência de café no sono

---

## Modelagem — Star Schema

| Tabela | Tipo | Descrição |
|--------|------|-----------|
| fato_saude_mental | Fato | Métricas de saúde mental |
| dim_jogador | Dimensão | Perfil demográfico |
| dim_habitos | Dimensão | Hábitos de jogo e rotina |
| dim_comportamento | Dimensão | Comportamento online |
| dim_social | Dimensão | Vida social |

---

## Dificuldades Encontradas

- Configuração da rede Docker para comunicação entre containers
- API do Great Expectations mudou na versão 1.x — necessário adaptar o script
- Valores inconsistentes em `daily_gaming_hours` (acima de 24h) identificados pelo GX
- Organização das pastas entre Lab01-A e Lab01-B durante o desenvolvimento
