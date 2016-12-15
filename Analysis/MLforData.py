#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Created on  12/11/16 23:06 PM

@author: IMYin

@File: MLforData.py
"""
import pandas as pd
import tushare as ts
import numpy as np
from sklearn.linear_model.logistic import LogisticRegression

def process_data(code):
    df = ts.get_k_data(retry_count=10)
    y = np.sign(df['close'] - df['open'])
    X = df['close', 'open', 'high', 'low', 'volume']
    return df, X, y

df,X,y = process_data('000382')
classifier = LogisticRegression()
classifier.fit(X,y)
predictions = classifier.predict()
for i, prediction in enumerate(predictions[-5:]):
    print 'Prediction: %s. Message: %s' % (prediction, X_test_raw.iloc[i])
