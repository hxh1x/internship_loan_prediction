from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
import joblib
import numpy as np
from datetime import datetime
import traceback # Added for debugging

app = Flask(__name__)
CORS(app) 

# -------------------------------------------------
# 1. SETUP PATHS & LOAD ML MODEL
# -------------------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'backend', 'database.json')
MODEL_PATH = os.path.join(BASE_DIR, 'model', 'loan_model.pkl')

# --- MOCK MODEL FALLBACK ---
# This ensures the system works even if the .pkl file is missing or incompatible
class MockModel:
    def predict(self, values):
        # values is [[dependents, education, ..., cibil, ...]]
        # Index 6 is CIBIL score based on the input order
        cibil = values[0][6] 
        # Simple logic: If CIBIL > 650, Approve (1), else Reject (0)
        return [1] if cibil >= 650 else [0]

ml_model = None
try:
    if os.path.exists(MODEL_PATH):
        ml_model = joblib.load(MODEL_PATH)
        print(f"✅ Loaded Real ML Model from {MODEL_PATH}")
    else:
        print(f"⚠️ Model file not found at {MODEL_PATH}. Using Mock Model.")
        ml_model = MockModel()
except Exception as e:
    print(f"❌ Error loading model: {e}. Using Mock Model.")
    ml_model = MockModel()

def read_db():
    if not os.path.exists(DB_PATH):
        initial_db = {
            "users": [],
            "loan_requests": [],
            "loan_quotes": [],
            "loan_accounts": [] 
        }
        with open(DB_PATH, 'w') as f:
            json.dump(initial_db, f, indent=4)
        return initial_db
        
    with open(DB_PATH, 'r') as f:
        return json.load(f)

def write_db(data):
    with open(DB_PATH, 'w') as f:
        json.dump(data, f, indent=4)

# -------------------------------------------------
# 2. AUTHENTICATION (Demo)
# -------------------------------------------------
@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if username == 'admin' and password == 'admin':
        return jsonify({
            "status": "success", "role": "BANK", "redirect": "bank.html", "user_id": 2
        })
    elif username == 'user' and password == 'user':
        return jsonify({
            "status": "success", "role": "CUSTOMER", "redirect": "index.html", "user_id": 1
        })
    else:
        return jsonify({"status": "error", "message": "Invalid credentials"}), 401

# -------------------------------------------------
# 3. LOAN REQUEST HANDLING
# -------------------------------------------------
@app.route('/api/request-loan', methods=['POST'])
def request_loan():
    data = request.json
    db = read_db()
    
    req_id = len(db['loan_requests']) + 1
    
    new_request = {
        "request_id": req_id,
        "user_id": data.get("user_id", 1),
        "features": {
            "dependents": data['dependents'],
            "education": data['education'],
            "self_employed": data['self_employed'],
            "income": data['income'],
            "loan_amount": data['loan_amount'],
            "loan_term": data['loan_term'],
            "cibil_score": data['cibil_score'],
            "res_asset": data['res_asset'],
            "com_asset": data['com_asset'],
            "lux_asset": data['lux_asset'],
            "bank_asset": data['bank_asset']
        },
        "status": "REQUESTED"
    }
    
    db['loan_requests'].append(new_request)
    write_db(db)
    
    return jsonify({"message": "Loan request submitted successfully", "request_id": req_id})

