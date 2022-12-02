# Библиотеки
import pandas as pd
import sqlite3 as sq


class Export:
    ### CONSTS
    """ 
    path                - путь до БД
    query_from_file     - флаг, брать ли запрос из файла
    query_file_path     - путь до запроса
    excel_query_text    - текст запроса, если запрос будет нужен не из файла
    column_names        - названия столбцов
    excel_file_path     - путь сохранения excel файла
    """

    column_names = ["Запись", "Время", "Пациент", "Пол", "Возраст", "Симптомы", "Номер", "Полис"]

    # Конструктор
    def __init__(self, path):
        # Путь до БД
        self.path = "bd.db"

        # Создание объекта connection
        self.connection = Export.create_connection(path)


    # Функция подключения к bd
    def create_connection(path):

        connection = None

        try:
            connection = sq.connect(path)
            if (__name__ == '__main__'):
                print("1. Connection to SQLite DB successful. \n")
        except sq.Error as e:
            print(f"1. The error '{e}' occured. \n")

        return connection



    # Функция выполнения запросов
    def execute_query(self, query):
        
        cursor = self.connection.cursor()

        try:
            cursor.execute(query)
            self.connection.commit()
            if (__name__ == '__main__'):
                print("3. Query executed successfully. \n")
        except sq.Error as e:
            print(f"3. The error '{e}' occured. \n")



    # Вывод выбранных ячеек
    def execute_read_query(self, id, *args, excel_query="", query_from_file="", query_file_path=""):

        cursor = self.connection.cursor()
        result = None

        if (query_from_file):
            with open(query_file_path, encoding='utf-8') as f:

                excel_query = f.read()

                if "{" in excel_query:
                    excel_query = excel_query.format(id)

                if (__name__ == '__main__'):
                    print("2. Excel query: \n", excel_query, "\n")

                excel_query = excel_query.splitlines()
                excel_query = " ".join( [s.lstrip('\t') for s in excel_query] )
        else:
            if (__name__ == '__main__'):
                    print("2. Excel query: \n", excel_query, "\n")
        
        try:
            cursor.execute(excel_query)
            result = cursor.fetchall()
            if (__name__ == '__main__'):
                print("3. Data fetched successfully. Fetched Data:")
            return result
        except sq.Error as e:
            print(f"3. The error '{e}' occured. \n")
            return result


    
    def dataFrame_create(self, table, column_names = [""]):
        return pd.DataFrame(data = table, columns = column_names)


    def excelFile_create(self, df, excel_file_path="./requests/first_request", column_widthes = [25, 7, 15, 10, 7, 30, 15, 20]):

        startCells = [1]
        for row in range(2,len(df)+1):
            if (df.loc[row-1,'Запись'] != df.loc[row-2,'Запись']):
                startCells.append(row)


        writer = pd.ExcelWriter(excel_file_path + '/timetable.xlsx', engine='xlsxwriter')
        df.to_excel(writer, sheet_name='Sheet1', index=False)
        workbook = writer.book
        worksheet = writer.sheets['Sheet1']
        merge_format = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'border': 2 } )
        row_format = workbook.add_format()


        lastRow = len(df)

        for row in startCells:
            try:
                endRow = startCells[startCells.index(row)+1]-1
                if row == endRow:
                    worksheet.write(row, 0, df.loc[row-1,'Запись'], merge_format)
                else:
                    worksheet.merge_range(row, 0, endRow, 0, df.loc[row-1,'Запись'], merge_format)
            except IndexError:
                if row == lastRow:
                    worksheet.write(row, 0, df.loc[row-1,'Запись'], merge_format)
                else:
                    worksheet.merge_range(row, 0, lastRow, 0, df.loc[row-1,'Запись'], merge_format)

        
        for i in range(len(df.columns)):
            worksheet.set_column(i, i, column_widthes[i])
        writer.save()

    def correctQuery(query, id):
        query.format(id)

    
    # Конечная функция
    def excelFromQuery(self, *args, id, excel_query="", query_from_file=False, query_file_path="", column_names=column_names, excel_file_path="./excel_files"):


        # Таблица выбранных данных из БД
        table = self.execute_read_query(id=id, excel_query = excel_query, 
                                        query_from_file = query_from_file, 
                                        query_file_path = query_file_path)

        # DataFrame из table:
        df = self.dataFrame_create(table=table, column_names=column_names)

        # Если датасет пустой
        if not df.empty:
            # Создание файла
            self.excelFile_create(df, excel_file_path)
        else:
            writer = pd.ExcelWriter(excel_file_path + '/timetable.xlsx', engine='xlsxwriter')
            df.to_excel(writer, sheet_name='Empty timetable', index=False)
            writer.save()




