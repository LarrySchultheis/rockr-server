import psycopg2
from rockr import config

# Simple starter class to wrap psycopg2 commands for DB access
# In the future we should implement some ORM like SQLAlchemy
# This will get us basic CRUD for now
class DbManager():
    def __init__(self):
        self.host = config.DATABSE_CONFIG['host']
        self.db = config.DATABSE_CONFIG['database']

    def _get_conn(self):
        return psycopg2.connect(host=self.host, database=self.db)

    def select(self, table, cols):
        query = f"SELECT {','.join(cols)} FROM {table}"

        conn = self._get_conn()
        cur = conn.cursor()

        cur.execute(query)
        res = cur.fetchall()
        cur.close()
        conn.close()
        return res