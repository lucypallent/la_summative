# -*- coding: utf-8 -*-
"""download_train_set.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1L5iKCExjMRE3P51wlmUcAh7v1a3_Ob0O
"""

import pandas as pd
url='https://drive.google.com/file/d/1F0-Rr9MPu2Ji2ZIuWpmT2iWc_cGYTy3Z/view?usp=sharing'
url='https://drive.google.com/uc?id=' + url.split('/')[-2]

df = pd.read_csv(url)

df.to_csv('train_set.csv')