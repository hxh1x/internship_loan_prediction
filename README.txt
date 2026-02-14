This report is designed to be copied directly into your project documentation, `README.md`, or printed for your college Viva presentation. It covers the architecture, the code structure, the technologies used, and the execution guide.

---

# **Project Report: Digital Loan Request, Approval & Disbursement System**

## **1. Project Overview**

This project is an end-to-end web application that automates the loan processing lifecycle. Unlike simple Machine Learning demonstrations, this system integrates a trained **RandomForest Classifier** into a realistic banking workflow.

The system features two distinct user roles:

1. **Customer:** Applies for loans, views status, and accepts offers.
2. **Bank Officer:** Reviews applications, uses ML to check eligibility, generates financial quotes (EMI/Interest), and disburses funds.

## **2. System Architecture**

The project follows a **Client-Server Architecture** with a clear separation of concerns:

* **Frontend (Presentation Layer):** Built with HTML, CSS, and Vanilla JavaScript. It serves as the user interface for input and visualization. It communicates with the backend via RESTful APIs using `fetch()`.
* **Backend (Application Layer):** Built with **Python Flask**. It acts as the central controller, routing requests, handling business logic, and managing the state of loan applications.
* **Intelligence Layer (ML):** A pre-trained **RandomForest** model (`.pkl`) is loaded by the backend to provide real-time predictions on loan eligibility based on 11 distinct features.
* **Data Layer (Persistence):** A lightweight, file-based **JSON Database** (`database.json`) simulates a NoSQL structure to store Users, Requests, Quotes, and Accounts.

---

## **3. Technology Stack**

| Component | Technology Used | Purpose |
| --- | --- | --- |
| **OS** | **Arch Linux** | Development Environment |
| **Language** | **Python 3.11+** | Core Backend Logic |
| **Framework** | **Flask** | REST API Web Server |
| **ML Library** | **Scikit-Learn** | Random Forest Implementation |
| **Data Proc.** | **Pandas, NumPy** | Data manipulation for ML |
| **Frontend** | **HTML5, CSS3** | User Interface & Styling |
| **Scripting** | **JavaScript (ES6)** | API Calls & DOM Manipulation |
| **Storage** | **JSON** | Lightweight Data Persistence |

---

## **4. Project Directory Structure**

The project is organized to separate the User Interface, Server Logic, and Data Models.

```text
internship_loan_prediction/
│
├── backend/                   # SERVER SIDE
│   ├── server.py              # The main Flask Application & API Routes
│   └── database.json          # The simulated database (stores all loan data)
│
├── frontend/                  # CLIENT SIDE
│   ├── login.html             # Entry point (Role selection)
│   ├── index.html             # Customer Dashboard (Application Form)
│   └── bank.html              # Bank Officer Dashboard (ML & Processing)
│
├── model/                     # MACHINE LEARNING
│   └── loan_model.pkl         # Trained RandomForest Model
│
├── src/                       # UTILITIES
│   ├── preprocessing.py       # Data cleaning scripts
│   └── train_model.py         # Script used to train the model
│
└── requirements.txt           # Python Dependencies

```

---

## **5. Key Modules & Features**

### **A. Authentication Module**

* **Function:** Simulates secure login.
* **Logic:** Redirects users to `index.html` (Customer) or `bank.html` (Officer) based on credentials.
* **Demo Credentials:**
* Customer: `user` / `user`
* Bank: `admin` / `admin`



### **B. The ML Eligibility Engine**

* **Trigger:** The Bank Officer clicks "Run ML Check".
* **Input:** 11 Features (Income, Dependents, Education, Self-Employed, Loan Amount, Term, CIBIL Score, Assets (Res, Com, Lux, Bank)).
* **Process:** The backend loads `loan_model.pkl`, converts inputs to a NumPy array, and predicts `1` (Eligible) or `0` (Rejected).
* **Safety Net:** Includes a fallback logic (Mock Model) if the `.pkl` file is missing, ensuring the demo never crashes.

### **C. The Financial Quote Engine**

* **Trigger:** Only available if Status is `ELIGIBLE`.
* **Logic (Rule-Based):**
* If CIBIL ≥ 750 → Interest Rate: **8.5%**
* If CIBIL ≥ 650 → Interest Rate: **10.5%**
* Else → Interest Rate: **12.5%**


* **Output:** Calculates the Monthly EMI and updates the application status to `OFFER_SENT`.

### **D. Disbursement Module**

* **Trigger:** Customer accepts offer → Bank clicks "Disburse".
* **Action:** Updates status to `ACTIVE`, creates a new record in the `loan_accounts` table, and timestamps the transaction.

---

## **6. How to Run the Project (Step-by-Step)**

### **Prerequisites (Arch Linux)**

Ensure the necessary Python libraries are installed via `pacman`:

```bash
sudo pacman -S python-flask python-flask-cors python-joblib python-numpy python-pandas python-scikit-learn

```

### **Step 1: Start the Backend Server**

Open a terminal in the project root folder and run:

```bash
python backend/server.py

```

*You will see:* `🚀 Starting Bank Backend API on http://localhost:5000`

### **Step 2: Access the Application**

Navigate to the `frontend/` folder in your file explorer and open **`login.html`** in your web browser.

### **Step 3: Execute the Workflow**

1. **Login as Customer:** (`user`/`user`) → Fill form → Submit.
2. **Login as Bank:** (`admin`/`admin`) in a new tab.
3. **Bank Action:** Click **"Run ML Check"** → Click **"Generate Quote"**.
4. **Customer Action:** Refresh Customer tab → Click **"Accept Offer"**.
5. **Bank Action:** Refresh Bank tab → Click **"Disburse Funds"**.

---

## **7. Conclusion**

This project successfully bridges the gap between theoretical Machine Learning and practical software development. By wrapping a Random Forest model in a Flask API and providing a realistic banking interface, the system demonstrates how AI can aid—rather than replace—human decision-making in financial institutions.

The implementation of **Role-Based Access Control (RBAC)** and **State Management** (Requested → Eligible → Offer Sent → Active) makes this a robust, industry-relevant prototype.
