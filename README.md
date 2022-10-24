# Data Wizard

Project created by Maciej Matusiak and Jakub Kozłowski. Application based on the PyQt5 library and files with the Ui extension in order to create a fully functional mechanism for presenting statistical data. Application implements an XGBoost Random Forest Regressor model and presents forecasts graphically using subplots from matplotlib.pyplot.

# Division of responsibilites

Maciej Matusiak

- Designing and creating files and images that were later used in the application.
- Creating a simple error control to check the completness of the project.
- Implementation of database support within the login and registration mechanism.
- Creating a project structure based on OPP design paradigms.
- Implementation of SQL commands to maintain and edit the database.

Jakub Kozłowski

- Implementation of SQL commands with sqlite3 to query the database.
- Manipulation of pandas DataFrames, including filtering and merging dataframes, handling missing values in stocks data, calculating rolling means and deviations from trends for a group of records, etc.
- Creating an XGBoost regression model with grid search cross-validation on time series data and implementing it recursively to calculate future values.
- Creating a visualization of the model's forecasts in matplotlib.pyplot.
- Creating a simple error control to check the completness of the project.
