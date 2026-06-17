import os
import sys
import subprocess
import json
from pathlib import Path
from flask import Flask, request, jsonify, render_template

# Add parent 'dsl' directory to Python path so we can import parser and executor
current_dir = Path(__file__).resolve().parent
project_root = current_dir.parent
sys.path.append(str(project_root / "dsl"))

try:
    from parser import PreprocessingParser
    from executor import PreprocessingTransformer, PreprocessingExecutor
except ImportError as e:
    print(f"Error importing DSL components: {e}")
    # Fallback to absolute imports if needed
    sys.path.append(str(project_root))

app = Flask(
    __name__,
    template_folder=str(current_dir / "templates"),
    static_folder=str(current_dir / "static")
)

# Recursively serialize the Lark AST node
def serialize_lark_node(node):
    from lark import Token
    if isinstance(node, Token):
        return {
            "type": "token",
            "token_type": str(node.type),
            "value": str(node),
            "line": getattr(node, "line", None),
            "column": getattr(node, "column", None)
        }
    elif hasattr(node, "data"):
        return {
            "type": "rule",
            "rule_name": str(node.data),
            "children": [serialize_lark_node(c) for c in node.children]
        }
    else:
        return {
            "type": "literal",
            "value": str(node)
        }

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/project-info", methods=["GET"])
def get_project_info():
    dataset_path = project_root / "Office-31"
    dataset_exists = dataset_path.exists() and dataset_path.is_dir()
    
    # Check if we have subdirectories
    subdirs = []
    if dataset_exists:
        try:
            subdirs = [d.name for d in dataset_path.iterdir() if d.is_dir()]
        except Exception:
            pass

    return jsonify({
        "projectName": "Catastrophic Forgetting in Vision Transformers (ViT)",
        "startDate": "June 13, 2026",
        "datasetPath": str(dataset_path),
        "datasetExists": dataset_exists,
        "domainsDetected": subdirs,
        "pythonVersion": sys.version.split(" ")[0]
    })

@app.route("/api/git-log", methods=["GET"])
def get_git_log():
    try:
        # Get git log formatted as JSON-friendly fields
        cmd = ["git", "log", '--pretty=format:{"hash":"%h","author":"%an","date":"%ad","subject":"%s"}', "--date=short"]
        result = subprocess.run(cmd, cwd=str(project_root), capture_output=True, text=True, check=True)
        # Parse output lines
        lines = [line.strip() for line in result.stdout.split("\n") if line.strip()]
        commits = []
        for line in lines:
            try:
                commits.append(json.loads(line))
            except Exception:
                # Fallback if subject has weird characters
                pass
        return jsonify({"success": True, "commits": commits})
    except Exception as e:
        return jsonify({"success": False, "error": str(e), "commits": []})

@app.route("/api/parse", methods=["POST"])
def parse_script():
    data = request.get_json() or {}
    script = data.get("script", "")
    
    if not script:
        return jsonify({"success": False, "error": "Empty script content."})

    try:
        parser = PreprocessingParser()
        tree = parser.parse(script)
        serialized_ast = serialize_lark_node(tree)
        
        transformer = PreprocessingTransformer()
        actions = transformer.transform(tree)
        
        return jsonify({
            "success": True,
            "ast": serialized_ast,
            "actions": actions
        })
    except Exception as e:
        # Lark parser exceptions contain detailed error messages
        return jsonify({
            "success": False,
            "error": str(e)
        })

@app.route("/api/run", methods=["POST"])
def run_script():
    data = request.get_json() or {}
    script = data.get("script", "")
    mode = data.get("mode", "simulated") # "real" or "simulated"
    
    if not script:
        return jsonify({"success": False, "error": "Empty script content."})

    # First, validate syntax
    try:
        parser = PreprocessingParser()
        tree = parser.parse(script)
        transformer = PreprocessingTransformer()
        actions = transformer.transform(tree)
    except Exception as e:
        return jsonify({"success": False, "error": f"Compilation Error: {e}"})

    dataset_path = project_root / "Office-31"
    dataset_exists = dataset_path.exists() and dataset_path.is_dir()

    if mode == "real" and not dataset_exists:
        return jsonify({
            "success": False,
            "error": "Real execution mode requested, but Office-31 dataset directory does not exist locally."
        })

    # If in simulated mode or dataset doesn't exist, we return success with simulation metadata
    if mode == "simulated" or not dataset_exists:
        # Return the parsed actions list so frontend can simulate execution step-by-step
        return jsonify({
            "success": True,
            "mode": "simulated",
            "actions": actions,
            "message": "DSL compiled successfully. Simulation sequence initiated."
        })

    # Real execution
    import io
    old_stdout = sys.stdout
    mystdout = io.StringIO()
    sys.stdout = mystdout
    
    try:
        executor = PreprocessingExecutor(actions)
        executor.run()
        success = True
        error_msg = None
    except Exception as e:
        success = False
        error_msg = str(e)
    finally:
        sys.stdout = old_stdout
        
    output = mystdout.getvalue()
    return jsonify({
        "success": success,
        "mode": "real",
        "actions": actions,
        "stdout": output,
        "error": error_msg
    })

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5001, debug=True)
