import os
import psycopg2
from urllib.parse import urlparse

database_url = os.environ.get('DATABASE_URL')

if database_url:
    url = urlparse(database_url)
    db_name = url.path[1:]
    user = url.username
    password = url.password
    host = url.hostname
    port = url.port or 5432

    try:
        conn = psycopg2.connect(dbname=db_name, user=user, password=password, host=host, port=port)
        print("Conexão com o banco de dados estabelecida com sucesso!")
        conn.close()
    except psycopg2.Error as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        print(f"Detalhes do erro: {e.args}")
else:
    print("Variável de ambiente DATABASE_URL não encontrada.")