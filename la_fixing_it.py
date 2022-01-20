# -*- coding: utf-8 -*-
"""LA-fixing it.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1M6yNG-C6cCaGtKujomq38VrgW-M4oVTC
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import datetime
import numpy as np
import visdom

# connect to visdom
vis = visdom.Visdom(server='http://ncc1.clients.dur.ac.uk', port=7234, env='LA-log-reg-0')

# import the datasets
question = pd.read_csv(r'question_metadata.csv')
answers = pd.read_csv(r'answers_metadata.csv')
student = pd.read_csv(r'student_metadata.csv')
subject = pd.read_csv(r'subject_metadata.csv')
training = pd.read_csv(r'training.csv')

# create a test_train split
from sklearn.model_selection import train_test_split
# np.random.seed(42)
train_set, test_set = train_test_split(training, test_size=0.2, random_state=42)

answers = answers.dropna(subset=['AnswerId']) 
# 7 values in AnswerId are na (out of 19834820), hence we are droppping those 7 values
answers['AnswerId'] = answers['AnswerId'].astype(int)

# merge the datasets
train_set = train_set.merge(answers , how='inner', on='AnswerId')
train_set = train_set.merge(student, how='inner', on='UserId')
train_set = train_set.merge(question, how='inner', on='QuestionId')

# drop nans
train_set.dropna(inplace=True)

# Data Cleaning
# need to change DateAnswered and DateOfBirth columns to datetime format
train_set['DateAnswered'] = pd.to_datetime(train_set['DateAnswered'], format='%Y-%m-%d %H:%M:%S.%f')
train_set['DateOfBirth'] = pd.to_datetime(train_set['DateOfBirth'], format='%Y-%m-%d %H:%M:%S.%f')

# change SubjectId to list format
train_set['SubjectId'] = train_set['SubjectId'].str.strip('[]').str.split(',')

# https://stackoverflow.com/questions/45312377/how-to-one-hot-encode-from-a-pandas-column-containing-a-list
from sklearn.preprocessing import MultiLabelBinarizer
# create a one hot encoding column for each category
# uses up a lot of RAM though
mlb = MultiLabelBinarizer(sparse_output=True)

train_set = train_set.join(
            pd.DataFrame.sparse.from_spmatrix(
                mlb.fit_transform(train_set.pop('SubjectId')),
                index=train_set.index,
                columns=mlb.classes_))

# based on: https://github.com/ageron/handson-ml2/blob/master/02_end_to_end_machine_learning_project.ipynb
from sklearn.base import BaseEstimator, TransformerMixin

class CombinedAttributesAdder(BaseEstimator, TransformerMixin):
#     def __init__(self): # no *args or **kargs
    def fit(self, train_set, y=None):
        return self  # nothing else to do
    def transform(self, train_set):
        
        # cat => numerical value # 'total_answered',
        train_set['total_answered'] = train_set.groupby(['UserId'])['IsCorrect'].transform('count')

        # cat => numerical value # 'prop_correct',
        train_set['total_correct'] = train_set.groupby(['UserId'])['IsCorrect'].transform('sum')
        train_set['prop_correct'] = train_set['total_correct'] / train_set['total_answered']
#         train_set.drop('total_correct', inplace=True)

        # cat / numerical => numerical valueCMA
        train_set.sort_values(['UserId', 'DateAnswered'], inplace=True)
        CMA = train_set.groupby(['UserId']).IsCorrect.expanding().mean()
        train_set['CMA'] = CMA.reset_index(level=0, drop=True)

        # 'total_q_answered',
        train_set['total_q_answered'] = train_set.groupby(['QuestionId'])['QuestionId'].transform('count')

        # lvl2 - needs SubjectId first
        train_set['lvl2'] = 0
        for i in [' 101', ' 1156', ' 119', ' 149', ' 151', ' 32', ' 49', ' 692', ' 71']:
            if i in train_set.columns.tolist():
                i_int = (int(i[1:]))
                train_set['lvl2'] = train_set['lvl2'] + (train_set[i] * i_int)

        # CMA_correct_subject - need lvl2 first
        CMA_correct_subject = train_set.groupby(['UserId', 'lvl2']).IsCorrect.expanding().mean()
        train_set['CMA_correct_subject'] = CMA_correct_subject.reset_index(level=[0,1], drop=True)

        # 'holiday',
        train_set['holiday'] = 1
        train_set.loc[((train_set['DateAnswered'] < '2018-10-20') & (train_set['DateAnswered'] > '2018-09-03')) |
              ((train_set['DateAnswered'] > '2018-10-28') & (train_set['DateAnswered'] < '2018-12-20')) |
              ((train_set['DateAnswered'] > '2019-01-02') & (train_set['DateAnswered'] < '2019-02-16')) |
              ((train_set['DateAnswered'] > '2019-02-24') & (train_set['DateAnswered'] < '2019-04-06')) |
              ((train_set['DateAnswered'] > '2019-04-22') & (train_set['DateAnswered'] < '2019-05-25')) |
              ((train_set['DateAnswered'] > '2019-06-02') & (train_set['DateAnswered'] < '2019-07-25')) |

              ((train_set['DateAnswered'] > '2019-09-01') & (train_set['DateAnswered'] < '2019-10-19')) |
              ((train_set['DateAnswered'] > '2019-10-27') & (train_set['DateAnswered'] < '2019-12-20')) |
              ((train_set['DateAnswered'] > '2020-01-05') & (train_set['DateAnswered'] < '2020-02-15')) |
              ((train_set['DateAnswered'] > '2020-02-23') & (train_set['DateAnswered'] < '2020-04-03')) |
              ((train_set['DateAnswered'] > '2020-04-19') & (train_set['DateAnswered'] < '2020-05-23')) |
              ((train_set['DateAnswered'] > '2020-05-31') & (train_set['DateAnswered'] < '2020-07-23')) 
              ,'holiday'] = 0
        
        # 'unique_day',
        unique_student_train = pd.DataFrame(data=train_set['UserId'].unique(), columns=['UserId'])
        unique_student_train['unique_day'] = 0
        for i in range(len(unique_student_train)):
                unique_student_train.iloc[i, 1] =  len(train_set.loc[train_set['UserId']==unique_student_train.iloc[i, 0]]['DateAnswered'].dt.normalize().unique())
        train_set = train_set.merge(unique_student_train, how='inner', on='UserId')
        del unique_student_train
        import gc
        gc.collect()

        # 'yr2',
        train_set['yr2'] = 1
        train_set.loc[(train_set['DateAnswered'] < '2019-09-01'), 'yr2'] = 0

        # 'age',
        train_set['age'] = train_set['DateAnswered'] - train_set['DateOfBirth'] 

        # 'term',
        train_set['term'] = 6

        train_set.loc[((train_set['DateAnswered'] >= '2018-09-04') & (train_set['DateAnswered'] < '2018-10-29')) |
                      ((train_set['DateAnswered'] >= '2019-09-02') & (train_set['DateAnswered'] < '2019-10-28')),
                      'term'] = 1

        train_set.loc[((train_set['DateAnswered'] >= '2018-10-29') & (train_set['DateAnswered'] < '2019-01-03')) |
                      ((train_set['DateAnswered'] >= '2019-10-28') & (train_set['DateAnswered'] < '2020-01-06')),
                      'term'] = 2

        train_set.loc[((train_set['DateAnswered'] >= '2019-01-03') & (train_set['DateAnswered'] < '2019-02-25')) |
                      ((train_set['DateAnswered'] >= '2020-01-06') & (train_set['DateAnswered'] < '2020-02-24')),
                      'term'] = 3

        train_set.loc[((train_set['DateAnswered'] >= '2019-02-25') & (train_set['DateAnswered'] < '2019-04-23')) |
                      ((train_set['DateAnswered'] >= '2020-02-24') & (train_set['DateAnswered'] < '2020-04-20')),
                      'term'] = 4

        train_set.loc[((train_set['DateAnswered'] >= '2019-04-23') & (train_set['DateAnswered'] < '2019-06-03')) |
                      ((train_set['DateAnswered'] >= '2020-04-20') & (train_set['DateAnswered'] < '2020-06-01')),
                      'term'] = 5

        # 'time',
        train_set['time'] = 4
        train_set.loc[(train_set['DateAnswered'].dt.strftime("%H:%M:%S") >= '08:00:00') &
                      (train_set['DateAnswered'].dt.strftime("%H:%M:%S") < '12:00:00')
                       , 'time'] = 1

        train_set.loc[(train_set['DateAnswered'].dt.strftime("%H:%M:%S") >= '12:00:00') &
                      (train_set['DateAnswered'].dt.strftime("%H:%M:%S") < '16:00:00')
                       , 'time'] = 2

        train_set.loc[(train_set['DateAnswered'].dt.strftime("%H:%M:%S") >= '16:00:00') &
                      (train_set['DateAnswered'].dt.strftime("%H:%M:%S") < '20:00:00')
                       , 'time'] = 3

        # 'is_weekend',
        train_set['is_weekend'] = 0
        train_set.loc[train_set['DateAnswered'].dt.dayofweek > 4, 'is_weekend'] = 1

        # 'last_answered', adds repeat as well
        train_set.sort_values(['UserId', 'DateAnswered'], inplace=True)
        train_set['last_answered'] = train_set['DateAnswered'] - datetime.datetime.strptime('2018-09-01 00:00:00', '%Y-%m-%d %H:%M:%S')
        train_set['repeat'] = (train_set['UserId']==train_set['UserId'].shift(1))
        train_set.loc[train_set['repeat'] == True, 'last_answered'] = train_set['DateAnswered'].diff()
        train_set.loc[train_set['repeat']==False, 'repeat'] = 0
        train_set.loc[train_set['repeat']==True, 'repeat'] = 1
        
        # get rid of values
        train_set.drop('IsCorrect', axis=1, inplace=True)

        # think issue is here
        train_set['DateAnswered'] = train_set['DateAnswered'].values.astype('float')
        train_set['DateOfBirth'] = train_set['DateOfBirth'].values.astype('float')
        train_set['last_answered'] = train_set['last_answered'].values.astype('float')
        train_set['age'] = train_set['age'].values.astype('float')

        # train_set.drop('DateAnswered', axis=1, inplace=True) # added
        # train_set.drop('DateOfBirth', axis=1, inplace=True) # added
            
        return train_set

attr_adder = CombinedAttributesAdder()

# prep data for ML algos
# they use strat_train_set - think should do this based on confidence value
# getting equal missing values
IsCorrect = train_set.drop('IsCorrect', axis=1)
IsCorrect_labels = train_set['IsCorrect'].copy()
AnswerValue = train_set.drop('AnswerValue', axis=1)
AnswerValue_labels = train_set['AnswerValue'].copy()

from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer

all_attribs = list(train_set)

training_extra_attribs = attr_adder.transform(train_set)

cat_attribs = ['QuestionId', 'UserId', 'AnswerId', 'CorrectAnswer', 'AnswerValue',
               'Confidence', 'Gender', 'PremiumPupil', 'lvl2', 'holiday', 'yr2',
               'term', 'time', 'is_weekend', 'repeat']

num_attribs = list(training_extra_attribs.drop(cat_attribs, axis=1))

full_pipeline = ColumnTransformer([
        # ('all', CombinedAttributesAdder(), all_attribs),
        ('num', StandardScaler(with_mean=False), num_attribs),
        ('cat', OneHotEncoder(), cat_attribs), # trying this as an extra but this should now work
    ])

IsCorrect_prepared = full_pipeline.fit_transform(training_extra_attribs)

"""# Simple log Reg Model

