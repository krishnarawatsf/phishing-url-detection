from flask import Flask, render_template, request, jsonify
import logging

import config
from core.predictor import PhishingPredictor
from database import init_db, save_scan_result, get_scan_history, get_scan_stats

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = config.MAX_REQUEST_SIZE
app.config["SECRET_KEY"] = config.SECRET_KEY
app.config["JSON_SORT_KEYS"] = False
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Initialize database schema on startup
init_db()

# Lazy-loaded predictor singleton
_predictor = None

def get_predictor():
    global _predictor
    if _predictor is None:
        _predictor = PhishingPredictor()
    return _predictor


@app.route("/")
def index():
    """Renders the main dashboard page."""
    return render_template("index.html")


@app.route("/api/scan", methods=["POST"])
def scan_url():
    """
    POST /api/scan
    JSON Payload: { "url": "https://example.com" }
    
    Returns:
        JSON response with scan results, risk score, and explanations.
    """
    try:
        if request.content_length and request.content_length > config.MAX_REQUEST_SIZE:
            return jsonify({
                "status": "error",
                "message": "Request body exceeds the supported size limit."
            }), 413

        data = request.get_json(silent=True)
        if not data or not isinstance(data, dict):
            return jsonify({
                "status": "error",
                "message": "Invalid or missing JSON payload in request."
            }), 400

        raw_url = data.get("url", "")
        if not raw_url or not str(raw_url).strip():
            return jsonify({
                "status": "error",
                "message": "Please enter a valid non-empty URL."
            }), 400

        if len(str(raw_url)) > 2048:
            return jsonify({
                "status": "error",
                "message": "URL is too long."
            }), 400

        predictor = get_predictor()
        result = predictor.predict_url(str(raw_url))
        
        if result["status"] == "error":
            return jsonify(result), 400
            
        # Automatically persist scan log to SQLite database
        scan_id = save_scan_result(result)
        result["scan_id"] = scan_id
        
        return jsonify(result), 200
        
    except Exception as e:
        logging.error(f"Unexpected server error during URL scan: {str(e)}")
        return jsonify({
            "status": "error",
            "message": "An internal server error occurred while processing the request."
        }), 500


@app.route("/api/history", methods=["GET"])
def history():
    """
    GET /api/history
    Returns recent URL scan logs.
    """
    try:
        limit = request.args.get("limit", default=10, type=int)
        logs = get_scan_history(limit=limit)
        return jsonify({
            "status": "success",
            "history": logs
        }), 200
    except Exception as e:
        logging.error(f"Failed to fetch scan history: {str(e)}")
        return jsonify({
            "status": "error",
            "message": "Could not retrieve scan history."
        }), 500


@app.route("/api/stats", methods=["GET"])
def stats():
    """
    GET /api/stats
    Returns aggregate scan metrics.
    """
    try:
        data = get_scan_stats()
        return jsonify({
            "status": "success",
            "stats": data
        }), 200
    except Exception as e:
        logging.error(f"Failed to fetch stats: {str(e)}")
        return jsonify({
            "status": "error",
            "message": "Could not retrieve stats."
        }), 500


if __name__ == "__main__":
    app.run(host=config.FLASK_HOST, port=config.FLASK_PORT, debug=config.FLASK_DEBUG)
