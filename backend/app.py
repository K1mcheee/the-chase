from flask import Flask, request, jsonify
from flask_cors import CORS

from algorithm import algo2, lossless_chase, chase

app = Flask(__name__)
CORS(app)


def parse_attributes(text):
    if not text or not text.strip():
        raise ValueError("Attributes input is required.")

    cleaned = text.replace(",", "").replace(" ", "").upper()
    attrs = set(cleaned)

    if not attrs:
        raise ValueError("No attributes found.")

    if not all(ch.isalnum() for ch in attrs):
        raise ValueError("Attributes must be alphanumeric.")

    return attrs


def parse_fds(text):
    if not text or not text.strip():
        raise ValueError("Functional dependencies input is required.")

    fds = []
    lines = [line.strip() for line in text.strip().splitlines() if line.strip()]

    for line in lines:
        if "->" not in line:
            raise ValueError(f"Invalid FD format: {line}")

        lhs_text, rhs_text = line.split("->", 1)
        lhs = set(lhs_text.replace(",", "").replace(" ", "").upper())
        rhs = set(rhs_text.replace(",", "").replace(" ", "").upper())

        if not lhs or not rhs:
            raise ValueError(f"Invalid FD format: {line}")

        if not all(ch.isalnum() for ch in lhs.union(rhs)):
            raise ValueError(f"Invalid characters in FD: {line}")

        fds.append((lhs, rhs))

    return fds


def parse_decomposition(text):
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

def parse_dependency(text):
    if not text or not text.strip():
        raise ValueError("Dependencies input is required.")

    lhs = set(text.split()[0])
    rhs = set(text.split()[2])
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
        fds = parse_fds(fd_text)
        decomposition = parse_decomposition(decomp_text)

        result = lossless_chase(attrs, fds, decomposition)

        return jsonify({
            "message": "Lossless decomposition check completed successfully.",
            "result": "Lossless decomposition" if result else "Not lossless decomposition"
        }), 200

    except ValueError as e:
        return jsonify({"message": str(e)}), 400
    except Exception as e:
        return jsonify({"message": f"Server error: {str(e)}"}), 500


@app.route("/api/entailment", methods=["POST"])
def entailment():
    try:
        data = request.get_json(silent=True) or {}

        attrs_text = data.get("attributes", "")
        fd_text = data.get("functionalDependencies", "")
        depend_text = data.get("dependency", "")

        attrs = parse_attributes(attrs_text)
        fds = parse_fds(fd_text)
        depenencies = parse_dependency(depend_text)

        result = chase(attrs, fds, depenencies)

        return jsonify({
            "message": "Entailment check completed successfully.",
            "result": "True: Dependency is logically entailed" if result else "False, Dependency is not logically entailed"
        }), 200

    except ValueError as e:
        return jsonify({"message": str(e)}), 400
    except Exception as e:
        return jsonify({"message": f"Server error: {str(e)}"}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)