## Initial Run
log_reg_0 = LogisticRegression(C=1.0, penalty='l1', solver='liblinear')
"""

# note this actually has run successfully thank god
from sklearn.linear_model import LogisticRegression


from sklearn.metrics import mean_squared_error

"""## GridCV"""

from sklearn.model_selection import GridSearchCV

# param_grid = [{'penalty': ['l2', 'l1', 'elasticnet', 'none'],
#                'C': np.logspace(-3,3,3),
#                'solver': ['newton-cg', 'lbfgs', 'liblinear', 'sag', 'saga']}]



param_grid = [{'penalty': ['l1'],
               'C': np.logspace(-3,3,2),
               'solver': ['lbfgs']}]


log_reg = LogisticRegression(random_state=42)

# train across 5 folds, that's a total of (12+6)*5=90 rounds of training 
grid_search = GridSearchCV(log_reg, param_grid, cv=5,
                           scoring='neg_mean_squared_error',
                           return_train_score=True, verbose=2)

grid_search.fit(IsCorrect_prepared, IsCorrect_labels)

optimised_log_reg = grid_search.best_estimator_
score_log_reg = grid_search.best_score_

vis.text(optimised_log_reg)
vis.text(score_log_reg)

# """###Scores"""

# from sklearn.model_selection import cross_val_predict
# from sklearn.metrics import confusion_matrix
# from sklearn.metrics import accuracy_score
# from sklearn.metrics import f1_score

