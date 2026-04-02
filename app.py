"""Flask web server - UI and API for the Agentic Test Automation Tool."""

import os
import json
import traceback
from flask import Flask, render_template, request, jsonify

from agent.scaffold import ensure_project_structure, get_project_tree
from agent.step_parser import parse_steps
from agent.object_repository import ObjectRepository
from agent.browser_agent import BrowserAgent
from agent.page_generator import generate_pages
from agent.test_generator import generate_tests
from agent.report_generator import generate_execution_report

app = Flask(__name__)

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/run", methods=["POST"])
def run_agent():
    """Main endpoint: parse steps, drive browser, generate artifacts."""
    data = request.get_json(force=True)
    raw_steps = data.get("steps", "")
    headless = data.get("headless", True)

    if not raw_steps.strip():
        return jsonify({"error": "No steps provided."}), 400

    try:
        ensure_project_structure(OUTPUT_DIR)

        parsed = parse_steps(raw_steps)

        repo_path = os.path.join(OUTPUT_DIR, "object_repository", "repository.json")
        repository = ObjectRepository(repo_path)

        agent = BrowserAgent(repository, headless=headless)
        execution_log = agent.run(parsed)

        repo_data = repository.to_dict()

        page_files = generate_pages(repo_data, OUTPUT_DIR)

        test_files = generate_tests(parsed, execution_log, repo_data, OUTPUT_DIR)

        report_path = generate_execution_report(execution_log, OUTPUT_DIR)

        tree = get_project_tree(OUTPUT_DIR)

        return jsonify({
            "status": "success",
            "parsed_steps": parsed,
            "execution_log": execution_log,
            "repository": repo_data,
            "generated_files": {
                "pages": page_files,
                "tests": test_files,
                "report": report_path,
            },
            "project_tree": tree,
            "commands": {
                "install": "pip install -r requirements.txt && playwright install chromium",
                "run_tests": f"cd {OUTPUT_DIR} && python -m pytest tests/ --html=reports/report.html --self-contained-html -v",
                "run_headed": f"cd {OUTPUT_DIR} && python -m pytest tests/ --headed --html=reports/report.html --self-contained-html -v",
            },
        })

    except Exception as exc:
        return jsonify({
            "status": "error",
            "error": str(exc),
            "traceback": traceback.format_exc(),
        }), 500


@app.route("/api/parse", methods=["POST"])
def parse_only():
    """Preview parsed steps without executing."""
    data = request.get_json(force=True)
    raw_steps = data.get("steps", "")

    if not raw_steps.strip():
        return jsonify({"error": "No steps provided."}), 400

    parsed = parse_steps(raw_steps)
    return jsonify({"parsed_steps": parsed})


@app.route("/api/repository", methods=["GET"])
def get_repository():
    """Return the current object repository."""
    repo_path = os.path.join(OUTPUT_DIR, "object_repository", "repository.json")
    if os.path.exists(repo_path):
        with open(repo_path, "r", encoding="utf-8") as f:
            return jsonify(json.load(f))
    return jsonify({"pages": {}})


@app.route("/api/tree", methods=["GET"])
def get_tree():
    """Return the output project tree."""
    if os.path.exists(OUTPUT_DIR):
        return jsonify({"tree": get_project_tree(OUTPUT_DIR)})
    return jsonify({"tree": "No output directory yet."})


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
