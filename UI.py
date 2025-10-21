from tkinter import *
from tkinter import ttk
from tkinter.messagebox import showinfo, showerror
from DBConn import DBConnection

from pyexpat.errors import messages


class DBLibraryUI:
    def __init__(self, title, width, height):
        self.entrybuffer = dict()
        self.tablecolinfo = dict()
        self.tablecolinfo["Кабинеты"] = {"Ид": "ClassroomID",
                                         "Название": "RoomName"}
        self.tablecolinfo["Расписания"] = {"Ид": "ScheduleID",
                                           "День недели": "Weekday",
                                           "Класс": "ClassID",
                                           "Номер урока": "LessonNumber",
                                           "Начало": "StartTime",
                                           "Конец": "EndTime",
                                           "Предмет": "SubjectID",
                                           "Учитель": "TeacherID",
                                           "Кабинет": "ClassroomID"}
        self.tablecolinfo["Предметы"] = {"Ид": "SubjectID",
                                         "Название": "SubjectName",
                                         "Тип": "SubjectType",
                                         "Учитель": "TeacherID"}
        self.tablecolinfo["Учителя"] = {"Ид": "TeacherID",
                                        "Полное имя": "FullName"}
        self.tablecolinfo["Классы"] = {"Ид": "ClassID",
                                       "Номер": "Grade",
                                       "Буква": "Letter"}

        self.tabledbnames = dict()
        self.tabledbnames["Кабинеты"] = "[dbo].[Classrooms]"
        self.tabledbnames["Расписания"] = "[dbo].[Schedule]"
        self.tabledbnames["Предметы"] = "[dbo].[Subjects]"
        self.tabledbnames["Учителя"] = "[dbo].[Teachers]"
        self.tabledbnames["Классы"] = "[dbo].[Classes]"

        self.root = Tk()
        self.root.title(title)
        self.root.minsize(width=width, height=height)
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        topmenu = Menu()

        reportmenu = Menu(tearoff=0)
        reportmenu.add_command(label="Учитель с наибольшим кол-вом предметов", command=self.report_mostteacher)
        reportmenu.add_command(label="Наименее используемая аудитория в дни", command=self.report_leastclassroom)
        reportmenu.add_command(label="Уроки и учителя для класса", command=self.report_lessonsforclass)
        reportmenu.add_command(label="Список предметов и учителей для параллели", command=self.report_subjectsforparallel)
        topmenu.add_cascade(label="Отчеты", menu=reportmenu)

        self.root.configure(menu=topmenu)

        self.mainframe = ttk.Frame(self.root, borderwidth=3, relief="raised", padding=(3, 3, 3, 3))
        self.mainframe.grid(column=0, row=0, sticky="nwes")
        self.mainframe.columnconfigure(0, weight=1)
        self.mainframe.columnconfigure(1, weight=1)
        self.mainframe.columnconfigure(2, weight=1)
        self.mainframe.columnconfigure(3, weight=1)
        self.mainframe.rowconfigure(0, weight=3)

        self.tableframe = ttk.Frame(self.mainframe, height=320, borderwidth=3, relief="sunken", padding=(3, 3, 3, 3))
        self.tableframe.grid(column=0, row=0, columnspan=4, sticky="nwes")
        self.tableframe.columnconfigure(0, weight=1)
        self.tableframe.columnconfigure(1, weight=0)
        self.tableframe.rowconfigure(0, weight=1)

        self.table = ttk.Treeview(self.tableframe, show="headings")
        self.table.grid(column=0, row=0, sticky="nwes")

        tablescroll = ttk.Scrollbar(self.tableframe, orient=VERTICAL, command=self.table.yview)
        self.table.configure(yscrollcommand=tablescroll.set)
        tablescroll.grid(column=1, row=0, sticky="nes")

        modiframe = ttk.Frame(self.mainframe, padding=(3,3,3,3))
        modiframe.grid(column=0, row=1, sticky="nwes")
        modiframe.columnconfigure(0, weight=1)
        modiframe.rowconfigure(0, weight=1)
        modiframe.rowconfigure(1, weight=1)
        modiframe.rowconfigure(2, weight=1)

        self.elementwidth = 20
        ttk.Button(modiframe, text="Удалить запись", command=self.deleteentry, width=self.elementwidth).grid(column=0, row=0, sticky="w")
        ttk.Button(modiframe, text="Добавить запись", command=self.createentry, width=self.elementwidth).grid(column=0, row=1, sticky="w")
        ttk.Button(modiframe, text="Редактировать запись", command=self.modifyentry, width=self.elementwidth).grid(column=0, row=2, sticky="w")

        queryframe = ttk.Frame(self.mainframe, padding=(3,3,3,3))
        queryframe.grid(column=1, row=1, sticky="nwes")
        queryframe.columnconfigure(0, weight=1)
        queryframe.rowconfigure(0, weight=1)
        queryframe.rowconfigure(1, weight=1)

        ttk.Button(queryframe, text="Выборка", command=self.qrybasic, width=self.elementwidth).grid(column=0, row=0, sticky="w")
        self.tablechoise = ttk.Combobox(queryframe, width=self.elementwidth, values=tuple(self.tabledbnames.keys()), state="readonly")
        self.tablechoise.grid(column=0, row=1, sticky="w")
        self.tablechoise.bind("<<ComboboxSelected>>", self.choosetable)

        searchframe = ttk.Frame(self.mainframe, padding=(3,3,3,3))
        searchframe.grid(column=2, row=1, sticky="nwes")
        searchframe.columnconfigure(0, weight=1)
        searchframe.rowconfigure(0, weight=1)
        searchframe.rowconfigure(1, weight=1)
        searchframe.rowconfigure(2, weight=1)

        self.issearchvar = IntVar(value=0)
        self.issearch = ttk.Checkbutton(searchframe, text="Поиск", variable=self.issearchvar, command=self.searchchecked, width=self.elementwidth)
        self.issearch.grid(column=0, row=0, sticky="w")
        self.searchcol = ttk.Combobox(searchframe, width=self.elementwidth, state=DISABLED)
        self.searchcol.grid(column=0, row=1, sticky="w")
        self.searchval = ttk.Entry(searchframe, width=self.elementwidth, state=DISABLED)
        self.searchval.grid(column=0, row=2, sticky="w")

        sortframe = ttk.Frame(self.mainframe, padding=(3,3,3,3))
        sortframe.grid(column=3, row=1, sticky="nwes")
        sortframe.columnconfigure(0, weight=1)
        sortframe.rowconfigure(0, weight=1)
        sortframe.rowconfigure(1, weight=1)
        sortframe.rowconfigure(2, weight=1)

        self.issortvar = IntVar(value=0)
        self.issort = ttk.Checkbutton(sortframe,  text="Сортировка", variable=self.issortvar, command=self.sortchecked, width=self.elementwidth)
        self.issort.grid(column=0, row=0, sticky="w")
        self.sortcol = ttk.Combobox(sortframe, width=self.elementwidth, state=DISABLED)
        self.sortcol.grid(column=0, row=1, sticky="w")
        self.sorttype = ttk.Combobox(sortframe, width=self.elementwidth, values=("Убывание", "Возрастание"), state=DISABLED)
        self.sorttype.grid(column=0, row=2, sticky="w")

        self.dbconn = DBConnection()

    def qrybasic(self):
        dbcols = self.tablecolinfo[self.tablechoise.get()].values()
        qry = "select " + ", ".join(dbcols) + " from " + self.tabledbnames[self.tablechoise.get()]
        if self.issearchvar.get() == 1:
            if self.searchcol.get() not in self.tablecolinfo[self.tablechoise.get()].keys():
                showerror("Ошибка запроса", message="Укажите столбец для поиска!")
                return
            qry += " where " + self.tablecolinfo[self.tablechoise.get()][self.searchcol.get()] + "="
            if self.searchval.get().isdigit():
                qry += self.searchval.get()
            else:
                qry += "'" + self.searchval.get() + "'"
        if self.issortvar.get() == 1:
            if self.sortcol.get() not in self.tablecolinfo[self.tablechoise.get()].keys():
                showerror("Ошибка запроса", message="Укажите столбец для сортировки!")
                return
            qry += " order by " + self.tablecolinfo[self.tablechoise.get()][self.sortcol.get()]
            if self.sorttype.get() == "Убывание":
                qry += " desc"
            elif self.sorttype.get() == "Возрастание":
                qry += " asc"
            else:
                showerror("Ошибка запроса", message="Укажите вид сортировки!")
                return
        print(qry)
        self.qrydbandfilltable(qry)

    def choosetable(self, event):
        self.cleartable()
        dbcolumns = tuple(self.tablecolinfo[self.tablechoise.get()].values())
        colnames = tuple(self.tablecolinfo[self.tablechoise.get()].keys())
        self.table.configure(columns=dbcolumns)
        self.searchcol.configure(values=colnames)
        self.sortcol.configure(values=colnames)
        colnum = 1
        for col in colnames:
            self.table.heading(self.tablecolinfo[self.tablechoise.get()][col], text=col, anchor="w")
            self.table.column(f"#{colnum}", stretch=YES)
            colnum+=1
        self.table.update()
        self.sortcol.update()
        self.searchcol.update()

    def sortchecked(self):
        if self.issortvar.get() == 0:
            self.sortcol.configure(state=DISABLED)
            self.sorttype.configure(state=DISABLED)
        else:
            self.sortcol.configure(state="readonly")
            self.sorttype.configure(state="readonly")
        self.sortcol.update()
        self.sorttype.update()

    def searchchecked(self):
        if self.issearchvar.get() == 0:
            self.searchcol.configure(state=DISABLED)
            self.searchval.configure(state=DISABLED)
        else:
            self.searchcol.configure(state="readonly")
            self.searchval.configure(state=NORMAL)
        self.searchcol.update()
        self.searchval.update()

    def createentry(self):
        if self.tablechoise.get() not in self.tablecolinfo.keys():
            showerror("Ошибка создания записи", message="Необходимо выбрать таблицу!")
            return

        creationwindow = Tk()
        creationwindow.title("Новая запись")
        creationwindow.minsize(width=265, height=220)
        creationwindow.maxsize(width=265, height=220)

        creationframe = ttk.Frame(creationwindow, padding=(3,3,3,3))
        creationframe.grid(column=0, row=0)

        self.entrybuffer = dict()
        rownum = 0
        insertcols = tuple(self.tablecolinfo[self.tablechoise.get()].keys())[1:]
        insertdbcols = tuple(self.tablecolinfo[self.tablechoise.get()].values())[1:]
        for col in insertcols:
            ttk.Label(creationframe, width=self.elementwidth, text=col).grid(column=0, row=rownum)
            self.entrybuffer[col] = ttk.Entry(creationframe, width=self.elementwidth)
            self.entrybuffer[col].grid(column=1, row=rownum)
            rownum+=1

        def qrycreateentry():
            qry = "insert into " + self.tabledbnames[self.tablechoise.get()]
            qry += " (" + ", ".join(insertdbcols) + ") values ("
            values = list()
            for entrycol in insertcols:
                entryval = self.entrybuffer[entrycol].get()
                if entryval.isdigit():
                    values.append(entryval)
                elif entryval.isalnum():
                    values.append("'" + entryval + "'")
            qry += ", ".join(values) + ")"
            self.dbconn.makegeneralquery(qry)
            self.qrybasic()
            creationwindow.destroy()

        ttk.Button(creationframe, width=self.elementwidth, text="Отменить", command=creationwindow.destroy).grid(column=0, row=rownum)
        ttk.Button(creationframe, width=self.elementwidth, text="Создать", command=qrycreateentry).grid(column=1, row=rownum)
        creationwindow.grab_set()
        creationwindow.mainloop()

    def modifyentry(self):
        if len(self.table.selection()) != 1:
            showerror("Ошибка редактирования", message="Необходимо выбрать одну запись!")
            return

        modifwindow = Tk()
        modifwindow.title("Редактирование записи")
        modifwindow.minsize(width=265, height=220)
        modifwindow.maxsize(width=265, height=220)

        modifframe = ttk.Frame(modifwindow, padding=(3, 3, 3, 3))
        modifframe.grid(column=0, row=0)

        modifcols = tuple(self.tablecolinfo[self.tablechoise.get()].keys())
        modifdbcols = tuple(self.tablecolinfo[self.tablechoise.get()].values())

        self.entrybuffer = dict()
        entryvalues = self.table.item(self.table.selection()[0])["values"]
        rownum = 0
        for col in modifcols:
            ttk.Label(modifframe, width=self.elementwidth, text=col).grid(column=0, row=rownum)
            self.entrybuffer[col] = ttk.Entry(modifframe, width=self.elementwidth)
            self.entrybuffer[col].insert(0, entryvalues[rownum])
            self.entrybuffer[col].grid(column=1, row=rownum)
            if rownum == 0:
                self.entrybuffer[col].configure(state="readonly")
            rownum += 1

        def qrymodifentry():
            qry = "update " + self.tabledbnames[self.tablechoise.get()]
            qry += "set "
            for entrycol in modifcols[1:]:
                qry += self.tablecolinfo[self.tablechoise.get()][col] + "="
                entryval = self.entrybuffer[entrycol].get()
                if entryval.isdigit():
                    qry += entryval
                elif entryval.isalnum():
                    qry += "'" + entryval + "'"
            qry += " where " + self.tablecolinfo[self.tablechoise.get()][modifcols[0]] + "="
            entryval = self.entrybuffer[modifcols[0]].get()
            if entryval.isdigit():
                qry += entryval
            elif entryval.isalnum():
                qry += "'" + entryval + "'"

            self.dbconn.makegeneralquery(qry)
            self.qrybasic()
            modifwindow.destroy()

        ttk.Button(modifframe, width=self.elementwidth, text="Отменить", command=modifwindow.destroy).grid(column=0, row=rownum)
        ttk.Button(modifframe, width=self.elementwidth, text="Редактировать", command=qrymodifentry).grid(column=1, row=rownum)
        modifwindow.grab_set()
        modifwindow.mainloop()

    def deleteentry(self):
        if len(self.table.selection()) == 0:
            showerror("Ошибка удаления", message="Выберите хотя бы одну запись из таблицы!")
            return

        def qrydelete(id):
            qry = "delete " + self.tabledbnames[self.tablechoise.get()] + " where " + tuple(self.tablecolinfo[self.tablechoise.get()].values())[0] + "=" + str(id)
            self.dbconn.makegeneralquery(qry)
            self.qrybasic()

        for entry in [self.table.item(row)["values"] for row in self.table.selection()]:
            qrydelete(entry[0])

    def report_mostteacher(self):
        qry = "SELECT TOP 1 "
        qry += "t.TeacherID, t.FullName AS Учитель, COUNT(DISTINCT s.SubjectID) AS КоличествоПредметов "
        qry += "FROM [dbo].[Teachers] t "
        qry += "INNER JOIN [dbo].[Subjects] s ON t.TeacherID = s.TeacherID "
        qry += "GROUP BY t.TeacherID, t.FullName "
        qry += "ORDER BY КоличествоПредметов DESC;"
        columns = ("Ид", "Учитель", "КоличествоПредметов")
        self.cleartable()
        self.table.configure(columns=columns)
        rownum = 0
        for col in columns:
            self.table.heading(col, text=col, anchor="w")
            self.table.column(f"#{rownum}", stretch=YES)
            rownum+=1

        rows = self.dbconn.makeselectquery(qry)
        for row in rows:
            self.table.insert("", END, values=tuple(row))
        self.table.update()
        self.tablechoise.set("")

    def report_leastclassroom(self):
        reportwindow = Tk()
        reportwindow.title("Отчет")
        reportwindow.minsize(width=265, height=100)
        reportwindow.maxsize(width=265, height=100)

        reportframe = ttk.Frame(reportwindow, padding=(3,3,3,3))
        reportframe.grid(row=0, column=0)

        ttk.Label(reportframe, text="Дни недели", width=self.elementwidth).grid(row=0, column=0, sticky="w")
        days = ttk.Entry(reportframe, width=self.elementwidth)
        days.grid(row=0, column=1)

        def qryleastclassroom():
            qry = "SELECT TOP 1 WITH TIES "
            qry += "c.RoomName AS Аудитория, COUNT(s.ScheduleID) AS КоличествоУроков, COUNT(DISTINCT s.Weekday) AS ДнейИспользования, "
            qry += "CASE"
            qry += " WHEN COUNT(s.ScheduleID) = 0 THEN 'Не используется'"
            qry += " WHEN COUNT(s.ScheduleID) = 3 THEN 'Мало используется'"
            qry += " WHEN COUNT(s.ScheduleID) = 8 THEN 'Умеренно используется' "
            qry += "ELSE 'Активно используется' "
            qry += "END AS Статус "
            qry += "FROM [dbo].[Classrooms] c "
            values = list()
            for day in days.get().split(","):
                values.append(f"'{day}'")
            qry += f"LEFT JOIN Schedule s ON c.ClassroomID = s.ClassroomID AND s.Weekday IN ({", ".join(values)}) "
            qry += "GROUP BY c.ClassroomID, c.RoomName "
            qry += "ORDER BY КоличествоУроков ASC;"

            columns = ("Аудитория", "КоличествоУроков", "ДнейИспользования", "Статус")
            self.cleartable()
            self.table.configure(columns=columns)
            rownum = 0
            for col in columns:
                self.table.heading(col, text=col, anchor="w")
                self.table.column(f"#{rownum}", stretch=YES)
                rownum += 1

            self.qrydbandfilltable(qry)
            self.table.update()
            self.tablechoise.set("")
            reportwindow.destroy()

        ttk.Button(reportframe, width=self.elementwidth, text="Отменить", command=reportwindow.destroy).grid(column=0, row=1)
        ttk.Button(reportframe, width=self.elementwidth, text="Выполнить", command=qryleastclassroom).grid(column=1, row=1)
        reportwindow.grab_set()
        reportwindow.mainloop()

    def report_lessonsforclass(self):
        qry = "SELECT c.ClassID, CONCAT(c.Grade, c.Letter) AS Класс, COUNT(s.ScheduleID) AS КоличествоУроков, COUNT(DISTINCT s.TeacherID) AS КоличествоУчителей "
        qry += "FROM [dbo].[Classes] c "
        qry += "INNER JOIN [dbo].[Schedule] s ON c.ClassID = s.ClassID "
        qry += "WHERE s.Weekday IN('ПН', 'ВТ', 'СР', 'ЧТ', 'ПТ') "
        qry += "GROUP BY c.ClassID, c.Grade, c.Letter "
        qry += "ORDER BY c.Grade, c.Letter;"

        columns = ("Ид", "Класс", "КоличествоУроков", "КоличествоУчителей")
        self.cleartable()
        self.table.configure(columns=columns)
        rownum = 0
        for col in columns:
            self.table.heading(col, text=col, anchor="w")
            self.table.column(f"#{rownum}", stretch=YES)
            rownum += 1

        self.qrydbandfilltable(qry)
        self.table.update()
        self.tablechoise.set("")

    def report_subjectsforparallel(self):
        reportwindow = Tk()
        reportwindow.title("Отчет")
        reportwindow.minsize(width=265, height=100)
        reportwindow.maxsize(width=265, height=100)

        reportframe = ttk.Frame(reportwindow, padding=(3, 3, 3, 3))
        reportframe.grid(row=0, column=0)

        ttk.Label(reportframe, text="Класс", width=self.elementwidth).grid(row=0, column=0, sticky="w")
        grade = ttk.Entry(reportframe, width=self.elementwidth)
        grade.grid(row=0, column=1)

        def qrysubjectsparallel():
            qry = "SELECT DISTINCT sub.SubjectName AS Предмет, "
            qry += "CASE"
            qry += " WHEN sub.SubjectType IS NOT NULL THEN '(' + sub.SubjectType + ')'"
            qry += " ELSE ''"
            qry += "END AS Тип, t.FullName AS Учитель "
            qry += "FROM [dbo].[Subjects] sub "
            qry += "INNER JOIN [dbo].[Teachers] t ON sub.TeacherID = t.TeacherID "
            qry += "INNER JOIN [dbo].[Schedule] s ON sub.SubjectID = s.SubjectID "
            qry += "INNER JOIN [dbo].[Classes] c ON s.ClassID = c.ClassID "
            qry += f"WHERE c.Grade = {grade.get()} "
            qry += "GROUP BY sub.SubjectName, sub.SubjectType, t.FullName "
            qry += "ORDER BY Предмет, Учитель;"

            columns = ("Предмет", "Тип", "Учитель")
            self.cleartable()
            self.table.configure(columns=columns)
            rownum = 0
            for col in columns:
                self.table.heading(col, text=col, anchor="w")
                self.table.column(f"#{rownum}", stretch=YES)
                rownum += 1

            self.qrydbandfilltable(qry)
            self.table.update()
            self.tablechoise.set("")
            reportwindow.destroy()

        ttk.Button(reportframe, width=self.elementwidth, text="Отменить", command=reportwindow.destroy).grid(column=0,row=1)
        ttk.Button(reportframe, width=self.elementwidth, text="Выполнить", command=qrysubjectsparallel).grid(column=1,row=1)
        reportwindow.grab_set()
        reportwindow.mainloop()

    def qrydbandfilltable(self, qry):
        rows = self.dbconn.makeselectquery(qry)
        self.cleartable()
        for row in rows:
            self.table.insert("", END, values=tuple(row))

    def cleartable(self):
        for row in self.table.get_children():
            self.table.delete(row)

    def start(self):
        self.root.mainloop()