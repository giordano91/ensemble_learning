#! /usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (C) 2015-2016, Giordano Sala

from src import support_functions
from src.naive_bayes import CalcNaiveBayes
from src.candidate_elimination import CalcCandidateElimination
from src.support_vector import CalcSupportVector
from termcolor import *

if __name__ == "__main__":

    # possible data training
    matrix_files = {
        '1': 'src/data/data_balloons.xls',
        '2': 'src/data/enjoy_sport.xlsx',
        '3': 'src/data/economic_car.xls',
        '4': 'src/data/breast_cancer.xls',
    }

    answers_list = ['1', '2', '3', '4', 'q']

    while True:
        cprint("****** ENSEMBLE LEARNING ******", 'blue')
        cprint("Choose data training:\n"
               "1 -> Data balloons\n"
               "2 -> Enjoy sport\n"
               "3 -> Economic car\n"
               "4 -> Breast cancer\n"
               "q -> Quit", 'green')
        cprint("*** - *** - *** - *** - *** - ***", 'blue')

        answer = input()
        if answer not in answers_list:
            cprint("Choice not allowed", 'red')
            continue
        if answer == 'q':
            break
        cprint("*** - *** - *** - *** - *** - ***", 'blue')

        # load data training
        print("Read data from Excel files ...")
        real_data, header = support_functions.read_data(matrix_files[answer])
        binary_data, total_values = support_functions.convert_data(real_data)
        print("Done!")
        cprint("*** - *** - *** - *** - *** - ***", 'blue')

        # prepare data
        print("Preparing data ...")
        data, target = support_functions.prepare_data(binary_data, header)
        print("Done!")
        cprint("*** - *** - *** - *** - *** - ***", 'blue')

        # Naive Bayes section
        print("Naive Bayes training ...")
        nb = CalcNaiveBayes()
        nb.training(data, target)
        print("Done!")
        cprint("*** - *** - *** - *** - *** - ***", 'blue')

        # Candidate Elimination section
        print("Candidate Elimination training ...")
        ce = CalcCandidateElimination(data, target)
        ce.candidate_elimination()
        print("Done!")
        cprint("*** - *** - *** - *** - *** - ***", 'blue')

        # Support Vector
        print("Support Vector training ...")
        sv = CalcSupportVector()
        sv.training(data, target)
        print("Done!")
        cprint("*** - *** - *** - *** - *** - ***", 'blue')
        cprint("*** - *** - *** - *** - *** - ***", 'blue')

        # Calculate performance indexes
        confusion_matrix = support_functions.calc_performance(binary_data, header, nb, ce, sv)

        possibilities = ['nb', 'ce', 'sv']
        full_list = []
        for possibility in possibilities:
            single_list = []
            acc = support_functions.calc_accuracy(confusion_matrix[possibility]['tn'],
                                                  confusion_matrix[possibility]['fp'],
                                                  confusion_matrix[possibility]['fn'],
                                                  confusion_matrix[possibility]['tp'])

            single_list.append(acc)

            spec = support_functions.calc_specificity(confusion_matrix[possibility]['tn'],
                                                      confusion_matrix[possibility]['fp'])

            single_list.append(spec)

            prec = support_functions.calc_precision(confusion_matrix[possibility]['tn'],
                                                    confusion_matrix[possibility]['fp'])

            single_list.append(prec)

            prev = support_functions.calc_prevalence(confusion_matrix[possibility]['tn'],
                                                     confusion_matrix[possibility]['fp'],
                                                     confusion_matrix[possibility]['fn'],
                                                     confusion_matrix[possibility]['tp'])

            single_list.append(prev)

            sens = support_functions.calc_sensitivity(confusion_matrix[possibility]['tn'],
                                                      confusion_matrix[possibility]['fp'])

            single_list.append(sens)

            full_list.append(single_list)

        support_functions.write_charts(full_list)

        # Start predictions
        print("Choose attributes to predict a new record")
        error_found = False
        new_record = [[]]
        for col in header:
            tmp_list = [sorted(total_values[col].items(), key=lambda x: x[1])]
            cprint("Attribute {}".format(col), 'green')
            for pair in tmp_list[0]:
                cprint("{} -> {}".format(pair[1], pair[0]), 'green')
            try:
                attr_answer = input()
                new_record[0].append(int(attr_answer))
                if int(attr_answer) not in [i for i in range(len(tmp_list[0]))]:
                    raise ValueError
            except ValueError:
                cprint("Choice not allowed", "red")
                error_found = True
                break
            cprint("*** - *** - *** - *** - *** - ***", 'blue')

        if error_found:
            continue

        # Show results
        final_results = [nb.prediction(new_record)[0], ce.prediction(new_record), sv.prediction(new_record)[0]]

        print("Naive Bayes result {}".format(True if nb.prediction(new_record)[0] == 1 else False))
        print("Candidate Elimination result {}".format(True if ce.prediction(new_record) == 1 else False))
        print("Support Vector result {}".format(True if sv.prediction(new_record)[0] == 1 else False))

        # Judge
        false_values = final_results.count(0)
        true_values = final_results.count(1)

        if true_values > false_values:
            cprint("Judge says True", 'blue')
        else:
            cprint("Judge says False", 'blue')

        cprint("Performance results are stored in 'Performance_recap.xls' file \n"
               "[dir {}]".format(os.path.abspath("Performance_recap.xls")), 'blue')

        cprint("Run again? [y/n]", 'green')
        another_one = input()
        if another_one == 'n':
            break
        elif another_one not in ['y', 'n']:
            cprint("Choice not allowed", 'red')
