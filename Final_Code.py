# -*- coding: utf-8 -*-
"""ROMANA.FINAL

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1gYC2ObNBVTyGC6G-0pHHYgfmYl4wyL6T
"""

# -*- coding: utf-8 -*-
"""Untitled7.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1gYC2ObNBVTyGC6G-0pHHYgfmYl4wyL6T
"""

# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
import xgboost as xgb

# Load the datasets (corrected file names)
train_df = pd.read_csv('train.csv')  # Load training data
test_df = pd.read_csv('test.csv')    # Load test data

# Preview data for EDA
print("Training Data Sample:\n", train_df.head())
print("Testing Data Sample:\n", test_df.head())

# Exploratory Data Analysis (EDA) should happen here
# Example: Checking for missing values, data types, and basic statistics
print("Training Data Info:\n", train_df.info())
print("Testing Data Info:\n", test_df.info())
print("Missing values in training data:\n", train_df.isnull().sum())
print("Missing values in testing data:\n", test_df.isnull().sum())

# Once EDA is complete, fill missing values for numeric columns with mean
train_df.fillna(train_df.select_dtypes(include=[np.number]).mean(), inplace=True)
test_df.fillna(test_df.select_dtypes(include=[np.number]).mean(), inplace=True)

# Fill missing values for categorical columns with mode
for col in train_df.select_dtypes(include=['object']).columns:
    train_df[col] = train_df[col].fillna(train_df[col].mode()[0])
    test_df[col] = test_df[col].fillna(test_df[col].mode()[0])

# Verify missing values again after filling
print("Missing values in training data after filling:\n", train_df.isnull().sum())
print("Missing values in testing data after filling:\n", test_df.isnull().sum())

# Convert categorical columns to category type
categorical_cols = ['Item_Identifier', 'Item_Fat_Content', 'Item_Type',
                    'Outlet_Identifier', 'Outlet_Size',
                    'Outlet_Location_Type', 'Outlet_Type']

# Convert categorical columns to numeric codes using .cat.codes
for col in categorical_cols:
    train_df[col] = train_df[col].astype('category').cat.codes
    test_df[col] = test_df[col].astype('category').cat.codes

# Define features and target
X = train_df.drop(['Item_Outlet_Sales'], axis=1)
y = train_df['Item_Outlet_Sales']

# Split data into training and validation sets
X_train, X_valid, y_train, y_valid = train_test_split(X, y, test_size=0.2, random_state=42)

# Convert training and validation data to DMatrix format
dtrain = xgb.DMatrix(X_train, label=y_train, enable_categorical=True)
dvalid = xgb.DMatrix(X_valid, label=y_valid, enable_categorical=True)

# Define model parameters
params = {
    'objective': 'reg:squarederror',  # for regression tasks
    'learning_rate': 0.05,
    'max_depth': 7,
    'seed': 42,
    'enable_categorical': True  # Enable categorical if using categorical types
}

# Train the model with early stopping
model = xgb.train(
    params,
    dtrain,
    num_boost_round=1000,
    evals=[(dvalid, "Validation")],
    early_stopping_rounds=10,
    verbose_eval=False
)

# Convert test data to DMatrix format for prediction
dtest = xgb.DMatrix(test_df, enable_categorical=True)

# Make predictions on test data
test_predictions = model.predict(dtest)

# Create a submission DataFrame with the required format
submission = pd.DataFrame({
    "Item_Identifier": test_df['Item_Identifier'],
    "Outlet_Identifier": test_df['Outlet_Identifier'],
    "Item_Outlet_Sales": test_predictions
})

# Ensure the submission DataFrame is in the correct order
submission = submission[["Item_Identifier", "Outlet_Identifier", "Item_Outlet_Sales"]]

# Save predictions to CSV
submission.to_csv('bigmart_sales_predictions.csv', index=False)
print("Predictions saved to 'bigmart_sales_predictions.csv'")