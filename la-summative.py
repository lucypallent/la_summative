#!/usr/bin/env python
# coding: utf-8

# # Create train_set dataset
# saving it to downloads currently

# In[5]:


# pip uninstall pandas
get_ipython().system('pip install pandas')


# In[6]:


get_ipython().system('pip install pandas')


# In[9]:


get_ipython().system('pip install pandas')


# In[8]:


import pandas as pd


# In[7]:


import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# CMA ##
CMA = pd.read_csv(r'C:\\Users\\kfps86\\Downloads\\CMA_train_set2.csv')


# CMA_s ##
CMA_s = pd.read_csv(r'C:\\Users\\kfps86\\Downloads\\train_set_CMA_correct_subject2.csv')

# unique_questions ##
unique_questions = pd.read_csv(r'C:\\Users\\kfps86\\Downloads\\unique_questions2.csv')

# day_count_train_set2 ##
day_count_train_set2 = pd.read_csv(r'C:\\Users\\kfps86\\Downloads\\day_count_train_set2.csv')

# train_set ##
train_set = pd.read_csv(r'C:\\Users\\kfps86\\Downloads\\train_set_draft_1.csv')

# question
question = pd.read_csv(r'C:\\Users\\kfps86\\Downloads\\dataset\\question_metadata.csv')


# need to change DateAnswered and DateOfBirth columns to datetime format
train_set['DateAnswered'] = pd.to_datetime(train_set['DateAnswered'], format='%Y-%m-%d %H:%M:%S.%f')
train_set['DateOfBirth'] = pd.to_datetime(train_set['DateOfBirth'], format='%Y-%m-%d %H:%M:%S.%f')

# change SubjectId to list format
question['SubjectId'] = question['SubjectId'].str.strip('[]').str.split(',')

# Merge datasets
train_set = train_set.merge(CMA['AnswerId', 'CMA'], how='inner', on=['AnswerId'])
train_set = train_set.merge(CMA_s['AnswerId', 'CMA_correct_subject'], how='inner', on=['AnswerId'])
train_set = train_set.merge(unique_questions['QuestionId', 'total_q_answered'], how='inner', on=['QuestionId'])
train_set = train_set.merge(day_count_train_set2['AnswerId', 'holiday', 'unique_day', 'yr_2'], how='inner', on=['AnswerId'])
train_set = train_set.merge(question['QuestionId', 'SubjectId'], how='inner', on=['QuestionId'])

train_set.to_csv(r'C:\\Users\\kfps86\\Downloads\\train_set.csv')
train_set.head()


# In[ ]:


# delt

