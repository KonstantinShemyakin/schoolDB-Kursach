import pyodbc

class DBConnection:
    def __init__(self, server, db, userid, password):
        connection_str = f"DRIVER=kuk;SERVER={server};DATABASE={db};UID={userid};PWD={password}"
        self.connection = pyodbc.connect(connection_str)

if __name__ == "__main__":
    conn = DBConnection("localhost", "your test db", "your user", "your passwd")
