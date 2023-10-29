import xlsxwriter


def create_sheet(data_dict, file_name, auto_size=None):
    workbook = xlsxwriter.Workbook(file_name)

    for sheet_name, data in data_dict.items():
        worksheet = workbook.add_worksheet(sheet_name)

        # Шрифт
        bold_format = workbook.add_format({'bold': True})

        for row_num, row_data in enumerate(data):
            for col_num, cell_value in enumerate(row_data):
                if row_num == 0:
                    worksheet.write(row_num, col_num, cell_value, bold_format)
                else:
                    worksheet.write(row_num, col_num, cell_value)

        # Автоширина
        if auto_size:
            for col_num, col_data in enumerate(data[0]):
                max_width = max(len(str(row[col_num])) for row in data)
                worksheet.set_column(col_num, col_num, max_width + 2)

    workbook.close()



# Пример использования:
data = {
    'Лист1': [
        ('col1', 'col2', 'col3'),
        ('data1', 'data2', 'data2')],
    'Лист2': [
        ('col1', 'col2', 'col3'),
        ('data1', 'data2', 'data2')]
}

# create(data, 'example.xlsx', auto_size=True)
