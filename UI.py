from tkinter import *
from tkinter import ttk
from tkinter.messagebox import showinfo, showerror

from pyexpat.errors import messages


class DBLibraryUI:
    def __init__(self, title, width, height):
        self.entrybuffer = dict()
        self.tablecolinfo = dict()
        self.tablecolinfo["Авторы"] = ("col1", "col2")
        self.tablecolinfo["Залы"] = ("col1", "col2")
        self.tablecolinfo["Города"] = ("col1", "col2")
        self.tablecolinfo["Издательства"] = ("col1", "col2")
        self.tablecolinfo["Жанры"] = ("col1", "col2")
        self.tablecolinfo["Книги"] = ("col1", "col2")
        self.tablecolinfo["Экземпляры"] = ("col1", "col2")
        self.tablecolinfo["Читатели"] = ("col1", "col2")

        self.tabledbnames = dict()
        self.tabledbnames["Авторы"] = "name"
        self.tabledbnames["Залы"] = "name"
        self.tabledbnames["Города"] = "name"
        self.tabledbnames["Издательства"] = "name"
        self.tabledbnames["Жанры"] = "name"
        self.tabledbnames["Книги"] = "name"
        self.tabledbnames["Экземпляры"] = "name"
        self.tabledbnames["Читатели"] = "name"

        self.root = Tk()
        self.root.title(title)
        self.root.minsize(width=width, height=height)
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        topmenu = Menu()

        reportmenu = Menu(tearoff=0)
        reportmenu.add_command(label="Учитель с наибольшим кол-вом предметов")
        reportmenu.add_command(label="Наименее используемая аудитория в дни")
        reportmenu.add_command(label="Уроки и учителя для класса")
        reportmenu.add_command(label="Список предметов и учителей для параллели")
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

        ttk.Button(queryframe, text="Выборка", width=self.elementwidth).grid(column=0, row=0, sticky="w")
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

    def choosetable(self, event):
        for row in self.table.get_children():
            self.table.delete(row)
        self.table.configure(columns=self.tablecolinfo[self.tablechoise.get()])
        self.searchcol.configure(values=self.tablecolinfo[self.tablechoise.get()])
        self.sortcol.configure(values=self.tablecolinfo[self.tablechoise.get()])
        colnum = 1
        for colname in self.tablecolinfo[self.tablechoise.get()]:
            self.table.heading(colname, text=colname, anchor="w")
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
        creationwindow.minsize(width=265, height=200)
        creationwindow.maxsize(width=265, height=200)

        creationframe = ttk.Frame(creationwindow, padding=(3,3,3,3))
        creationframe.grid(column=0, row=0)

        self.entrybuffer = dict()
        rownum = 0
        for col in self.tablecolinfo[self.tablechoise.get()]:
            ttk.Label(creationframe, width=self.elementwidth, text=col).grid(column=0, row=rownum)
            self.entrybuffer[col] = ttk.Entry(creationframe, width=self.elementwidth)
            self.entrybuffer[col].grid(column=1, row=rownum)
            rownum+=1
        ttk.Button(creationframe, width=self.elementwidth, text="Отменить", command=creationwindow.destroy).grid(column=0, row=rownum)
        ttk.Button(creationframe, width=self.elementwidth, text="Создать", command=creationwindow.destroy).grid(column=1, row=rownum)
        creationwindow.mainloop()

    def modifyentry(self):
        if len(self.table.selection()) != 1:
            showerror("Ошибка редактирования", message="Необходимо выбрать единственную запись!")
            return

        modifwindow = Tk()
        modifwindow.title("Редактирование записи")
        modifwindow.minsize(width=265, height=200)
        modifwindow.maxsize(width=265, height=200)

        modifframe = ttk.Frame(modifwindow, padding=(3, 3, 3, 3))
        modifframe.grid(column=0, row=0)

        self.entrybuffer = dict()
        entryvalues = self.table.item(self.table.selection()[0])["values"]
        rownum = 0
        for col in self.tablecolinfo[self.tablechoise.get()]:
            ttk.Label(modifframe, width=self.elementwidth, text=col).grid(column=0, row=rownum)
            self.entrybuffer[col] = ttk.Entry(modifframe, width=self.elementwidth)
            self.entrybuffer[col].insert(0, entryvalues[rownum])
            self.entrybuffer[col].grid(column=1, row=rownum)
            rownum += 1
        ttk.Button(modifframe, width=self.elementwidth, text="Отменить", command=modifwindow.destroy).grid(column=0, row=rownum)
        ttk.Button(modifframe, width=self.elementwidth, text="Редактировать", command=modifwindow.destroy).grid(column=1, row=rownum)
        modifwindow.mainloop()

    def deleteentry(self):
        self.table.insert("", END, values=("69", "FUckYoY"))
        #for entry in self.table.selection():
        #    pass #query deletion of all entries one by one

    def start(self):
        self.root.mainloop()