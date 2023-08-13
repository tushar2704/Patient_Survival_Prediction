# -*- coding: utf-8 -*-
"""Patient Survival Prediction

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1ar3_WoD_nUC5jXrb0m1JKopL9bMThuHy

# Patient Survival Prediction
## Author github.com/tushar2704

### Contents

- Introduction
- Exploratory Data Analysis
- Data Preprocessing
- Baseline Neural Network
- Hyperparameter Tuning
- Explainable AI
- Acknowledgements
- References

### Importing libraries
"""

# File system manangement
import time, psutil, os

# Mathematical functions
import math

# Data manipulation
import numpy as np
import pandas as pd

# Plotting and visualization
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
sns.set_theme()
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go

# Train-test split and k-fold cross validation
from sklearn.model_selection import train_test_split, KFold,  GridSearchCV

# Missing data imputation
from sklearn.impute import SimpleImputer

# Categorical data encoding
from sklearn.preprocessing import LabelEncoder

# Deep learning
import tensorflow as tf
from tensorflow import keras
from keras import layers
from keras.models import Sequential
from keras.layers import Dense

# Hyperparameter Tuning
!pip install -q -U keras-tuner
import keras_tuner as kt
from keras_tuner import HyperModel, Hyperband

# Model evaluation
from sklearn import metrics
from sklearn.metrics import accuracy_score
from sklearn.metrics import roc_auc_score
from sklearn.metrics import precision_score
from sklearn.metrics import recall_score
from sklearn.metrics import f1_score

# Model loading
from keras.models import load_model

# Explainable AI
!pip install shap
import shap

# Warning suppression
import warnings
warnings.filterwarnings('ignore')

# Recording the starting time, which will be complemented with a time check at the end, to compute the total runtime of the process
start = time.time()

"""<a name = "Introduction"></a>
# 1. Introduction

## Data

Source: https://journals.lww.com/ccmjournal/Citation/2019/01001/33__THE_GLOBAL_OPEN_SOURCE_SEVERITY_OF_ILLNESS.36.aspx
"""

# Loading the data
data = pd.read_csv('content/Dataset.csv')

# Memory usage
print("Memory usage: {0:.2f} MB".format(data.memory_usage().sum()/(1024*1024)))

# Printing the dataframe
data

"""## Project Objective

The medical records of a patient play a significant role in determining his/her survival odds to a substantial extent. In this project, the objective is to predict whether a patient will survive or not, based on various relevant medical information.

<a name = "Exploratory-Data-Analysis"></a>
# 2. Exploratory Data Analysis

- Understanding Features
- Basic Data Exploration
- Univariate Analysis
- Multivariate Analysis

<a name = "Understanding-Features"></a>
## 2.1. Understanding Features
"""

# Loading data description
data_dictionary = pd.read_csv('content/Dictionary.csv')

# Memory usage
print("Memory usage: {0:.2f} MB".format(data_dictionary.memory_usage().sum()/(1024*1024)))

# Printing the dataframe
data_dictionary

"""<a name = "Basic-Data-Exploration"></a>
## 2.2. Basic Data Exploration
"""

# Shape of the data
print(pd.Series({"Shape of the dataset": data.shape}).to_string())

# Count of observations
print(pd.Series({"Number of observations in the dataset": len(data)}).to_string())

# Count of columns
print(pd.Series({"Total number of columns in the dataset": len(data.columns)}).to_string())

# Column names
data.columns

# Column datatypes
print(data.dtypes)

# Count of column datatypes
cols_int = data.columns[data.dtypes == 'int64'].tolist()
cols_float = data.columns[data.dtypes == 'float64'].tolist()
cols_object = data.columns[data.dtypes == 'object'].tolist()
print(pd.Series({"Number of integer columns": len(cols_int),
                 "Number of float columns": len(cols_float),
                 "Number of object columns": len(cols_object)}).to_string())

# Count of duplicate rows
print(pd.Series({"Number of duplicate rows in the dataset": data.duplicated().sum()}).to_string())

# Count of duplicate columns
print(pd.Series({"Number of duplicate columns in the dataset": data.T.duplicated().sum()}).to_string())

# Constant columns
cols_constant = data.columns[data.nunique() == 1].tolist()
if len(cols_constant) == 0:
    cols_constant = "None"
print(pd.Series({"Constant columns in the dataset": cols_constant}).to_string())

# Count of columns with missing values
print(pd.Series({"Number of columns with missing values in the dataset": len(data.isna().sum()[data.isna().sum() != 0])}).to_string())

# Columns with missing values and respective proportions of values that are missing
print((data.isna().sum()/len(data))[data.isna().sum() != 0].sort_values(ascending = False))

# Statistical description of numerical variables in the dataset
data.describe()

# Statistical description of categorical variables in the dataset
data.describe(include = ['O'])

# Dropping constant columns
data.drop(cols_constant, axis = 1, inplace = True)
cols_int.remove('readmission_status')

