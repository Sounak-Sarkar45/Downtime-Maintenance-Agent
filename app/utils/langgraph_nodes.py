from typing import TypedDict, List, Optional, Dict
from langgraph.graph import StateGraph, END
from .email_utils import send_shortfall_email, send_risk_summary_email, send_safety_email
import pandas as pd
from prophet import Prophet
from sklearn.preprocessing import LabelEncoder, StandardScaler
import nest_asyncio
import logging
from flask import current_app

nest_asyncio.apply()
logging.getLogger('cmdstanpy').setLevel(logging.ERROR)

class AgentState(TypedDict):
    """
    Represents the state of the Supply Chain Intelligence Agent.
    """
    df: Optional[pd.DataFrame]
    forecast_df: Optional[pd.DataFrame]
    shortfall_status: Optional[pd.DataFrame]
    location_risk_scores: Optional[pd.DataFrame]
    safety_scores: Optional[pd.DataFrame]
    data_path: str
    monthly_target: int
    sender_email: str
    sender_password: str
    receiver_email: str
    forecast_days: int
    
def load_data(state: AgentState) -> AgentState:
    data_path = state['data_path']
    print(f"--- Loading data from {data_path}...")
    try:
        df = pd.read_csv(data_path)
        print("Data loaded successfully.")
        return {**state, 'df': df}
    except FileNotFoundError:
        print(f"Error: The file at {data_path} was not found.")
        return {**state, 'df': None}

def production_forecaster(state: AgentState) -> AgentState:
    df = state['df']
    forecast_days = state['forecast_days']
    if df is None: return state

    print("--- Running Production Forecaster...")
    df_proc = df.copy()
    df_proc['ds'] = pd.to_datetime(df_proc['DATE'])
    df_proc['y'] = df_proc['Units produced']
    categorical_cols = ['CITY', 'COUNTRY', 'MODEL', 'PART']
    le = LabelEncoder()
    for col in categorical_cols:
        df_proc[col] = le.fit_transform(df_proc[col].astype(str))
    
    m = Prophet(daily_seasonality=True, weekly_seasonality=True)
    regressors = ['ORDERS', 'Production Cost', 'Warranties processed', 'Warranty claims', 'CITY', 'COUNTRY', 'MODEL', 'PART']
    for reg in regressors: m.add_regressor(reg)
    m.fit(df_proc)

    future = m.make_future_dataframe(periods=forecast_days)
    last_known_values = df_proc[regressors].iloc[-1].to_dict()
    for reg in regressors: future[reg] = last_known_values[reg]
    
    forecast = m.predict(future)
    forecast_df = forecast[['ds', 'yhat']].tail(forecast_days).copy()
    forecast_df.rename(columns={'ds': 'Date', 'yhat': 'Forecasted Units'}, inplace=True)
    
    print("Production forecasting complete.")
    return {**state, 'forecast_df': forecast_df}

def check_shortfall(state: AgentState) -> AgentState:
    forecast_df = state['forecast_df']
    monthly_target = state['monthly_target']
    if forecast_df is None: return state

    print("--- Running Shortfall Check...")
    forecast_df['Date'] = pd.to_datetime(forecast_df['Date'])
    forecasted_monthly_production = forecast_df.groupby(
        forecast_df['Date'].dt.to_period('M')
    )['Forecasted Units'].sum()
    
    results = pd.DataFrame({
        'Month': forecasted_monthly_production.index.astype(str),
        'Forecasted Total Units': forecasted_monthly_production.values
    })
    
    results['Monthly Target'] = monthly_target
    results['Shortfall'] = results['Forecasted Total Units'] < monthly_target
    
    print("Shortfall analysis complete.")
    return {**state, 'shortfall_status': results}

