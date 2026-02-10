import pandas as pd
from sklearn.preprocessing import LabelEncoder

# Load dataset
df = pd.read_csv("data/loan_data.csv")

# Clean column names
df.columns = df.columns.str.strip().str.lower()

# Drop ID column
df.drop('loan_id', axis=1, inplace=True)

# 🔥 CLEAN loan_status VALUES (THIS WAS MISSING)
df['loan_status'] = df['loan_status'].astype(str).str.strip().str.lower()

# Handle missing values
df['loan_amount'].fillna(df['loan_amount'].median(), inplace=True)
df['loan_term'].fillna(df['loan_term'].median(), inplace=True)
df['cibil_score'].fillna(df['cibil_score'].median(), inplace=True)

# Encode categorical columns
le = LabelEncoder()
for col in ['education', 'self_employed']:
    df[col] = le.fit_transform(df[col])

# ✅ CORRECT target encoding (AFTER CLEANING)
df['loan_status'] = df['loan_status'].map({
    'approved': 1,
    'rejected': 0
})

# 🔍 SANITY CHECK
print("Loan status after encoding:")
print(df['loan_status'].value_counts(dropna=False))

# Save cleaned data
df.to_csv("data/cleaned_loan_data.csv", index=False)

print("✅ Preprocessing completed successfully.")
