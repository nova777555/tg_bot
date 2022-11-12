# Библиотеки
import pandas as pd
import sqlite3 as sq



### CONSTS
""" 
path                - путь до БД
query_from_file     - флаг, брать ли запрос из файла
query_file_path     - путь до запроса
excel_query_text    - текст запроса, если запрос будет нужен не из файла
column_names        - названия столбцов
"""
path = "bd.db"
query_from_file = True
query_file_path = "./requests/first_request"
excel_file_path = "./excel_files"

excel_query = """
SELECT  CASE 
            WHEN strftime('%w', appointments.date) = '1' THEN appointments.date || " (Понедельник)"
            WHEN strftime('%w', appointments.date) = '2' THEN appointments.date || " (Вторник)" 
            WHEN strftime('%w', appointments.date) = '3' THEN appointments.date || " (Среда)" 
            WHEN strftime('%w', appointments.date) = '4' THEN appointments.date || " (Четверг)" 
            WHEN strftime('%w', appointments.date) = '5' THEN appointments.date || " (Пятница)" 
            WHEN strftime('%w', appointments.date) = '6' THEN appointments.date || " (Суббота)" 
            ELSE "Воскресенье"
            END AS День,
	   CAST(time / 2 AS STRING) || ':' || IIF(time % 2 = 0, '00', '30') AS Время,
	   name || ' ' || surname AS Пациент,
	   IIF(sex = 1, 'Мужчина', 'Женщина') AS Пол,
	   DATE() - birthday AS Возраст,
	   simptoms AS Симптомы,
	   number AS Номер,
	   polis AS Полис
FROM appointments INNER JOIN users ON appointments.patient = users.id
WHERE patient IS NOT NULL
"""
column_names = ["Запись", "Время", "Пациент", "Пол", "Возраст", "Симптомы", "Номер", "Полис"]



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

# Создание объекта connection
connection = create_connection(path)



# Функция выполнения запросов
def execute_query(connection, query):
    
    cursor = connection.cursor()

    try:
        cursor.execute(query)
        connection.commit()
        if (__name__ == '__main__'):
            print("3. Query executed successfully. \n")
    except sq.Error as e:
        print(f"3. The error '{e}' occured. \n")



# Вывод выбранных ячеек
def execute_read_query(connection, query):

    cursor = connection.cursor()
    result = None

    try:
        cursor.execute(query)
        result = cursor.fetchall()
        if (__name__ == '__main__'):
            print("3. Data fetched successfully. \n")
        return result
    except sq.Error as e:
        print(f"3. The error '{e}' occured. \n")

# Запрос
if (query_from_file):
    with open(query_file_path) as f:
        excel_query = f.read()

        if (__name__ == '__main__'):
            print("2. Excel query: \n", excel_query, "\n")

        excel_query = excel_query.splitlines()
        excel_query = " ".join( [s.lstrip('\t') for s in excel_query] )

# Вывод запроса
table = execute_read_query(connection, excel_query)
if (__name__ == '__main__'):
    print("4. Inserted data:")
    for row in table:
        print(row)



# Создание DataFrame pandas
df = pd.DataFrame(data = table, columns = column_names)

if (__name__ == '__main__'):
    print("\n 4. Current DataFrame: \n", df, "\n")





startCells = [1]
for row in range(2,len(df)+1):
    if (df.loc[row-1,'Запись'] != df.loc[row-2,'Запись']):
        startCells.append(row)


writer = pd.ExcelWriter(excel_file_path + '/timetable.xlsx', engine='xlsxwriter')
df.to_excel(writer, sheet_name='Sheet1', index=False)
workbook = writer.book
worksheet = writer.sheets['Sheet1']
merge_format = workbook.add_format({'align': 'center', 'valign': 'vcenter'})


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


writer.save()