def location_risk_classifier(state: AgentState) -> AgentState:
    df = state['df']
    if df is None: return state

    print("--- Running Location Risk Classifier...")
    risk_data = df.copy()
    scaler = StandardScaler()
    risk_data.fillna(0, inplace=True) 
    
    risk_metrics = {
        'Repairs Processed': 1, 'Warranty claims': 1, 'QA pass rate': -1,
        'Warranties processed': 1, 'Shipping Cost': 1, 'On time deliveries': -1,
        'Shipping container utilization': -1
    }

    risk_data['Total_Risk_Score'] = 0.0
    for metric, direction in risk_metrics.items():
        if metric in risk_data.columns:
            risk_data[f'Scaled_{metric}'] = scaler.fit_transform(risk_data[[metric]])
            risk_data['Total_Risk_Score'] += risk_data[f'Scaled_{metric}'] * direction

    location_risk_scores = risk_data.groupby(['CITY', 'COUNTRY']).agg(
        Average_Risk_Score=('Total_Risk_Score', 'mean'),
        Total_Repairs_Processed=('Repairs Processed', 'sum'),
        Total_Warranty_Claims=('Warranty claims', 'sum'),
        On_Time_Delivery_Rate=('On time deliveries', 'mean')
    ).reset_index()

    location_risk_scores['Risk Tier'] = pd.qcut(
        location_risk_scores['Average_Risk_Score'], q=3, labels=['Low', 'Medium', 'High']
    )
    
    print("Location risk classification complete.")
    return {**state, 'location_risk_scores': location_risk_scores}

def safety_risk_analyzer(state: AgentState) -> AgentState:
    df = state['df']
    if df is None: return state

    print("--- Running Safety Risk Analyzer...")
    df_safety = df.copy()
    df_safety.fillna(0, inplace=True)
    
    df_safety['Repairs_Per_K_Units'] = (df_safety['Repairs Processed'] / df_safety['Units produced']) * 1000
    df_safety['Claims_Per_K_Units'] = (df_safety['Warranty claims'] / df_safety['Units produced']) * 1000
    
    safety_metrics = {
        'Repairs_Per_K_Units': 1,
        'Claims_Per_K_Units': 1,
        'QA pass rate': -1
    }

    scaler = StandardScaler()
    df_safety['Safety_Risk_Score'] = 0.0
    for metric, direction in safety_metrics.items():
        if metric in df_safety.columns:
            df_safety[f'Scaled_{metric}'] = scaler.fit_transform(df_safety[[metric]])
            df_safety['Safety_Risk_Score'] += df_safety[f'Scaled_{metric}'] * direction

    location_safety_scores = df_safety.groupby(['CITY', 'COUNTRY']).agg(
        Safety_Risk_Score=('Safety_Risk_Score', 'mean'),
        Repairs_Per_K_Units=('Repairs_Per_K_Units', 'mean'),
        Claims_Per_K_Units=('Claims_Per_K_Units', 'mean'),
        QA_Pass_Rate=('QA pass rate', 'mean')
    ).reset_index()
    
    location_safety_scores['Safety_Risk_Tier'] = pd.qcut(
        location_safety_scores['Safety_Risk_Score'], q=3, labels=['Low', 'Medium', 'High']
    )
    
    print("Safety risk analysis complete.")
    return {**state, 'safety_scores': location_safety_scores}

def send_alerts(state: AgentState) -> AgentState:
    """Sends all three types of email alerts based on analysis results."""
    
    print("\n--- Running Alert Sender Node...")
    
    sender_email = state['sender_email']
    sender_password = state['sender_password']
    receiver_email = state['receiver_email']
    
    # 1. Shortfall Alert
    if state['shortfall_status'] is not None:
        send_shortfall_email(state['shortfall_status'], sender_email, sender_password, receiver_email)

    # 2. General Location Risk Alert
    if state['location_risk_scores'] is not None:
        send_risk_summary_email(state['location_risk_scores'], sender_email, sender_password, receiver_email)

    # 3. Safety Risk Alert
    if state['safety_scores'] is not None:
        send_safety_email(state['safety_scores'], sender_email, sender_password, receiver_email)
        
    print("All alerts processed.")
    return state

def run_workflow(state_dict: Dict):
    workflow = StateGraph(AgentState)
    workflow.add_node("load_data", load_data)
    workflow.add_node("production_forecaster", production_forecaster)
    workflow.add_node("check_shortfall", check_shortfall)
    workflow.add_node("location_risk_classifier", location_risk_classifier)
    workflow.add_node("safety_risk_analyzer", safety_risk_analyzer)
    workflow.add_node("send_alerts", send_alerts)
    workflow.set_entry_point("load_data")
    workflow.add_edge("load_data", "production_forecaster")
    workflow.add_edge("production_forecaster", "check_shortfall")
    workflow.add_edge("check_shortfall", "location_risk_classifier")
    workflow.add_edge("location_risk_classifier", "safety_risk_analyzer")
    workflow.add_edge("safety_risk_analyzer", "send_alerts")
    workflow.add_edge("send_alerts", END)

    app = workflow.compile()
    final_state = app.invoke(state_dict)
    return final_state

