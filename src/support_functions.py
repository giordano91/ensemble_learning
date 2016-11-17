import xlrd
import xlsxwriter


def read_data(path):
    """
    Read data from Excel file that user chose
    :param path: string
    :return:
    - values: a list of values read
    - header: a list with the first row of Excel file (without last column)
    """

    values = []
    workbook = xlrd.open_workbook(path)
    sheet = workbook.sheet_by_index(0)

    header = sheet.row_values(0)

    for row_idx in range(1, sheet.nrows):
        row = sheet.row_values(row_idx)
        instance = {}
        for col_idx in range(0, sheet.ncols):
            if col_idx == sheet.ncols - 1:
                instance['result'] = row[col_idx]
            else:
                instance[header[col_idx]] = row[col_idx]
        values.append(instance)

    return values, header[:-1]


def prepare_data(data, header):
    """
    :param data: list of dictionaries; keys are attributes and values represent the binary form of real values
                example: [
                            {'result': 1, 'Age': 0, 'Size': 0, 'Color': 0, 'Act': 0},
                            {'result': 0, 'Age': 1, 'Size': 0, 'Color': 0, 'Act': 0}
                          ]
    :param header: the first row of Excel file (without last column) - list
    :return:
    - values_list: a list of list contains attributes values order by excel header
    example: [[0, 0, 0, 0], [0, 0, 0, 1]]
    - results_list: a list with all final results of Excel (1 o 0)
    """
    values_list = []
    results_list = []
    for instance in data:
        single_list = []
        results_list.append(instance['result'])
        for elem in header:
            single_list.append(instance[elem])
        values_list.append(single_list)

    return values_list, results_list


def convert_data(data):
    """
    For each column of Excel file, converts data from strings to binary values in this way:
    For each attribute, every record is changed in a number; The first attribute is 0 and when the function
    finds a new attribute, this is converted in 1. The same logic is repeated for each different attribute
    example:
    -+- attribute 1 -+- attribute 2 -+-
    -+-   blue      -+-   small     -+-
    -+-   red       -+-    big      -+-
    -+-   red       -+-   small     -+-
    become
    -+- attribute 1 -+- attribute 2 -+-
    -+-      0      -+-      0      -+-
    -+-      1      -+-      1      -+-
    -+-      1      -+-      0      -+-
    :param data: list of dictionaries; keys are attributes and values represent the binary form of real values
                example: [
                            {'result': 1, 'Age': 0, 'Size': 0, 'Color': 0, 'Act': 0},
                            {'result': 0, 'Age': 1, 'Size': 0, 'Color': 0, 'Act': 0}
                          ]
    :return:
    - data: Excel data convert to binary form
    - tmp_dict: dictionary that contains as keys the attributes and as values a dict with
                possible values for attribute
    """

    tmp_dict = {'result': {'True': 1, 'False': 0}}
    for instance in data:
        for key, value in instance.items():
            if key not in tmp_dict:
                tmp_dict[key] = {}
            if tmp_dict[key] == {}:
                tmp_dict[key][value] = 0
            elif value in tmp_dict[key]:
                pass
            else:
                max_value = max(tmp_dict[key], key=tmp_dict[key].get)
                tmp_dict[key][value] = tmp_dict[key][max_value] + 1
            instance[key] = tmp_dict[key][value]

    return data, tmp_dict


def calc_performance(binary_data, header, nb, ce, sv):
    """
    Calculate confusion matrix
    :param binary_data: binary data - list of dicts
    :param header: header - list
    :param nb: Naive Bayes object
    :param ce: Candidate Elimination object
    :param sv: Support Vector Object
    :return:
    - confusion_matrix: a dictionary that contains for each classifier the following attributes:
    tn: True  - negative
    fp: False - positive
    fn: False - negative
    tp: True  - positive
    """
    confusion_matrix = {'nb': {'tn': 0, 'fp': 0, 'fn': 0, 'tp': 0},
                        'ce': {'tn': 0, 'fp': 0, 'fn': 0, 'tp': 0},
                        'sv': {'tn': 0, 'fp': 0, 'fn': 0, 'tp': 0}
                        }

    for d in binary_data:
        single_record = [[]]
        for i in header:
            result = d['result']
            single_record[0].append(d[i])

        nb_result = nb.prediction(single_record)[0]
        if result == 1:
            if nb_result == 1:
                confusion_matrix['nb']['tp'] += 1
            else:
                confusion_matrix['nb']['fn'] += 1
        else:
            if nb_result == 1:
                confusion_matrix['nb']['fp'] += 1
            else:
                confusion_matrix['nb']['tn'] += 1

        ce_result = ce.prediction(single_record)
        if result == 1:
            if ce_result == 1:
                confusion_matrix['ce']['tp'] += 1
            else:
                confusion_matrix['ce']['fn'] += 1
        else:
            if ce_result == 1:
                confusion_matrix['ce']['fp'] += 1
            else:
                confusion_matrix['ce']['tn'] += 1

        sv_result = sv.prediction(single_record)[0]
        if result == 1:
            if sv_result == 1:
                confusion_matrix['sv']['tp'] += 1
            else:
                confusion_matrix['sv']['fn'] += 1
        else:
            if sv_result == 1:
                confusion_matrix['sv']['fp'] += 1
            else:
                confusion_matrix['sv']['tn'] += 1

    return confusion_matrix


