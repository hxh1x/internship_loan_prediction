import tkinter as tk
import numpy as np
import joblib
import os

# -------------------------------------------------
# Load trained model safely (absolute path handling)
# -------------------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "model", "loan_model.pkl")

model = joblib.load(MODEL_PATH)

# -------------------------------------------------
# Prediction function
# -------------------------------------------------
def predict():
    try:
        values = np.array([[
            int(dep.get()),
            int(edu.get()),
            int(self_emp.get()),
            int(income.get()),
            int(loan_amt.get()),
            int(term.get()),
            int(cibil.get()),
            int(res_asset.get()),
            int(com_asset.get()),
            int(lux_asset.get()),
            int(bank_asset.get())
        ]])

        result = model.predict(values)

        if result[0] == 1:
            output.config(text="Loan Approved", fg="green")
        else:
            output.config(text="Loan Rejected", fg="red")

    except Exception as e:
        output.config(text="Invalid Input", fg="orange")

# -------------------------------------------------
# GUI Window Setup
# -------------------------------------------------
root = tk.Tk()
root.title("Bank Loan Prediction System")
root.geometry("600x600")
root.resizable(False, False)

# -------------------------------------------------
# Labels and Entry Fields
# -------------------------------------------------
labels = [
    "No. of Dependents",
    "Education (Graduate=1, Not=0)",
    "Self Employed (Yes=1, No=0)",
    "Annual Income",
    "Loan Amount",
    "Loan Term",
    "CIBIL Score",
    "Residential Assets Value",
    "Commercial Assets Value",
    "Luxury Assets Value",
    "Bank Asset Value"
]

entries = []

for i, text in enumerate(labels):
    tk.Label(root, text=text, anchor="w").grid(
        row=i, column=0, padx=15, pady=6, sticky="w"
    )
    entry = tk.Entry(root, width=25)
    entry.grid(row=i, column=1, padx=15, pady=6)
    entries.append(entry)

(
    dep,
    edu,
    self_emp,
    income,
    loan_amt,
    term,
    cibil,
    res_asset,
    com_asset,
    lux_asset,
    bank_asset
) = entries

# -------------------------------------------------
# Predict Button
# -------------------------------------------------
tk.Button(
    root,
    text="Predict Loan Status",
    command=predict,
    bg="#2ecc71",
    fg="white",
    width=25
).grid(row=11, column=0, columnspan=2, pady=20)

# -------------------------------------------------
# Output Label
# -------------------------------------------------
output = tk.Label(root, text="", font=("Arial", 14, "bold"))
output.grid(row=12, column=0, columnspan=2, pady=10)

# -------------------------------------------------
# Start GUI
# -------------------------------------------------
root.mainloop()

