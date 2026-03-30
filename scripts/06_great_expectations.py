import great_expectations as gx
import pandas as pd

CSV_PATH = "data/raw/gaming_mental_health_database.csv"

print("Lendo dataset...")
df = pd.read_csv(CSV_PATH, low_memory=False)

# Configura o contexto GX
context = gx.get_context()

# Cria o datasource
datasource = context.data_sources.add_pandas(name="gaming_datasource")
asset = datasource.add_dataframe_asset(name="gaming_asset")
batch_definition = asset.add_batch_definition_whole_dataframe("gaming_batch")
batch = batch_definition.get_batch(batch_parameters={"dataframe": df})

# Cria a suite de expectativas
suite = context.suites.add(
    gx.ExpectationSuite(name="gaming_mental_health_suite")
)

# Expectativa 1 — colunas essenciais sem nulos
for col in ["age", "gender", "anxiety_score", "depression_score"]:
    suite.add_expectation(
        gx.expectations.ExpectColumnValuesToNotBeNull(column=col)
    )

# Expectativa 2 — scores de saúde mental entre 0 e 10
for col in ["anxiety_score", "depression_score",
            "happiness_score", "stress_level", "addiction_level"]:
    suite.add_expectation(
        gx.expectations.ExpectColumnValuesToBeBetween(
            column=col, min_value=0, max_value=10
        )
    )

# Expectativa 3 — valores válidos para gênero
suite.add_expectation(
    gx.expectations.ExpectColumnValuesToBeInSet(
        column="gender",
        value_set=["Male", "Female", "Other"]
    )
)

# Expectativa 4 — horas de jogo entre 0 e 24
suite.add_expectation(
    gx.expectations.ExpectColumnValuesToBeBetween(
        column="daily_gaming_hours", min_value=0, max_value=24
    )
)

# Expectativa 5 — dataset deve ter pelo menos 100.000 linhas
suite.add_expectation(
    gx.expectations.ExpectTableRowCountToBeBetween(
        min_value=100000, max_value=2000000
    )
)

# Cria e executa a validação
validation_definition = context.validation_definitions.add(
    gx.ValidationDefinition(
        name="gaming_validation",
        data=batch_definition,
        suite=suite,
    )
)

results = validation_definition.run(
    batch_parameters={"dataframe": df}
)

# Cria o checkpoint
checkpoint = context.checkpoints.add(
    gx.Checkpoint(
        name="gaming_checkpoint",
        validation_definitions=[validation_definition],
    )
)

# Executa o checkpoint (isso salva os resultados para o Data Docs)
results = checkpoint.run(
    batch_parameters={"dataframe": df}
)

# Gera relatório HTML
context.build_data_docs()
context.open_data_docs()

# Resultado no terminal
print("\n=== Resultado da Validação ===")
print(f"Sucesso geral : {results.success}")