# def output_scores(labels, predictions):
#   conf_matrix = confusion_matrix(IsCorrect_labels, predictions)

#   acc = accuracy_score(labels, predictions, normalize=True)

#   f1 = f1_score(labels, predictions)

#   TP = conf_matrix[0,0]
#   TN = conf_matrix[1,1]
#   FP = conf_matrix[0,1]
#   FN = conf_matrix[1,0]

#   spec = TN / (TN + FP)

#   sens = TP / (TP + FN)

#   print('Confusion Matrix is: ')
#   print(conf_matrix)
#   print('Accuracy is: ' + str(acc))
#   print('F1 Score is: ' + str(f1))
#   print('Specicivity is: ' + str(spec))
#   print('Sensitivity is: ' + str(sens))

# # create log_reg_1 with the best paramaters

# # calculate the new scores
# output_scores(IsCorrect_labels, predictions)



# # """# Simple Random Forest Model

# # ## Initial Run
# # RandomForestRegressor(n_estimators=100, random_state=42)
# # """

# # from sklearn.ensemble import RandomForestRegressor

# # forest_reg_0 = RandomForestRegressor(n_estimators=100, random_state=42)
# # forest_reg_0.fit(IsCorrect_prepared, IsCorrect_labels)

# # forest_reg_0_predictions = forest_reg_0.predict(IsCorrect_prepared)
# # forest_0_mse = mean_squared_error(IsCorrect_labels, forest_reg_0_predictions)
# # forest_0_rmse = np.sqrt(forest_0_mse)
# # forest_0_rmse

# # """###Scores"""

# # output_scores(IsCorrect_labels, forest_reg_0_predictions)

# # asd

# # sd


