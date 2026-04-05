import pandas as pd
from sqlalchemy import create_engine

# Caminho do CSV
csv_path = "data/IOT-temp.csv"

print("Lendo arquivo CSV...")
df = pd.read_csv(csv_path)

#  LOG 1 — visualizar dados
print("\n Primeiras linhas:")
print(df.head())

#  LOG 2 — estrutura
print("\n Estrutura do dataset:")
print(df.info())

#  LOG 3 — valores nulos
print("\n Valores nulos por coluna:")
print(df.isnull().sum())

# =============================
#  TRATAMENTO DE DADOS
# =============================

print("\n Iniciando tratamento de dados...")

# Remover valores nulos
df = df.dropna()

# Converter temperatura para número
df["temp"] = pd.to_numeric(df["temp"], errors="coerce")

# Converter data para datetime
df["noted_date"] = pd.to_datetime(df["noted_date"], format="%d-%m-%Y %H:%M", errors="coerce")

# Remover linhas inválidas após conversão
df = df.dropna()

# LOG 4 — após tratamento
print("\n Dados após tratamento:")
print(df.head())

print("\n Estatísticas:")
print(df.describe())

#  CONEXÃO COM BANCO


print("\n Conectando ao PostgreSQL...")

engine = create_engine("postgresql://user:password@localhost:5432/iot_db")

# Enviar dados
print("\n Enviando dados para o banco...")

df.to_sql("temperature_readings", engine, if_exists="replace", index=False)

print("\n Dados inseridos com sucesso!")