"""**Dataset synopsis:**

- Number of observations: $91713$
- Number of columns: $186$
- Number of integer columns: $8$
- Number of float columns: $170$
- Number of object columns: $8$
- Number of duplicate observations: $0$
- Constant column: `readmission_status`
- Number of columns with missing values: $175$
- Columns with over $90\%$ missing values: `h1_bilirubin_max`, `h1_bilirubin_min`, `h1_lactate_min`, `h1_lactate_max`, `h1_albumin_max`
- Memory Usage: $130.15$ MB

<a name = "Univariate-Analysis"></a>
## 2.3. Univariate Analysis

- Target variable
- Predictor variables

In general, throughout the notebook, we choose the number of bins of a histogram by the [Freedman-Diaconis rule](https://en.wikipedia.org/wiki/Freedman%E2%80%93Diaconis_rule), which suggests the optimal number of bins to grow as $k \sim n^{1/3},$ where $n$ is the total number of observations.
"""

# Setting the number of bins
bins_fd = math.floor(len(data)**(1/3))

"""<a name = "Target-variable"></a>
### 2.3.1. Target variable

The target variable `hospital_death` is a binary variable indicating the survival status of a patient.
\begin{align*}
&0 \mapsto \text{patient survived}\\
&1 \mapsto \text{patient died}
\end{align*}
"""

# Function to construct barplot and donutplot of a dataframe column
def bar_donut(df, col, height = 500, width = 800, manual_title_text = False, title_text = "Frequency distribution"):
    fig = make_subplots(rows = 1, cols = 2, specs = [[{'type': 'xy'}, {'type': 'domain'}]])
    fig.add_trace(go.Bar(x = df[col].value_counts(sort = False).index.tolist(),
                         y = df[col].value_counts(sort = False).tolist(),
                         text = df[col].value_counts(sort = False).tolist(),
                         textposition = 'auto'),
                         row = 1, col = 1)
    fig.add_trace(go.Pie(values = df[col].value_counts(sort = False).tolist(),
                         labels = df[col].value_counts(sort = False).index.tolist(),
                         hole = 0.5, textinfo = 'label+percent', title = f"{col}"),
                         row = 1, col = 2)
    fig.update_layout(height = height, width = width, showlegend = False,
                      title = {'text': f"Frequency distribution of {col}",
                               'y': 0.95, 'x': 0.5, 'xanchor': 'center', 'yanchor': 'top'},
                      xaxis = dict(tickmode = 'linear', tick0 = 0, dtick = 1))
    if manual_title_text == True:
        fig.update_layout(height = height, width = width, showlegend = False,
                          title = {'text': title_text,
                                   'y': 0.95, 'x': 0.5, 'xanchor': 'center', 'yanchor': 'top'},
                          xaxis = dict(tickmode = 'linear', tick0 = 0, dtick = 1))
    fig.show()

# hospital_death
bar_donut(data, 'hospital_death')

"""**Observation:** The dataset is imbalanced with respect to the target variable

<a name = "Predictor-variables"></a>
### 2.3.2 Predictor variables
"""

# Function to compute almost constant columns and relative frequencies of corresponding modes
def almost_constant(df, threshold = 0.9, show = True, return_list = True):
    rel_freq = []
    for col in df.columns:
        mode_rel_freq = max(df[col].value_counts(sort = True)/len(df[col]))
        if mode_rel_freq > threshold:
            rel_freq.append((col, mode_rel_freq))
    keys = [item[0] for item in rel_freq]
    values = [item[1] for item in rel_freq]
    series = pd.Series(data = values, index = keys).sort_values(ascending = False)
    if show == True:
        print(series.to_string())
    if return_list == True:
        return keys

# Almost constant columns and relative frequencies of corresponding modes
almost_constant_cols = almost_constant(data.drop('hospital_death', axis = 1), threshold = 0.9)

"""**Observations:**
- The column `readmission_status` is same for every observation, and hence is not relevant in the context of predicting the target variable
- Apart from `readmission_status`, relative frequency of the mode value is over $0.9$ for $10$ other predictor variables, among which `icu_stay_type` is an object variable, taking values `admit`, `transfer` and `readmit`, while the rest are binary float variables, taking values `0.0` and `1.0`
"""

# Donutplots in N x 3 grid form
def donuts_grid(df, cols, ncols = 3, hole = 0.5, height = 1500, width = 900):
    nrows = math.ceil(len(cols)/ncols)
    specs = np.full((nrows, ncols), {'type': 'domain'}).tolist()
    fig = make_subplots(rows = nrows, cols = ncols, specs = specs)
    count = 0
    break_flag = False
    for row in range(nrows):
        for col in range(ncols):
            i = (row * ncols) + col
            fig.add_trace(go.Pie(values = df[cols[i]].value_counts(sort = False).tolist(),
                                 labels = df[cols[i]].value_counts(sort = False).index.tolist(),
                                 hole = hole, textinfo = 'percent', title = f'{cols[i]}'),    # 'label+percent'
                          row = row + 1, col = col + 1)
            count = count + 1
            if count == len(cols):
                break_flag = True
                break

        if break_flag == True:
            break

    fig.update_layout(height = height, width = width)
    fig.show()

