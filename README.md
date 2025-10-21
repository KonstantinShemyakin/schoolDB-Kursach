## School database viewer project
It is a very simple UI built with tkinter for making standart DB queries for getting, adding, deleting and changing data in tables.
pyodbc library was used for DB connection and querying.

Project was written with python 3.14. 
To create new venv with used library launch create_venv.bat from your project folder.

Standart DB is SQL Server Express with connection host 'localhost\SQLEXPRESS'. 
You can launch dbtest.bat and check your db connection. It will make a simple select query for table 'Classrooms'.

To launch main program using created venv start launch.bat file.
