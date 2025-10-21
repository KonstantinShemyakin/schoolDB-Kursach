import pyodbc

class DBConnection:
    def __init__(self):
        connection_str = "DRIVER={ODBC Driver 17 for SQL Server};Server=localhost\\SQLEXPRESS;Database=SchoolSchedule10;Trusted_Connection=yes;"
        self.connection = pyodbc.connect(connection_str)

    def makeselectquery(self, qry):
        qrycursor = self.connection.cursor()
        qrycursor.execute(qry)
        return qrycursor.fetchall()

    def makegeneralquery(self, qry):
        self.connection.execute(qry)
        self.connection.commit()

if __name__ == "__main__":
    conn = DBConnection()
    for row in conn.makeselectquery("select * from [dbo].[Classrooms]"):
        print(row)