# Binary columns except gender and hospital_death
cols_binary = [col for col in data.columns if data[col].nunique() == 2]
cols_binary.remove('gender')
cols_binary.remove('hospital_death')
donuts_grid(data, cols_binary, ncols = 4, hole = 0.5, height = 1250, width = 1200)

# gender and icu_stay_type
fig = make_subplots(rows = 1, cols = 2, specs = [[{'type': 'domain'}, {'type': 'domain'}]])
fig.add_trace(go.Pie(values = data['gender'].value_counts(sort = False).tolist(),
                     labels = data['gender'].value_counts(sort = False).index.tolist(),
                     hole = 0.5, textinfo = 'label+percent', title = 'gender'),
                     row = 1, col = 1)
fig.add_trace(go.Pie(values = data['icu_stay_type'].value_counts(sort = False).tolist(),
                     labels = data['icu_stay_type'].value_counts(sort = False).index.tolist(),
                     hole = 0.5, textinfo = 'label+percent', title = 'icu_stay_type'),
                     row = 1, col = 2)
fig.update_layout(height = 450, width = 900, showlegend = False)
fig.show()

# Columns with 4 to 15 distinct values
cols_selected = [col for col in data.columns if 3 < data[col].nunique() <= 15]
col_vert = ['ethnicity', 'hospital_admit_source', 'icu_admit_source', 'icu_type', 'apache_3j_bodysystem', 'apache_2_bodysystem']
nrows = math.ceil(len(cols_selected)/3)
fig, ax = plt.subplots(nrows, 3, figsize = (15, 6.2*nrows), sharey = False)
for i in range(len(cols_selected)):
    countplot = sns.countplot(data = data, x = cols_selected[i], ax = ax[i//3, i%3])
    if cols_selected[i] in col_vert:
        countplot.set_xticklabels(countplot.get_xticklabels(), rotation = 90)
    if i%3 != 0:
        ax[i//3, i%3].set_ylabel(" ")
plt.tight_layout()
plt.show()

# Non-float columns with more than 15 distinct values
[col for col in data.columns if data[col].nunique() > 15 and data[col].dtype != 'float64']

# Number of unique values
keys = ['encounter_id', 'patient_id', 'hospital_id', 'icu_id']
values = [data[col].nunique() for col in keys]
print(pd.Series(data = values, index = keys).to_string())

"""**Observation:** The features `encounter_id` and `patient_id` are unique for each observation, and hence do not contribute to the task of predicting the target variable."""

# Dropping encounter_id and patient_id
data.drop(['encounter_id', 'patient_id'], axis = 1, inplace = True)
cols_int.remove('encounter_id')
cols_int.remove('patient_id')

# hospital_id
plt.figure(figsize = (15, data['hospital_id'].nunique()/6))
sns.countplot(data = data, y = 'hospital_id')
plt.tight_layout()
plt.show()

# icu_id
plt.figure(figsize = (15, data['icu_id'].nunique()/6))
sns.countplot(data = data, y = 'icu_id')
plt.tight_layout()
plt.show()

# Histograms in grid
def distribution_plot(df, cols, ncols = 4, kind = 'hist', hue = None, height = 0.84*4, width = 4):
    cols = [col for col in df.columns if df[col].nunique() > 15 and df[col].dtype == 'float64']
    bins_fd = math.floor(len(df)**(1/3))
    nrows = math.ceil(len(cols)/ncols)
    if kind == 'hist':
        fig, ax = plt.subplots(nrows, ncols, figsize = (width*ncols, height*nrows), sharey = False)
        for i in range(len(cols)):
            sns.histplot(data = df, x = cols[i], bins = bins_fd, hue = hue, ax = ax[i // ncols, i % ncols])
            if i % ncols != 0:
                ax[i // ncols, i % ncols].set_ylabel(" ")
    elif kind == 'kde':
        fig, ax = plt.subplots(nrows, ncols, figsize = (width*ncols, height*nrows), sharey = False)
        for i in range(len(cols)):
            sns.kdeplot(data = df, x = cols[i], hue = hue, ax = ax[i // ncols, i % ncols])
            if i % ncols != 0:
                ax[i // ncols, i % ncols].set_ylabel(" ")
    else:
        raise TypeError(f"'{kind}' is not a valid argument for the parameter kind. Use 'hist' or 'kde'.")
    plt.tight_layout()
    plt.show()

# Float columns with more than 15 distinct values
cols_selected = [col for col in data.columns if data[col].nunique() > 15 and data[col].dtype == 'float64']
distribution_plot(df = data, cols = cols_selected, kind = 'hist')

"""<a name = "Multivariate-Analysis"></a>
## 2.4. Multivariate Analysis

- Relationships among the predictor variables
- Relationships of the target variable with the predictor variables

<a name = "Relationships-among-the-predictor-variables"></a>
### 2.4.1. Relationships among the predictor variables

### Correlation structure among numerical features
"""

# Heatmap
cols_selected = [col for col in cols_int + cols_float if col != 'hospital_death']
plt.figure(figsize = (180, 135))
sns.heatmap(data[cols_selected].corr(), annot = True, cmap = plt.cm.CMRmap_r)

# Function to detect pairs with extreme correlation
def pairs_with_strong_corr(df, cols, threshold = 0.8, show = True, return_variables = False):
    variable_list = []
    corr_positive_list = []
    corr_negative_list = []
    for i in range(len(cols)):
        for j in range(len(cols)):
            if i<j:
                corr = df[cols[i]].corr(df[cols[j]])
                if corr > threshold:
                    variable_list = variable_list + [cols[i], cols[j]]
                    corr_positive_list.append(((cols[i], cols[j]), corr))
                if corr < -threshold:
                    variable_list = variable_list + [cols[i], cols[j]]
                    corr_negative_list.append(((cols[i], cols[j]), corr))
    if show == True:
        corr_positive = pd.Series(data = [item[1] for item in corr_positive_list], index = [item[0] for item in corr_positive_list])
        corr_negative = pd.Series(data = [item[1] for item in corr_negative_list], index = [item[0] for item in corr_negative_list])
        print("Pairs with extreme positive correlation:")
        print(" ")
        print(corr_positive.sort_values(ascending = False).to_string())
        print(" ")
        print("Pairs with extreme negative correlation:")
        print(" ")
        print(corr_negative.sort_values(ascending = True).to_string())
    if return_variables == True:
        return variable_list

# Detecting pairs with extreme correlation
cols_selected = [col for col in cols_int + cols_float if col != 'hospital_death']
pairs_with_strong_corr(df = data, cols = cols_selected, threshold = 0.9)

"""**Observations:**

- There are $94$ pairs of numerical features with correlation coefficient over $0.9$
- There are no pair of numerical features with correlation coefficient below $-0.9$
- $3$ pairs of numerical features have correlation coefficient exactly equal to $1,$ i.e. there exists perfect linear relationship (with positive slope) between the variables in each of those pairs (this corresponds to the fact that there are $3$ duplicate columns in the dataset)

<a name = "Relationships-of-the-target-variable-with-the-predictor-variables"></a>
### 2.4.2. Relationships of the target variable with the predictor variables
"""

# Contingency tables for target variable and binary features
def contingency_binary(df, target, ncols = 3, figsize_multiplier = 2):
    cols_binary = [col for col in df.columns if df[col].nunique() == 2]
    cols_binary.remove(target)
    if len(cols_binary) == 0:
        print("The dataset does not contain a binary feature")
    else:
        nrows = math.ceil(len(cols_binary)/ncols)
        nvals = 2 # Binary variables
        figsize = (figsize_multiplier*nvals*ncols, 0.8*figsize_multiplier*nvals*nrows)
        fig, ax = plt.subplots(nrows, ncols, figsize = figsize, sharey = False)
        class_names_2 = df[target].value_counts().index.tolist()
        for i in range(len(cols_binary)):
            class_names_1 = df[cols_binary[i]].value_counts().index.tolist()
            contingency_mat = np.zeros(shape = (len(class_names_2), len(class_names_1)))
            for j in range(len(class_names_2)):
                for k in range(len(class_names_1)):
                    contingency_mat[j][k] = len([l for l in range(len(df)) if df[target][l] == class_names_2[j] and df[cols_binary[i]][l] == class_names_1[k]])
            contingency_table_df = pd.DataFrame(contingency_mat)
            hm = sns.heatmap(contingency_table_df, annot = True, annot_kws = {"size": 16}, fmt = 'g', ax = ax[i // ncols, i % ncols])
            hm.set_xlabel(f'{cols_binary[i]}', fontsize = 14)
            hm.set_ylabel(target, fontsize = 14)
            hm.set_xticklabels(class_names_1, fontdict = {'fontsize': 12}, rotation = 0, ha = "right")
            hm.set_yticklabels(class_names_2, fontdict = {'fontsize': 12}, rotation = 0, ha = "right")
            if i % ncols != 0:
                ax[i // ncols, i % ncols].set_ylabel(" ")
        plt.tight_layout()
        plt.show()

# Target x Binary features
contingency_binary(df = data, target = 'hospital_death', ncols = 3, figsize_multiplier = 2)

# Contingency table for target variable and general categorical feature
def contingency_table(df, feature, target, figsize_multiplier = 2, title = False, rotate_xticklabels = 0, rotate_yticklabels = 0):
    class_names_1 = df[feature].value_counts().index.tolist()
    class_names_2 = df[target].value_counts().index.tolist()

    contingency_mat = np.zeros(shape = (len(class_names_2), len(class_names_1)))
    for i in range(len(class_names_2)):
        for j in range(len(class_names_1)):
            contingency_mat[i][j] = len([k for k in range(len(df)) if df[target][k] == class_names_2[i] and df[feature][k] == class_names_1[j]])

    contingency_table_df = pd.DataFrame(contingency_mat)
    plt.figure(figsize = (figsize_multiplier*len(class_names_1), 0.8*figsize_multiplier*len(class_names_2)))
    if title == True:
        plt.title(f"{target} x {feature}")
    hm = sns.heatmap(contingency_table_df, annot = True, annot_kws = {"size": 16}, fmt = 'g')
    hm.set_xlabel(f'{feature}', fontsize = 14)
    hm.set_ylabel(f'{target}', fontsize = 14)
    hm.set_xticklabels(class_names_1, fontdict = {'fontsize': 12}, rotation = rotate_xticklabels, ha = "right")
    hm.set_yticklabels(class_names_2, fontdict = {'fontsize': 12}, rotation = rotate_yticklabels, ha = "right")
    plt.grid(False)
    plt.show()

# Target x Features taking 3 to 15 distinct values
cols_selected = [col for col in data.columns if 3 <= data[col].nunique() <= 15]
cols_xticklabels = ['ethnicity', 'hospital_admit_source', 'icu_admit_source', 'icu_type', 'apache_3j_bodysystem', 'apache_2_bodysystem']
for col in cols_selected:
    if col in cols_xticklabels:
        rotate_xticklabels = 45
    else:
        rotate_xticklabels = 0
    contingency_table(df = data, feature = col, target = 'hospital_death', figsize_multiplier = 1.6, rotate_xticklabels = rotate_xticklabels)

# Target x Float features with more than 15 distinct values
cols_selected = [col for col in data.columns if data[col].nunique() > 15 and data[col].dtype == 'float64']
distribution_plot(df = data, cols = cols_selected, kind = 'kde', hue = 'hospital_death')

"""<a name = "Data-Preprocessing"></a>
# 3. Data Preprocessing

- Train-Test Split
- Missing Data Imputation
- Categorical Data Encoding
- Normalization

<a name = "Train-Test-Split"></a>
## 3.1. Train-Test Split
"""

X = data.drop('hospital_death', axis = 1) # Independent variables
y = data['hospital_death'] # Target variable
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.2, shuffle = True)

"""### Training data"""

# Training set - Predictor variables
X_train

# Training set - Target variable
bar_donut(pd.DataFrame(y_train), 'hospital_death',  manual_title_text = True,
          title_text = "Frequency distribution of hospital_death in the training set")

"""### Test data"""

# Test set - Predictor variables
X_test

# Test set - Target variable
bar_donut(pd.DataFrame(y_test), 'hospital_death', manual_title_text = True,
          title_text = "Frequency distribution of hospital_death in the test set")

"""<a name = "Missing-Data-Imputation"></a>
## 3.2. Missing Data Imputation
"""

# Count of missing values for the target variable
print(pd.Series({"Number of missing target values in the training set": y_train.isna().sum(),
                 "Number of missing target values in the test set": y_test.isna().sum()}).to_string())

"""### Dropping columns with majority of the observations missing"""

# Columns with more than 50% missing values in the training set
print((X_train.isna().sum()/len(X_train))[X_train.isna().sum()/len(X_train) > 0.5].sort_values(ascending = False))

"""We drop the $74$ features, which have over $50\%$ values missing in the training dataset, from the subsequent analysis."""

# Dropping columns with more than 50% missing values in the training set
majority_missing = (X_train.isna().sum()/len(X_train))[data.isna().sum()/len(data) > 0.5].index.tolist()
X_train.drop(majority_missing, axis = 1, inplace = True)
X_test.drop(majority_missing, axis = 1, inplace = True)

"""### Mode imputation"""

# Function to impute missing values with the most frequent value appearing in the corresponding columns
def mode_imputer(data):
    data_imputed = data.copy(deep = True)
    imputer = SimpleImputer(strategy = 'most_frequent')
    data_imputed.iloc[:, :] = imputer.fit_transform(data_imputed)
    return data_imputed

"""### Proportion-based imputation

With the goal of keeping the feature distributions same before and after imputation, we impute the missing values in a column in such a way so that the proportions of the existing unique values in that particular column remain roughly same as those were prior to the imputation. The following function takes a dataframe, implements the proportion-based imputation in each column containing missing values and returns the resulting dataframe.
"""

# Function to impute missing values proportionately with respect to the existing unique values
def prop_imputer(df):
    df_prop = df.copy(deep = True)
    missing_cols = df_prop.isna().sum()[df_prop.isna().sum() != 0].index.tolist()
    for col in missing_cols:
        values_col = df_prop[col].value_counts(normalize = True).index.tolist()
        probabilities_col = df_prop[col].value_counts(normalize = True).values.tolist()
        df_prop[col] = df_prop[col].fillna(pd.Series(data = np.random.choice(values_col, p = probabilities_col, size = len(df_prop)), index = df_prop[col].index))
    return df_prop

# Proportion-based imputation
X_train = prop_imputer(X_train)
X_test = prop_imputer(X_test)

"""<a name = "Categorical-Data-Encoding"></a>
## 3.3. Categorical Data Encoding
"""

# Object type columns and corresponding number of unique values
print(pd.Series(data = [data[col].nunique() for col in cols_object], index = cols_object).to_string())

"""All $8$ categorical features are nominal in nature, i.e. there is no notion of order in their realized values.

### Label encoding
"""

def label_encoder(df, cols):
    df_le = df.copy(deep = True)
    le = LabelEncoder()
    for col in cols:
        df_le[col] = le.fit_transform(df_le[col])
    return df_le

"""Explanation of the arguments:
- **df:** The input dataset
- **cols:** List of columns that we want to encode
"""

X_train_le = label_encoder(X_train, cols_object)
X_test_le = label_encoder(X_test, cols_object)

"""For a categorical column with $n$ distinct values, the label encoder maps the $n$ distinct values to numerical values between $0$ and $n-1$."""

# Example
X_train_le[[col for col in X_train_le.columns if cols_object[1] in col]]

"""### One-hot encoding"""

# Function for one-hot encoding
def one_hot_encoder(df, cols, drop_first = False):
    cols = [col for col in cols if col in df.columns] # To ensure that 'cols' is contained (as a subset) within df.columns
    df_ohe = pd.get_dummies(df, columns = cols, drop_first = drop_first)
    return df_ohe

"""Explanation of the arguments:
- **df:** The input dataset
- **cols:** List of columns that we want to encode
"""

# One-hot encoding with drop_first = False
X_concat = pd.concat([X_train, X_test])
X_concat_ohe = one_hot_encoder(X_concat, cols_object, drop_first = False)
X_train_ohe = X_concat_ohe.loc[X_train.index]
X_test_ohe = X_concat_ohe.loc[X_test.index]

"""For a categorical column with $k$ distinct values, the [one-hot](https://en.wikipedia.org/wiki/One-hot) encoder produces $k$ new columns, one corresponding to each unique value. The original column is then dropped."""

# Example
X_train_ohe[[col for col in X_train_ohe.columns if cols_object[1] in col]]

"""Note that `gender_F` and `gender_M` are related by `gender_F + gender_M = 1`. Hence we shall lose no information by dropping one of these columns. This can be done (for each feature) by changing `drop_first = False` to `drop_first = True`."""

# One-hot encoding with drop_first = True
X_concat_ohe = one_hot_encoder(X_concat, cols_object, drop_first = True)
X_train_ohe = X_concat_ohe.loc[X_train.index]
X_test_ohe = X_concat_ohe.loc[X_test.index]

"""Now the one-hot encoder produces $k-1$ new columns for a categorical column with $k$ distinct values, by dropping the first column. As before, the original column is also dropped."""

# Example
X_train_ohe[[col for col in X_train_ohe.columns if cols_object[1] in col]]

"""To have a column corresponding to `nan` values (if they are present in the original column), one must set the `dummy_na` parameter of the `get_dummies` function to be `True` (which is by default `False`)."""

# Replacing original predictors with encoded predictors
X_train = X_train_ohe
X_test = X_test_ohe

"""<a name = "Normalization"></a>
## 3.4. Normalization
"""

# Min-max normalization of predictors in the training set
for col in X_train.columns:
    if X_train[col].dtypes == 'int64' or X_train[col].dtypes == 'float64': # Checking if the column is numerical
        if X_train[col].nunique() > 1: # Checking if the column is non-constant
           X_train[col] = (X_train[col] - X_train[col].min()) / (X_train[col].max() - X_train[col].min())
X_train

# Min-max normalization of predictors in the test set
for col in X_test.columns:
    if X_test[col].dtypes == 'int64' or X_test[col].dtypes == 'float64': # Checking if the column is numerical
        if X_test[col].nunique() > 1: # Checking if the column is non-constant
           X_test[col] = (X_test[col] - X_test[col].min()) / (X_test[col].max() - X_test[col].min())
X_test

"""<a name = "Baseline-Neural-Network"></a>
# 4. Baseline Neural Network
"""

# Adding layers to sequential model
model = Sequential()
model.add(Dense(16, input_dim = len(X_train.columns), activation = 'relu'))
model.add(Dense(12, activation = 'relu'))
model.add(Dense(8, activation = 'relu'))
model.add(Dense(4, activation = 'relu'))
model.add(Dense(1, activation = 'sigmoid'))
model.summary()

# Specifying loss function and optimizer
model.compile(loss = 'binary_crossentropy', optimizer = 'adam', metrics = ['accuracy'])

# Training the model
history = model.fit(X_train, y_train, validation_data = (X_test, y_test), epochs = 100, batch_size = 64)

# Visualization of model accuracy
model_accuracy = pd.DataFrame()
model_accuracy['accuracy'] = history.history['accuracy']
model_accuracy['val_accuracy'] = history.history['val_accuracy']

plt.figure(figsize = (9, 6))
sns.lineplot(data = model_accuracy['accuracy'], label = 'Train')
sns.lineplot(data = model_accuracy['val_accuracy'], label = 'Test')
plt.title('Model accuracy', fontsize = 14)
plt.ylabel('Accuracy', fontsize = 14)
plt.xlabel('Epoch', fontsize = 14)
plt.legend()
plt.show()

# Visualization of model loss
model_loss = pd.DataFrame()
model_loss['loss'] = history.history['loss']
model_loss['val_loss'] = history.history['val_loss']

plt.figure(figsize = (9, 6))
sns.lineplot(data = model_loss['loss'], label = 'Train')
sns.lineplot(data = model_loss['val_loss'], label = 'Test')
plt.title('Model loss', fontsize = 14)
plt.ylabel('Loss', fontsize = 14)
plt.xlabel('Epoch', fontsize = 14)
plt.legend()
plt.show()

# Prediction on test set
pred = model.predict(X_test)
threshold = 0.5
y_pred = [0 if pred[i][0] < threshold else 1 for i in range(len(pred))]

# Function to compute and visualize confusion matrix
def confusion_mat(y_pred, y_test):
    class_names = [0, 1]
    tick_marks_y = [0.5, 1.5]
    tick_marks_x = [0.5, 1.5]
    confusion_matrix = metrics.confusion_matrix(y_test, y_pred)
    confusion_matrix_df = pd.DataFrame(confusion_matrix, range(2), range(2))
    plt.figure(figsize = (6, 4.75))
    plt.title("Confusion Matrix", fontsize = 14)
    hm = sns.heatmap(confusion_matrix_df, annot = True, annot_kws = {"size": 16}, fmt = 'd') # font size
    hm.set_xlabel("Predicted label", fontsize = 14)
    hm.set_ylabel("True label", fontsize = 14)
    hm.set_xticklabels(class_names, fontdict = {'fontsize': 14}, rotation = 0, ha = "right")
    hm.set_yticklabels(class_names, fontdict = {'fontsize': 14}, rotation = 0, ha = "right")
    plt.grid(False)
    plt.show()

# Confusion matrix
confusion_mat(y_pred, y_test)

# Evaluation metrics
acc = accuracy_score(y_test, y_pred)
roc_auc = roc_auc_score(y_test, y_pred)
precision = precision_score(y_test, y_pred)
recall = recall_score(y_test, y_pred)
f1 = f1_score(y_test, y_pred)

print(pd.Series({"Accuracy": acc,
                 "ROC-AUC": roc_auc,
                 "Precision": precision,
                 "Recall": recall,
                 "F1-score": f1}).to_string())

"""<a name = "Hyperparameter-Tuning"></a>
# 5. Hyperparameter Tuning
"""

# Building the model
def model_builder(ht):
    model = Sequential()
    model.add(keras.layers.Flatten(input_shape = (X_train.shape[1],)))

    # Tuning the number of units in the first Dense layer
    ht_units = ht.Int('units', min_value = 32, max_value = 512, step = 32) # 32-512
    model.add(keras.layers.Dense(units = ht_units, activation = 'relu'))
    model.add(keras.layers.Dense(12, activation = 'relu'))
    model.add(keras.layers.Dense(8, activation = 'relu'))
    model.add(keras.layers.Dense(4, activation = 'relu'))
    model.add(keras.layers.Dense(1, activation = 'sigmoid'))

    # Tuning the learning rate for the optimizer
    ht_learning_rate = ht.Choice('learning_rate', values = [0.01, 0.001, 0.0001])

    model.compile(loss = 'binary_crossentropy', optimizer = 'adam', metrics = ['accuracy'])

    return model

# Making the tuner
tuner = kt.Hyperband(model_builder,
                     objective = 'val_accuracy',
                     max_epochs = 10,
                     factor = 3,
                     directory = 'dir_2')

# Early stopping
stop_early = tf.keras.callbacks.EarlyStopping(monitor = 'val_loss', patience = 5)

# Implementing the tuner
tuner.search(X_train, y_train, epochs = 50, validation_split = 0.2, callbacks = [stop_early])

# Get the optimal hyperparameters
best_hparams = tuner.get_best_hyperparameters(num_trials = 1)[0]

print("-------- The hyperparameter search is complete --------")
print(" ")
print(pd.Series({"Optimal number of units in the first densely-connected layer": best_hparams.get('units'),
                 "Optimal learning rate for the optimizer": best_hparams.get('learning_rate')}).to_string())

# Building the model with optimal hyperparameters
model = tuner.hypermodel.build(best_hparams)

# Training the model
history = model.fit(X_train, y_train, epochs = 50, validation_split = 0.2)

# Validation accuracy
val_accuracy_optimal = history.history['val_accuracy']

# Computing best epoch in terms of maximum validation accuracy
best_epoch = val_accuracy_optimal.index(max(val_accuracy_optimal)) + 1
print(" ")
print(pd.Series({"Best epoch": (best_epoch)}).to_string())

# Re-instantiating the model
model_tuned = tuner.hypermodel.build(best_hparams)

# Re-training the hypermodel with the optimal number of epochs
model_tuned.fit(X_train, y_train, epochs = best_epoch, validation_split = 0.2)

# Evaluation on the test set
eval_tuned = model_tuned.evaluate(X_test, y_test)
print(" ")
print(pd.Series({"Test loss": eval_tuned[0],
                 "Test accuracy": eval_tuned[1]}).to_string())

# Confusion matrix
pred_tuned = model_tuned.predict(X_test)
threshold = 0.5
y_pred_tuned = [0 if pred_tuned[i][0] < threshold else 1 for i in range(len(pred_tuned))]
confusion_mat(y_pred_tuned, y_test)

# Evaluation metrics
acc = accuracy_score(y_test, y_pred_tuned)
roc_auc = roc_auc_score(y_test, y_pred_tuned)
precision = precision_score(y_test, y_pred_tuned)
recall = recall_score(y_test, y_pred_tuned)
f1 = f1_score(y_test, y_pred_tuned)

print(pd.Series({"Accuracy": acc,
                 "ROC-AUC": roc_auc,
                 "Precision": precision,
                 "Recall": recall,
                 "F1-score": f1}).to_string())

"""### Saving and loading the model"""

# Saving the model
model_tuned.save('model_tuned.h5')

# Loading the model
model_tuned_loaded = load_model('model_tuned.h5')

"""<a name = "Explainable-AI"></a>
# 6. Explainable AI
"""

# Loading JavaScript library
shap.initjs()

# Sampling from test data predictors
X_test_sample = X_test.sample(50)

# Predicted values corresponding to the sample
pred_tuned_sample = np.array(pd.Series(data = pred_tuned.flatten(), index = X_test.index)[X_test_sample.index])
y_pred_tuned_sample = np.array(pd.Series(data = y_pred_tuned, index = X_test.index)[X_test_sample.index])

# Wrapper function
def wrap(X):
    return model_tuned.predict(X).flatten()

# Explainer
explainer = shap.KernelExplainer(wrap, X_test_sample)

# Computing SHAP values based on the sample
shap_values = explainer.shap_values(X_test_sample, nsamples = 500)

"""## Global interpretation"""

# Summary plot
shap.summary_plot(shap_values = shap_values, features = X_test_sample, plot_type = 'bar')

"""## Local interpretation

### Explaining single prediction
"""

# Force plot
shap.initjs()
row = math.floor(3*len(X_test_sample)/4)
print(pd.Series({"Predicted value": pred_tuned_sample[row]}).to_string())
shap_values_row = explainer.shap_values(X_test_sample.iloc[row, :], nsamples = 500)
shap.force_plot(base_value = explainer.expected_value,
                shap_values = shap_values_row,
                features = X_test_sample.iloc[row, :],
                feature_names = X_test_sample.columns)

# Waterfall plot
print(pd.Series({"Predicted value": pred_tuned_sample[row]}).to_string())
shap.waterfall_plot(shap.Explanation(values = shap_values_row,
                                     base_values = explainer.expected_value,
                                     data = X_test_sample.iloc[row, :],
                                     feature_names = X_test_sample.columns.tolist()))

# Decision plot
print(pd.Series({"Predicted value": pred_tuned_sample[row]}).to_string())
shap.decision_plot(base_value = explainer.expected_value,
                   shap_values = shap_values_row,
                   features = X_test_sample.iloc[row, :],
                   feature_names = X_test_sample.columns.tolist())

"""### Explaining multiple predictions"""

# Force plot
shap.initjs()
shap.force_plot(base_value = explainer.expected_value,
                shap_values = shap_values,
                features = X_test_sample,
                feature_names = X_test_sample.columns)

# Dependence plot for ventilated_apache
shap.dependence_plot(ind = 'ventilated_apache', shap_values = shap_values, features = X_test_sample)

# Dependence plot for age
shap.dependence_plot(ind = 'age', shap_values = shap_values, features = X_test_sample)

# Dependence plot for age
shap.dependence_plot(ind = 'd1_heartrate_max', shap_values = shap_values, features = X_test_sample)

# Decision plot
print("Predicted values")
print(" ")
rows = [i*math.floor(len(X_test_sample)/6) for i in range(6)]
print(np.array(pd.Series(pred_tuned_sample)[rows]))
print(" ")
shap.decision_plot(base_value = explainer.expected_value,
                   shap_values = shap_values[rows],
                   features = X_test_sample.iloc[rows, :],
                   feature_names = X_test_sample.columns.tolist())

"""<a name = "Acknowledgements"></a>
# Acknowledgements

- [Global Open Source Severity of Illness Score (GOSSIS) dataset](https://journals.lww.com/ccmjournal/Citation/2019/01001/33__THE_GLOBAL_OPEN_SOURCE_SEVERITY_OF_ILLNESS.36.aspx)
- [Introduction to the Keras Tuner](https://www.tensorflow.org/tutorials/keras/keras_tuner)

<a name = "References"></a>
# References

- [Freedman-Diaconis rule](https://en.wikipedia.org/wiki/Freedman%E2%80%93Diaconis_rule)
- [One-hot](https://en.wikipedia.org/wiki/One-hot)
"""

# Runtime and memory usage
stop = time.time()
process = psutil.Process(os.getpid())

print(pd.Series({"Process runtime": "{:.2f} seconds".format(float(stop - start)),
                 "Process memory usage": "{:.2f} MB".format(float(process.memory_info()[0]/(1024*1024)))}).to_string())