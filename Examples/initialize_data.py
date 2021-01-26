from EquationConstants import DB_HOST, DB_NAME, DB_PASS, DB_USER
from EquationConstants import DB_TABLE_NAMES_Q
import psycopg2
import psycopg2.extras

# p2 = subprocess.run(['convert', '-density 300', '-depth 8', '-quality 85', filename+'.pdf', filename+'.png'],
#   shell=True, capture_output=True, text=True, check=True)
# p1 = subprocess.run(['xelatex.exe', filename+'.tex','-interaction=batchmode'],
#   shell=True, capture_output=True, text=True, check=True)
# template_query = """INSERT INTO latex (data, image, thumbnail, insert_order, created_by)
#   VALUES ({data},{image},{thumbnail}, {insert_order}, {created_by})"""


connection = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)
cursor = connection.cursor()

myTable = 'unit'

template_query = """SELECT id, name FROM {aTable}""".format(aTable=myTable)
cursor.execute(template_query)

myData = cursor.fetchall()
self.tableWidget.setRowCount(0)

for row_number, row_data in enumerate(myData):
    self.tableWidget.insertRow(row_number)
    for column_number, data in enumerate(row_data):
        self.tableWidget.setItem(row_number, column_number, QtWidgets.QTableWidgetItem(str(data)))

cursor.close()
connection.close()