# -------------------------------------------------
# 4. BANK PROCESSES
# -------------------------------------------------
@app.route('/api/evaluate-eligibility', methods=['POST'])
def evaluate_eligibility():
    try:
        if not ml_model:
            return jsonify({"error": "ML Model failed to initialize"}), 500

        req_id = request.json.get('request_id')
        db = read_db()
        
        loan_req = next((r for r in db['loan_requests'] if r['request_id'] == req_id), None)
        if not loan_req:
            return jsonify({"error": "Request not found"}), 404

        feats = loan_req['features']
        
        # Safe conversion with error logging
        try:
            values = np.array([[
                int(feats['dependents']),
                int(feats['education']),
                int(feats['self_employed']),
                int(feats['income']),
                int(feats['loan_amount']),
                int(feats['loan_term']),
                int(feats['cibil_score']),
                int(feats['res_asset']),
                int(feats['com_asset']),
                int(feats['lux_asset']),
                int(feats['bank_asset'])
            ]])
        except ValueError as ve:
            return jsonify({"error": f"Invalid input data: {str(ve)}"}), 400

        # Predict
        prediction = ml_model.predict(values)[0]
        
        if prediction == 1:
            loan_req['status'] = "ELIGIBLE"
            message = "ML Model Approved: Customer is Eligible"
        else:
            loan_req['status'] = "REJECTED"
            message = "ML Model Declined: Customer is High Risk"
            
        write_db(db)
        return jsonify({"status": loan_req['status'], "message": message})

    except Exception as e:
        print("❌ SERVER ERROR in evaluate_eligibility:")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/api/generate-quote', methods=['POST'])
def generate_quote():
    req_id = request.json.get('request_id')
    db = read_db()
    
    loan_req = next((r for r in db['loan_requests'] if r['request_id'] == req_id), None)
    
    # Business Logic
    cibil = int(loan_req['features']['cibil_score'])
    requested_amt = int(loan_req['features']['loan_amount'])
    term = int(loan_req['features']['loan_term'])
    
    if cibil >= 750:
        interest_rate = 8.5
    elif cibil >= 650:
        interest_rate = 10.5
    else:
        interest_rate = 12.5

    total_interest = (requested_amt * interest_rate * (term/12)) / 100
    emi = (requested_amt + total_interest) / term

    quote = {
        "quote_id": len(db['loan_quotes']) + 1,
        "request_id": req_id,
        "approved_amount": requested_amt,
        "interest_rate": interest_rate,
        "emi_amount": round(emi, 2),
        "status": "OFFER_SENT"
    }
    
    db['loan_quotes'].append(quote)
    loan_req['status'] = "OFFER_SENT"
    write_db(db)
    
    return jsonify({"message": "Quote generated", "quote": quote})

# -------------------------------------------------
# 5. FINALIZATION STEPS
# -------------------------------------------------
@app.route('/api/accept-offer', methods=['POST'])
def accept_offer():
    req_id = request.json.get('request_id')
    db = read_db()
    
    loan_req = next((r for r in db['loan_requests'] if r['request_id'] == req_id), None)
    
    if loan_req and loan_req['status'] == 'OFFER_SENT':
        loan_req['status'] = 'OFFER_ACCEPTED'
        write_db(db)
        return jsonify({"message": "Offer Accepted! Waiting for disbursement."})
    
    return jsonify({"error": "Invalid request state"}), 400

@app.route('/api/disburse-loan', methods=['POST'])
def disburse_loan():
    req_id = request.json.get('request_id')
    db = read_db()
    
    loan_req = next((r for r in db['loan_requests'] if r['request_id'] == req_id), None)
    quote = next((q for q in db['loan_quotes'] if q['request_id'] == req_id), None)
    
    if loan_req and quote and loan_req['status'] == 'OFFER_ACCEPTED':
        loan_req['status'] = 'DISBURSED'
        
        new_account = {
            "account_id": len(db.get('loan_accounts', [])) + 1,
            "user_id": loan_req['user_id'],
            "original_request_id": req_id,
            "principal_balance": quote['approved_amount'],
            "start_date": datetime.now().strftime("%Y-%m-%d"),
            "status": "ACTIVE"
        }
        
        if 'loan_accounts' not in db: db['loan_accounts'] = []
        db['loan_accounts'].append(new_account)
        
        write_db(db)
        return jsonify({"message": "Funds Disbursed! Loan Account Created."})

    return jsonify({"error": "Cannot disburse funds."}), 400

@app.route('/api/db', methods=['GET'])
def view_db():
    return jsonify(read_db())

if __name__ == '__main__':
    print("🚀 Starting Bank Backend API on http://localhost:5000")
    app.run(debug=True, port=5000)
