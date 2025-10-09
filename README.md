# 🏭 Downtime Maintenance Agent

An intelligent **supply chain monitoring and maintenance automation agent** that forecasts production, detects shortfalls, and classifies operational and safety risks using predictive analytics.  
It integrates **LangGraph**, **Prophet**, **FastAPI**, and **machine learning** to deliver real-time insights and automated email alerts for proactive decision-making.

---

## 🚀 Key Features

- ⚙️ **Automated Data Pipeline** – Loads and processes manufacturing datasets for analysis.  
- 📈 **Production Forecasting** – Predicts future production using Prophet time-series modeling.  
- 🚨 **Shortfall Detection** – Flags underproduction compared to monthly targets.  
- 🌍 **Location Risk Classification** – Detects high-risk facilities based on operational metrics.  
- 🦺 **Safety Risk Analysis** – Evaluates safety metrics and QA performance for risk detection.  
- ✉️ **Automated Email Alerts** – Sends alerts for:
  - Production shortfalls  
  - High-risk locations  
  - Safety and continuity risks  
- 🌐 **FastAPI Integration** – Enables users to upload datasets and run analyses via REST APIs.

---

## 🧠 Workflow Overview

The LangGraph workflow follows this sequence:

1. **Load Data** → Reads and validates input CSV.  
2. **Production Forecaster** → Uses Prophet to forecast units produced.  
3. **Check Shortfall** → Compares forecasts against monthly targets.  
4. **Location Risk Classifier** → Evaluates city-wise operational risks.  
5. **Safety Risk Analyzer** → Calculates safety-based risk scores.  
6. **Send Alerts** → Dispatches automated summary emails.