def calc_accuracy(tn, fp, fn, tp):
    """
    Calc accuracy.
    if raise a ZeroDivisionError exception, return 0
    :param tn: True  - negatives
    :param fp: False - positives
    :param fn: False - negatives
    :param tp: True  - positives
    :return: accuracy
    """

    try:
        accuracy = (tp + tn) / (tn + fp + fn + tp)
        return accuracy
    except ZeroDivisionError:
        return 0


def calc_specificity(tn, fp):
    """
    Calc specificity.
    if raise a ZeroDivisionError exception, return 0
    :param tn: True  - negatives
    :param fp: False - positives
    :return: specificity
    """

    try:
        specificity = tn / (tn + fp)
        return specificity
    except ZeroDivisionError:
        return 0


def calc_sensitivity(tp, fn):
    """
    Calc sensitivity
    :param tp: True  - positives
    :param fn: False - negatives
    :return: sensitivity
    """

    try:
        sensitivity = tp / (tp + fn)
        return sensitivity
    except ZeroDivisionError:
        return 0


def calc_precision(fp, tp):
    """
    Calc precision.
    If raise a ZeroDivisionError exception, return 0
    :param fp: False - positives
    :param tp: True  - positives
    :return: precision
    """

    try:
        precision = tp / (fp + tp)
        return precision
    except ZeroDivisionError:
        return 0


def calc_prevalence(tn, fp, fn, tp):
    """
    Calc prevalence.
    If raise a ZeroDivisionError exception, return 0
    :param tn: True  - negatives
    :param fp: False - positives
    :param fn: False - negatives
    :param tp: True  - positives
    :return: prevalence
    """

    try:
        prevalence = (fn + tp) / (tn + fp + fn + tp)
        return prevalence
    except ZeroDivisionError:
        return 0


def write_charts(value_list):
    """
    Write in an Excel file all performance params and draws a column chart.
    :param value_list:
    """

    # init xls file
    workbook = xlsxwriter.Workbook('Performance_recap.xls')
    worksheet = workbook.add_worksheet()

    # set styles and format
    worksheet.set_column(0, 4, 25)
    center_bold = workbook.add_format({'bold': 1, 'align': 'center'})
    center = workbook.add_format({'align': 'center'})

    # prepare list for write Excel file
    headings = ['Parameters', 'Naive Bayes', 'Candidate Elimination', 'Support Vector']
    column = ['Accuracy', 'Specificity', 'Precision', 'Prevalence', 'Sensitivity']

    # Create a new chart
    chart = workbook.add_chart({'type': 'column'})

    # write row and columns
    worksheet.write_row('A1', headings, center_bold)
    worksheet.write_column('A2', column)
    worksheet.write_column('B2', value_list[0], center)
    worksheet.write_column('C2', value_list[1], center)
    worksheet.write_column('D2', value_list[2], center)

    # configure the chart
    chart.add_series({'name': 'Naive Bayes', 'values': '=Sheet1!$B$2:$B$6', 'categories': '=Sheet1!$A$2:$A$6'})
    chart.add_series({'name': 'Candidate Elimination', 'values': '=Sheet1!$C$2:$C$6', 'categories': '=Sheet1!$A$2:$A$6'})
    chart.add_series({'name': 'Support Vector', 'values': '=Sheet1!$D$2:$D$6', 'categories': '=Sheet1!$A$2:$A$6'})

    # set title and axis's names
    chart.set_title({'name': 'Results of performance analysis'})
    chart.set_x_axis({'name': 'Performance parameters'})
    chart.set_y_axis({'name': 'Values'})

    chart.set_style(11)

    # insert the chart into the worksheet.
    worksheet.insert_chart('A9', chart)

    # close file
    workbook.close()
