# FraudShield - Full-Stack Fraud Detection Platform

FraudShield is a fintech web application that monitors digital transactions in real time. It evaluates every incoming transaction using a combination of fraud rules and a machine learning model. The system calculates a risk score from 0 to 100 and classifies the transaction into one of three decisions: ALLOW, REVIEW, or BLOCK.

## Problem Statement

Online financial fraud causes major financial losses for companies and customers. Simple rule-based systems are easy to understand, but they often miss new fraud patterns. On the other hand, machine learning models can find complex patterns, but they can be hard to explain to analysts. 

FraudShield combines both approaches into a hybrid decision system that is fast, explainable, and accurate.

## Key Features

- Real-Time Evaluation: Checks transactions in real time and returns immediate risk decisions.
- Rule Engine: Checks 5 practical security rules (unusually high amount, new device, transaction bursts, unusual hours, location mismatch).
- Machine Learning Model: Uses a trained Random Forest model to predict fraud probability.
- Combined Risk Scoring: Combines ML probability (60% weight) and Rule violations (40% weight) to create a final risk score from 0 to 100.
- Explainable Results: Gives clear reasons for suspicious flags so analysts understand why a transaction was flagged or blocked.
- Analyst Dashboard: Includes key summary cards, a transaction ledger, and a live testing tool.

## System Architecture

The system follows a simple transaction evaluation flow:

1. **Frontend → Django API**  
   The user submits a transaction through the web interface.

2. **Django → Fraud Detection**  
   The backend validates the transaction and sends it to the fraud detection module.

3. **Fraud Detection → Risk Score**  
   The system checks rule-based conditions and uses the ML model to generate a fraud score.

4. **Risk Score → Decision + Database**  
   Based on the score, the transaction is marked as **ALLOW, REVIEW, or BLOCK**, and the result is stored in PostgreSQL.

### Flow

```text
Frontend
   ↓
Django REST API
   ↓
Fraud Detection
   ├── Rule Engine
   └── ML Model
         ↓
     Risk Score
         ↓
  ALLOW / REVIEW / BLOCK
         ↓
     PostgreSQL
```

## Tech Stack

- Backend: Python, Django, Django REST Framework
- Database: PostgreSQL (with SQLite fallback for local development)
- Machine Learning: scikit-learn, pandas, numpy, joblib
- Frontend: HTML5, CSS3, JavaScript
- Testing: pytest, Django TestCase
- Deployment & DevOps: Docker, Docker Compose, GitHub Actions

## Database Design

The database stores user profiles, merchant information, transactions, fraud predictions, and rule violations.

Entity Relationship Diagram:

+------------------+          +------------------+          +-----------------------+
|  AccountProfile  | 1      * |   Transaction    | *      1 |       Merchant        |
+------------------+----------+------------------+----------+-----------------------+
| id (PK)          |          | id (PK)          |          | id (PK)               |
| account_number   |          | transaction_id   |          | merchant_id           |
| account_age_days |          | account_id (FK)  |          | merchant_name         |
| avg_amount       |          | merchant_id (FK) |          | category              |
| usual_location   |          | amount           |          +-----------------------+
| usual_device_id  |          | location         |
+------------------+          | device_id        |
                              | is_new_device    |
                              | status           |
                              +--------+---------+
                                       | 1
                                       |
                   +-------------------+-------------------+
                 1 |                                       | 1..*
+------------------+---------------+       +---------------+------------------+
|  FraudPrediction                 |       |  RuleViolation                   |
+----------------------------------+       +----------------------------------+
| id (PK)                          |       | id (PK)                          |
| transaction_id (FK, Unique)      |       | transaction_id (FK)              |
| fraud_probability                |       | rule_name                        |
| risk_score                       |       | explanation                      |
| risk_level                       |       | severity                         |
| decision                         |       +----------------------------------+
+----------------------------------+

## Machine Learning Pipeline

1. Dataset: Uses a synthetic financial dataset of 10,000 transaction records with a ~4.5% fraud rate to simulate real-world class imbalance.
2. Features Used: amount, user_avg_amount, amount_ratio, account_age_days, is_new_device, recent_transaction_count, hour_of_day, location_match.
3. Model Selection: Trained a Random Forest Classifier using class weights to handle class imbalance effectively.
4. Performance Metrics:
   - Precision: 1.00 (Prevents flagging legitimate transactions)
   - Recall: 0.99 (Successfully catches actual fraudulent attempts)
   - ROC-AUC: 1.0000

## Fraud Risk Scoring Logic

The overall risk score is calculated using the following formula:

Risk Score = (ML Fraud Probability * 100 * 0.60) + (Rule Engine Score * 0.40)

Decision Matrix:

- 0 to 34 Risk Score -> LOW Risk -> ALLOW (Transaction approved immediately)
- 35 to 69 Risk Score -> MEDIUM Risk -> REVIEW (Sent to analysts for manual review)
- 70 to 100 Risk Score -> HIGH Risk -> BLOCK (Transaction declined automatically)

## API Endpoints

- POST /api/auth/register/ : Registers a new user and creates an account profile.
- POST /api/auth/login/ : Authenticates user credentials.
- GET /api/transactions/ : Returns a list of transactions with optional status filter.
- POST /api/transactions/ : Submits and evaluates a new transaction in real time.
- GET /api/transactions/<id>/ : Retrieves details and fraud breakdown for a single transaction.
- POST /api/transactions/<id>/evaluate/ : Re-evaluates an existing transaction.
- GET /api/dashboard/summary/ : Returns overall system stats and recent suspicious transactions.



## System Limitations

1. Dataset Scope: Uses synthetic financial data generated for demonstration and educational purposes.
2. Latency & Scale: In a high-volume production environment, user averages would be cached in Redis rather than queried from a database on every request.
3. Asynchronous Processing: Production banking systems use event streaming platforms like Apache Kafka to decouple payment authorization from fraud evaluation loops.
