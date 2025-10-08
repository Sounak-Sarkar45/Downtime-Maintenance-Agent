from flask import Blueprint, request, jsonify, current_app
from app.utils.langgraph_nodes import run_workflow

analysis_bp = Blueprint('analysis', __name__)

@analysis_bp.route('/run-analysis', methods=['POST'])
def run_analysis():
    data = request.json
    required_keys = ['data_path', 'monthly_target', 'forecast_days']
    for key in required_keys:
        if key not in data:
            return jsonify({'error': f'Missing key: {key}'}), 400

    try:
        app_config = current_app.config
        
        final_state = run_workflow({
            'data_path': data['data_path'],
            'monthly_target': data['monthly_target'],
            'sender_email': app_config['SENDER_EMAIL'],  
            'sender_password': app_config['SENDER_PASSWORD'],
            'receiver_email': app_config['RECEIVER_EMAIL'],
            'forecast_days': data['forecast_days'],
            'df': None,
            'forecast_df': None,
            'shortfall_status': None,
            'location_risk_scores': None,
            'safety_scores': None
        })
        return jsonify({'message': 'Analysis completed and alerts sent.', 'shortfall_status': final_state['shortfall_status'].to_dict()})
    except Exception as e:
        return jsonify({'error': str(e)}), 500