from flask import Flask, request, jsonify
from flask_cors import CORS
import os

from algorithm import algo2, lossless_chase, chase, format_table

app = Flask(__name__)
CORS(app)


def parse_attributes(text):
    if not text or not text.strip():
        raise ValueError("Attributes input is required.")

    cleaned = text.replace(",", "").replace(" ", "").upper()
    print(cleaned)
    attrs = set(cleaned)

    if not attrs:
        raise ValueError("No attributes found.")

    if not all(ch.isalnum() for ch in attrs):
        raise ValueError("Attributes must be alphanumeric.")

    return attrs

def parse_fd(text, attrs):
    if text.count("->") != 1:
        raise ValueError(f"Invalid FD format: {text}")
    
    lhs_text, rhs_text = text.split("->", 1)
    
    lhs = set(lhs_text.replace(",", "").replace(" ", "").upper())
    rhs = set(rhs_text.replace(",", "").replace(" ", "").upper())

    if not lhs or not rhs:
        raise ValueError(f"Invalid FD format: {text}")

    if not all(ch.isalnum() for ch in lhs.union(rhs)):
        raise ValueError(f"Invalid characters in FD: {text}")
    
    if attrs is not None and not (lhs | rhs) <= attrs:
        raise ValueError(f"Invalid attribute in FD: {text}")
    
    return lhs, rhs

def parse_fds(text, attrs=None):
    if not text or not text.strip():
        raise ValueError("Functional dependencies input is required.")

    fds = []
    lines = [line.strip() for line in text.strip().splitlines() if line.strip()]

    for line in lines:
        lhs, rhs = parse_fd(line, attrs)

        fds.append((lhs, rhs))

    return fds


def parse_decomposition(text, attrs):
    if not text or not text.strip():
        raise ValueError("Decomposition input is required.")

    parts = [part.strip() for part in text.split(";") if part.strip()]
    if not parts:
        raise ValueError("Invalid decomposition format.")

    decomposition = []
    for part in parts:
        rel = set(part.replace(",", "").replace(" ", "").upper())

        if not rel:
            raise ValueError(f"Invalid decomposition part: {part}")

        if not all(ch.isalnum() for ch in rel):
            raise ValueError(f"Invalid characters in decomposition part: {part}")
            
        if not rel <= attrs:
            raise ValueError(f"Invalid attribute in decomposition: {part}")

        decomposition.append(list(rel))

    return decomposition


def format_fds(fds):
    lines = []
    normalized = []

    for lhs, rhs in fds:
        normalized.append(("".join(sorted(lhs)), "".join(sorted(rhs))))

    normalized.sort()

    for lhs, rhs in normalized:
        lines.append(f"{lhs} -> {rhs}")

    return "\n".join(lines)

def parse_dependency(text, attrs):
    if not text or not text.strip():
        raise ValueError("Dependencies input is required.")
    entail = [line.strip() for line in text.strip().splitlines() if line.strip()]

    if len(entail) != 1:
        raise ValueError("Only 1 dependency can be checked.")

    lhs, rhs = parse_fd(entail[0], attrs)

    return lhs, rhs


@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "Backend is running"}), 200


@app.route("/api/minimal-cover", methods=["POST"])
def minimal_cover():
    try:
        data = request.get_json(silent=True) or {}

        fd_text = data.get("functionalDependencies", "")
        _ = data.get("attributes", "")  # accepted but not used

        fds = parse_fds(fd_text)
        result = algo2(fds)

        return jsonify({
            "message": "Minimal cover generated successfully.",
            "result": format_fds(result)
        }), 200

    except ValueError as e:
        return jsonify({"message": str(e)}), 400
    except Exception as e:
        return jsonify({"message": f"Server error: {str(e)}"}), 500


@app.route("/api/lossless-decomposition", methods=["POST"])
def lossless_decomposition():
    try:
        data = request.get_json(silent=True) or {}

        attrs_text = data.get("attributes", "")
        fd_text = data.get("functionalDependencies", "")
        decomp_text = data.get("decomposition", "")

        attrs = parse_attributes(attrs_text)
        fds = parse_fds(fd_text, attrs)
        decomposition = parse_decomposition(decomp_text, attrs)

        result, tbl = lossless_chase(attrs, fds, decomposition)
        formatted_table = format_table(tbl)
        return jsonify({
            "message": "Lossless decomposition check completed successfully.",
            "result": "Lossless decomposition" if result else "Not lossless decomposition.",
            "table": formatted_table
        }), 200

    except ValueError as e:
        print("ValueError:", repr(e))
        return jsonify({"message": str(e)}), 400
    except Exception as e:
        print("Exception:", repr(e))
        return jsonify({"message": f"Server error: {str(e)}"}), 500


@app.route("/api/entailment", methods=["POST"])
def entailment():
    try:
        data = request.get_json(silent=True) or {}

        attrs_text = data.get("attributes", "")
        fd_text = data.get("functionalDependencies", "")
        depend_text = data.get("dependency", "")

        attrs = parse_attributes(attrs_text)
        fds = parse_fds(fd_text, attrs)
        depenencies = parse_dependency(depend_text, attrs)

        result, tbl = chase(attrs, fds, depenencies)
        formatted_table = format_table(tbl)

        return jsonify({
            "message": "Entailment check completed successfully.",
            "result": "True: Dependency is logically entailed." if result else "False, Dependency is not logically entailed.",
            "table": formatted_table
        }), 200

    except ValueError as e:
        return jsonify({"message": str(e)}), 400
    except Exception as e:
        return jsonify({"message": f"Server error: {str(e)}"}), 500


if __name__ == "__main__":
    debug_mode = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    app.run(host="0.0.0.0", port=8080, debug=debug_mode)