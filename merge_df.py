import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import visdom

# connect to visdom
vis = visdom.Visdom(server='http://ncc1.clients.dur.ac.uk', port=7234, env='LA')

# CMA ##
url = 'https://drive.google.com/file/d/1-3XCYN4jh79xdDNnDiOZxk21C6wCvFkW/view?usp=sharing'
path = 'https://drive.google.com/uc?export=download&id='+url.split('/')[-2]
CMA = pd.read_csv(path)

# CMA_s ##
url = 'https://drive.google.com/file/d/1-FiYPZQJQHgdv_6VwSGQwHjS9mvZxCph/view?usp=sharing'
path = 'https://drive.google.com/uc?export=download&id='+url.split('/')[-2]
CMA_s = pd.read_csv(path)

# unique_questions ##
url = 'https://drive.google.com/file/d/1-E2vDCWZqPIcy4WnlNy7NfPzRNK27fB_/view?usp=sharing'
path = 'https://drive.google.com/uc?export=download&id='+url.split('/')[-2]
unique_questions = pd.read_csv(path)

# day_count_train_set2 ##
url = 'https://drive.google.com/file/d/1-G-l-LCqqJSCx7AQKP7BAN5p44Fiaw6w/view?usp=sharing'
path = 'https://drive.google.com/uc?export=download&id='+url.split('/')[-2]
day_count_train_set2 = pd.read_csv(path)

# train_set ##
url = 'https://drive.google.com/file/d/11w6bWPVH0OR6N9vLNfaF7-pCN45rTrrf/view?usp=sharing'
path = 'https://drive.google.com/uc?export=download&id='+url.split('/')[-2]
train_set = pd.read_csv(path)

# need to change DateAnswered and DateOfBirth columns to datetime format
train_set['DateAnswered'] = pd.to_datetime(train_set['DateAnswered'], format='%Y-%m-%d %H:%M:%S.%f')
train_set['DateOfBirth'] = pd.to_datetime(train_set['DateOfBirth'], format='%Y-%m-%d %H:%M:%S.%f')

# Merge datasets
train_set = train_set.merge(CMA['AnswerId', 'CMA'], how='inner', on=['AnswerId'])
train_set = train_set.merge(CMA_s['AnswerId', 'CMA_correct_subject'], how='inner', on=['AnswerId'])
train_set = train_set.merge(unique_questions['QuestionId', 'total_q_answered'], how='inner', on=['QuestionId'])
train_set = train_set.merge(day_count_train_set2['AnswerId', 'holiday', 'unique_day', 'yr_2'], how='inner', on=['AnswerId'])

train_set.to_csv('train_set.csv')
