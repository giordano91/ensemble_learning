#Ensemble Learning
An example of ensemble learning composed by three classifiers:
- Naive Bayes
- Candidate Elimination
- Support Vector

Both, Naive Bayes and Support Vector, work with scikit-learn library, so were not developed from scratch.

The repository provides already 4 examples of data training (.xls and .xlsx).

The user can choose one of data training file and each classifier starts the learning phase.

After this, application allows the user to insert a new record in order to predict the final result.
Each classifier calculates a result and a “judge” decides to majority the final result.

At the end, the application calculates also 5 performance indexes:
- Accuracy
- Sensitivity
- Specificity
- Precision
- Prevalence

and writes them in an excel file.


#Requirements:
- Python 3 – 3.4.3
- termcolor – 1.1.0
- xlrd – 1.0.0
- xlsxwriter – 0.9.3
- scikit-learn – 0.17.1
- numpy – 1.11.2
- scipy – 0.18.1

