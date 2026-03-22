# Lab01 — Ingestão de Dados End-to-End (Local)

**Aluno:** João Armandes Vieira Costa  
**Disciplina:** Engenharia de Dados — Pós-Graduação  
**Dataset:** [Gaming and Mental Health](https://www.kaggle.com/datasets/sharmajicoder/gaming-and-mental-health?resource=download) — 1.000.000 linhas × 39 colunas

---

## Arquitetura — Medallion Architecture
```
CSV Original → Bronze (Raw) → Silver (Parquet) → Gold (PostgreSQL)
```

| Camada | Objetivo | Saída |
|--------|----------|-------|
| Bronze | Ingestão as-is, sem alterações | `data/raw/` + log |
| Silver | Limpeza, padronização e análise exploratória | `data/silver/*.parquet` |
| Gold | Modelagem Star Schema e carga no PostgreSQL | Tabelas no banco `lab01` |

---

## Pré-requisitos

### Dependências
```bash
pip install pandas seaborn matplotlib pyarrow sqlalchemy python-dotenv psycopg2-binary
```

| Biblioteca | Uso |
|------------|-----|
| pandas | Manipulação e limpeza dos dados |
| seaborn / matplotlib | Geração de gráficos |
| pyarrow | Leitura e escrita do formato Parquet |
| sqlalchemy | Conexão e operações no PostgreSQL |
| python-dotenv | Leitura do arquivo `.env` |
| psycopg2-binary | Driver PostgreSQL para o SQLAlchemy |

### Configuração do banco
1. Instale o PostgreSQL localmente
2. Crie o banco de dados:
```sql
CREATE DATABASE lab01;
```
3. Crie o arquivo `.env` na raiz do projeto:
```
DATABASE_URL=postgresql://postgres:SUA_SENHA@localhost:5432/lab01
```

> O arquivo `.env` está no `.gitignore` e nunca deve ser commitado.

---

## Estrutura do Projeto
```
Lab01_PART1_NUSP/
├── data/
│   ├── raw/                        # CSV original + log de ingestão
│   ├── silver/
│   │   ├── dataset_clean.parquet   # Dataset limpo
│   │   ├── relatorio_graficos.md   # Relatório com gráficos
│   │   └── graficos/               # Imagens dos gráficos
│   └── gold/                       # (referência — dados ficam no Postgres)
├── scripts/
│   └── 01_bronze.py                # Ingestão Bronze
├── data/silver/
│   ├── check.py                    # Verificação geral dos dados
│   ├── cleaning.py                 # Limpeza e geração do Parquet
│   └── graphics.py                 # Gráficos e relatório Markdown
├── data/gold/
│   ├── carga.py                    # Modelagem Star Schema + carga no Postgres
│   └── metricas.py                 # 5 queries de métricas de negócio
├── .env                            # Credenciais do banco (não commitado)
├── .gitignore
├── requirements.txt
└── README.md
```

---

## Ordem de Execução
```bash
# 1. Camada Bronze — verifica o CSV e gera log
python scripts/01_bronze.py

# 2. Camada Silver — checagem geral dos dados
python data/silver/check.py

# 3. Camada Silver — limpeza e geração do Parquet
python data/silver/cleaning.py

# 4. Camada Silver — gráficos e relatório Markdown (requer o Parquet)
python data/silver/graphics.py

# 5. Camada Gold — carga no PostgreSQL em Star Schema
python data/gold/carga.py

# 6. Camada Gold — execução das métricas de negócio
python data/gold/metricas.py
```

> As etapas devem ser executadas **nessa ordem** — cada etapa depende da anterior.

---

## Modelagem — Star Schema

O modelo adotado é o **Star Schema**, com uma tabela fato central e quatro tabelas de dimensão. O `player_id` é a chave primária (PK) em todas as tabelas.
```
          dim_comportamento
                 |
dim_jogador — fato_saude_mental — dim_habitos
                 |
            dim_social
```

### Tabela fato — `fato_saude_mental`
Contém as métricas numéricas de saúde mental de cada jogador.

| Coluna | Descrição |
|--------|-----------|
| player_id | Chave estrangeira (FK) para as dimensões |
| stress_level | Score de estresse |
| anxiety_score | Score de ansiedade |
| depression_score | Score de depressão |
| addiction_level | Nível de vício em jogos |
| happiness_score | Score de felicidade |
| aggression_score | Score de agressividade |
| academic_performance | Score de performance acadêmica |
| work_productivity | Score de produtividade no trabalho |
| eye_strain_score | Score de cansaço ocular |
| back_pain_score | Score de dor nas costas |

### Dimensão — `dim_jogador`
Perfil demográfico do jogador.

| Coluna | Descrição |
|--------|-----------|
| player_id | Chave primária (PK) |
| age | Idade |
| gender | Gênero |
| income | Renda anual |
| bmi | Índice de Massa Corporal (IMC) |

### Dimensão — `dim_habitos`
Hábitos de jogo e rotina diária.

| Coluna | Descrição |
|--------|-----------|
| player_id | Chave primária (PK) |
| daily_gaming_hours | Horas de jogo por dia |
| weekly_sessions | Sessões de jogo por semana |
| years_gaming | Anos de experiência com jogos |
| sleep_hours | Média de horas de sono por dia |
| caffeine_intake | Quantidade de cafeína ingerida |
| exercise_hours | Horas de exercício por dia |
| weekend_gaming_hours | Horas jogadas nos fins de semana |
| screen_time_total | Tempo total de tela |
| streaming_hours | Horas assistindo streaming |

### Dimensão — `dim_comportamento`
Comportamento e preferências online.

| Coluna | Descrição |
|--------|-----------|
| player_id | Chave primária (PK) |
| multiplayer_ratio | Proporção de sessões multiplayer |
| toxic_exposure | Exposição a ambientes tóxicos |
| violent_games_ratio | Proporção de jogos violentos |
| mobile_gaming_ratio | Proporção de jogos mobile |
| night_gaming_ratio | Proporção de sessões noturnas |
| esports_interest | Interesse em e-sports (sim/não) |
| headset_usage | Uso de headset (sim/não) |
| microtransactions_spending | Gasto em microtransações |
| competitive_rank | Ranking competitivo |
| internet_quality | Qualidade da conexão de internet |

### Dimensão — `dim_social`
Vida social e interações do jogador.

| Coluna | Descrição |
|--------|-----------|
| player_id | Chave primária (PK) |
| friends_gaming_count | Quantidade de amigos que jogam |
| online_friends | Quantidade de amigos online |
| social_interaction_score | Score de interação social |
| relationship_satisfaction | Score de satisfação no relacionamento |
| loneliness_score | Score de solidão |
| parental_supervision | Tem supervisão parental? (sim/não) |

---

## Métricas de Negócio

As 5 queries executadas em `data/gold/metricas.py` respondem às seguintes perguntas:

| # | Pergunta |
|---|----------|
| M1 | Qual faixa de horas de jogo diárias está associada ao maior score de ansiedade? |
| M2 | Qual gênero apresenta maior nível médio de vício em jogos? |
| M3 | Jogadores com alta exposição a conteúdo tóxico têm maior agressividade? |
| M4 | Jogadores que dormem mais de 7h têm melhor saúde mental? |
| M5 | Jogadores com mais amigos online se sentem menos solitários? |

---

## Qualidade dos Dados

| Problema | Ação tomada |
|----------|-------------|
| Nenhum valor nulo encontrado | Nenhuma imputação necessária |
| Duplicatas | Verificadas e removidas |
| Tipos inconsistentes | Colunas binárias convertidas para `bool`, `gender` para `category` |
| Nomes de colunas | Padronizados para `snake_case` |

---

## Dificuldades Encontradas

- Entendimento do Star Schema e como implementá-lo na prática com o dataset
- Configuração da conexão com o PostgreSQL (PATH, credenciais, banco correto)
- O Stack Builder do PostgreSQL não conectava ao servidor — resolvido instalando o DBeaver separadamente