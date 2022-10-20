from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from sklearn.model_selection import TimeSeriesSplit, GridSearchCV
from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QWidget
from xgboost import XGBRegressor
import matplotlib.pyplot as plt
from PyQt5 import QtWidgets
import pandas as pd
import numpy as np
import sqlite3
import datetime

database_dir = 'test1.sqlite'
files_directory = 'Stocks'
tab_name = 'Tabela1'


class SecondWindow(QMainWindow):
    def __init__(self):
        super(SecondWindow, self).__init__()
        self.main_widget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.main_widget)
        layout = QtWidgets.QVBoxLayout(self.main_widget)
        wp = WidgetPlot()
        layout.addWidget(wp)


class WidgetPlot(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        self.setLayout(QVBoxLayout())
        self.canvas = MyMplCanvas(self)
        self.toolbar = NavigationToolbar(self.canvas, self)
        self.layout().addWidget(self.toolbar)
        self.layout().addWidget(self.canvas)


class MyMplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=930, height=540, company_list=['msft'],
                 pred_start_date=pd.to_datetime('2010-01-01'), pred_end_date=pd.to_datetime('2012-01-01'),
                 means=(5, 20, 50, 200), train_since=None, pred_every=None):
        self.fig, self.ax = plt.subplots(nrows=len(company_list), ncols=1, sharex=True)
        if len(company_list) == 1:
            self.ax = [self.ax]
        # fig = Figure(figsize=(width, height))
        # self.axes = fig.add_subplot(111)
        self.compute_figure(company_list=['msft'], pred_start_date=pd.to_datetime('2010-01-01'),
                            pred_end_date=pd.to_datetime('2012-01-01'), means=(5, 20, 50, 200), train_since=None,
                            pred_every=None)

        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def compute_figure(self, company_list=['msft'], pred_start_date=pd.to_datetime('2010-01-01'),
                       pred_end_date=pd.to_datetime('2012-01-01'), means=(5, 20, 50, 200), train_since=None,
                       pred_every=None):

        if type(pred_start_date) not in (pd.Timestamp, datetime.datetime):
            print('\npred_start_date expected types: pandas.Timestamp, datetime.datetime. Got {}'.format(
                type(pred_start_date)))
            exit(100)
        if type(pred_end_date) not in (pd.Timestamp, datetime.datetime):
            print('\npred_end_date expected types: pandas.Timestamp, datetime.datetime. Got {}'.format(
                type(pred_end_date)))
            exit(101)
        if type(train_since) not in (pd.Timestamp, datetime.datetime, type(None)):
            print(
                '\ntrain_since expected types: pandas.Timestamp, datetime.datetime, NoneType (disabled). Got {}'.format(
                    type(train_since)))
            exit(102)
        if type(pred_every) not in (datetime.timedelta, type(None)):
            print('\npred_every expected types: datetime.timedelta (days > 0), NoneType (disabled). Got {}'.format(
                type(pred_every)))
            exit(103)
        elif type(pred_every) == datetime.timedelta and pred_every.days <= 0:
            print('\npred_every expected datetime.timedelta with days > 0')
            exit(104)

        try:
            for num in means:
                if type(num) is not int:
                    print('\nmeans expected iterable of ints. Inside iterable got {}'.format(type(num)))
                    exit(106)
        except TypeError:
            print('\nmeans expected iterable of ints. Got {}'.format(type(means)))
            exit(105)

        if train_since is None and pred_end_date <= pred_start_date:
            print('\npred_end_date has to be after pred_start_date')
            exit(107)

        if train_since is not None and not ((pred_end_date > pred_start_date) and (pred_start_date > train_since)):
            print('\npred_end_date has to be after pred_start_date, which has to be after train_since')
            exit(107)

        global files_directory, database_dir, tab_name
        con = sqlite3.connect(database_dir)
        results_data = pd.DataFrame()
        pred_start_copy = pred_start_date
        for company_symbol in company_list:
            try:
                comp_data = pd.read_sql_query(
                    'SELECT Date, Close FROM {} WHERE "company name" = "{}"'.format(tab_name, company_symbol), con)
            except pd.errors.DatabaseError:
                print('\nTable {} could not be found in database {}'.format(tab_name, database_dir))
                exit(110)

            comp_data.set_index('Date', inplace=True)
            comp_data.index = pd.to_datetime(comp_data.index, format='%Y-%m-%d')
            close_name = 'Close_' + company_symbol
            comp_data = comp_data.rename(columns={'Close': close_name})
            comp_data['change%'] = comp_data[close_name] / comp_data[close_name].shift(1)

            fluct_list = []
            for num in means:
                comp_data['Rolling_' + str(num)] = comp_data[close_name].rolling(num).mean().shift(1)
                comp_data['Fluctuation_' + str(num)] = comp_data[close_name].shift(1) / comp_data['Rolling_' + str(num)]
                fluct_list.append('Fluctuation_' + str(num))
            comp_data = comp_data.dropna()

            if train_since is None:
                to_model = comp_data[comp_data.index < pred_start_date]
            else:
                to_model = comp_data[(comp_data.index < pred_start_date) & (comp_data.index >= train_since)]

            if len(to_model) < 10:
                print(
                    '\nNot enough records found for company {} (table {} in database {}). Found {} records matching given dates'.
                    format(company_symbol, tab_name, database_dir, str(len(to_model))))
                exit(111)

            X = to_model[fluct_list]
            y_tree = to_model['change%']
            tree_params = {'max_depth': [2, 3, 4], 'colsample_bytree': [0.2, 0.3, 0.4], 'eta': np.arange(0.3, 0.6, 0.1)}
            tree = XGBRegressor(booster='gbtree', n_estimators=1000)

            model_tree = GridSearchCV(tree, param_grid=tree_params, scoring='neg_mean_squared_error', n_jobs=-1,
                                      cv=TimeSeriesSplit(n_splits=5, max_train_size=100))
            model_tree.fit(X, y_tree)
            results_data = pd.concat([results_data, comp_data[[close_name]]], axis=1)
            cols = [close_name]

            while pred_start_date < pred_end_date:
                comp_data_predict = comp_data.copy(deep=True)
                for index, _ in comp_data_predict[(comp_data_predict.index >= pred_start_date) & (
                        comp_data_predict.index <= pred_end_date)].iterrows():
                    row_frame = comp_data_predict.loc[index:index, fluct_list]
                    comp_data_predict.at[index, 'change%'] = model_tree.predict(row_frame)
                    comp_data_predict.at[index, close_name] = comp_data_predict.at[index, 'change%'] * \
                                                              comp_data_predict[close_name].shift(1).at[index]
                    for num in means:
                        comp_data_predict['Rolling_' + str(num)] = comp_data_predict[close_name].rolling(
                            num).mean().shift(1)
                        comp_data_predict['Fluctuation_' + str(num)] = comp_data_predict[close_name].shift(1) / \
                                                                       comp_data_predict['Rolling_' + str(num)]

                comp_data_predict = comp_data_predict[
                    (comp_data_predict.index >= pred_start_date) & (comp_data_predict.index <= pred_end_date)]
                comp_data_predict[close_name] = comp_data_predict[close_name].rolling(20).mean().fillna(
                    comp_data_predict[close_name])
                results_data = results_data.merge(comp_data_predict[close_name], how='outer', left_index=True,
                                                  right_index=True,
                                                  suffixes=('', '_pred_' + pred_start_date.strftime('%Y-%m-%d')))
                cols.append(close_name + '_pred_' + pred_start_date.strftime('%Y-%m-%d'))
                if pred_every is None:
                    break
                else:
                    pred_start_date += pred_every
            pred_start_date = pred_start_copy
            for col in cols:
                self.ax[company_list.index(company_symbol)].plot(results_data.loc[pred_start_date:pred_end_date].index,
                                                                 results_data.loc[pred_start_date:pred_end_date, col],
                                                                 label=col)
                self.ax[company_list.index(company_symbol)].grid(axis='both', color='0.95')
            self.ax[company_list.index(company_symbol)].legend()
        con.close()
        plt.xticks(rotation=45)
