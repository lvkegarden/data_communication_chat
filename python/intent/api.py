from flask import Blueprint, request, jsonify, send_from_directory
from .service import IntentService
import os


intent_bp = Blueprint('intent', __name__, url_prefix='/api/intent')
_intent_service = None


def get_intent_service(llm=None):
    global _intent_service
    if _intent_service is None:
        _intent_service = IntentService(llm)
    return _intent_service


def register_intent_routes(app, llm=None):
    service = get_intent_service(llm)
    
    @intent_bp.route('/analyze', methods=['POST'])
    def analyze():
        try:
            data = request.get_json()
            input_text = data.get('text', '').strip()
            
            if not input_text:
                return jsonify({"success": False, "error": "Text is required"}), 400
            
            result = service.analyze_intent(input_text)
            return jsonify(result)
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500

    @intent_bp.route('/analyze/batch', methods=['POST'])
    def analyze_batch():
        try:
            data = request.get_json()
            inputs = data.get('texts', [])
            
            if not inputs or not isinstance(inputs, list):
                return jsonify({"success": False, "error": "Texts list is required"}), 400
            
            result = service.analyze_batch(inputs)
            return jsonify(result)
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500

    @intent_bp.route('/types', methods=['GET'])
    def intent_types():
        try:
            result = service.get_intent_types()
            return jsonify(result)
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500

    @intent_bp.route('/history', methods=['GET'])
    def history():
        try:
            result = service.get_history()
            return jsonify(result)
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500

    @intent_bp.route('/history', methods=['DELETE'])
    def clear_history():
        try:
            result = service.clear_history()
            return jsonify(result)
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500

    app.register_blueprint(intent_bp)
    return intent_bp
