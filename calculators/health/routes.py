from flask import Blueprint, request, jsonify, render_template
from .engines import (
    calc_bmi, calc_bmr_tdee, calc_body_fat, calc_water_intake,
    calc_egfr, calc_ldl_friedewald, calc_homa_ir, calc_hba1c_to_glucose,
    calc_corrected_calcium, calc_atherogenic_index,
    calc_ffmi, calc_lean_body_mass, calc_protein_intake, calc_ideal_body_weight,
)

health_bp = Blueprint("health", __name__, url_prefix="/health")


def _get_float(data, key, default=None):
    val = data.get(key, default)
    if val is None:
        return None
    return float(val)


def _get_str(data, key, default=""):
    return str(data.get(key, default))


# ── Page routes ──

@health_bp.route("/")
def index():
    return render_template("health/index.html")

@health_bp.route("/bmi")
def bmi_page():
    return render_template("health/bmi.html")

@health_bp.route("/bmr-tdee")
def bmr_tdee_page():
    return render_template("health/bmr_tdee.html")

@health_bp.route("/body-fat")
def body_fat_page():
    return render_template("health/body_fat.html")

@health_bp.route("/water-intake")
def water_intake_page():
    return render_template("health/water_intake.html")

@health_bp.route("/egfr")
def egfr_page():
    return render_template("health/egfr.html")

@health_bp.route("/ldl")
def ldl_page():
    return render_template("health/ldl.html")

@health_bp.route("/homa-ir")
def homa_ir_page():
    return render_template("health/homa_ir.html")

@health_bp.route("/hba1c")
def hba1c_page():
    return render_template("health/hba1c.html")

@health_bp.route("/corrected-calcium")
def corrected_calcium_page():
    return render_template("health/corrected_calcium.html")

@health_bp.route("/atherogenic-index")
def atherogenic_index_page():
    return render_template("health/atherogenic_index.html")

@health_bp.route("/ffmi")
def ffmi_page():
    return render_template("health/ffmi.html")

@health_bp.route("/lean-body-mass")
def lean_body_mass_page():
    return render_template("health/lean_body_mass.html")

@health_bp.route("/protein-intake")
def protein_intake_page():
    return render_template("health/protein_intake.html")

@health_bp.route("/ideal-body-weight")
def ideal_body_weight_page():
    return render_template("health/ideal_body_weight.html")


# ── API routes ──

@health_bp.route("/api/bmi", methods=["POST"])
def api_bmi():
    data = request.get_json()
    try:
        result = calc_bmi(
            weight_kg=_get_float(data, "weight_kg"),
            height_cm=_get_float(data, "height_cm"),
        )
        return jsonify({"status": "success", "data": result})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


@health_bp.route("/api/bmr-tdee", methods=["POST"])
def api_bmr_tdee():
    data = request.get_json()
    try:
        result = calc_bmr_tdee(
            weight_kg=_get_float(data, "weight_kg"),
            height_cm=_get_float(data, "height_cm"),
            age=int(data.get("age", 25)),
            gender=_get_str(data, "gender", "male"),
            activity_level=_get_str(data, "activity_level", "moderate"),
        )
        return jsonify({"status": "success", "data": result})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


@health_bp.route("/api/body-fat", methods=["POST"])
def api_body_fat():
    data = request.get_json()
    try:
        result = calc_body_fat(
            weight_kg=_get_float(data, "weight_kg"),
            height_cm=_get_float(data, "height_cm"),
            age=int(data.get("age", 25)),
            gender=_get_str(data, "gender", "male"),
            waist_cm=_get_float(data, "waist_cm"),
            neck_cm=_get_float(data, "neck_cm"),
            hip_cm=_get_float(data, "hip_cm", 0),
        )
        return jsonify({"status": "success", "data": result})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


@health_bp.route("/api/water-intake", methods=["POST"])
def api_water_intake():
    data = request.get_json()
    try:
        result = calc_water_intake(
            weight_kg=_get_float(data, "weight_kg"),
            activity_level=_get_str(data, "activity_level", "moderate"),
            climate=_get_str(data, "climate", "hot"),
        )
        return jsonify({"status": "success", "data": result})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


@health_bp.route("/api/egfr", methods=["POST"])
def api_egfr():
    data = request.get_json()
    try:
        result = calc_egfr(
            creatinine=_get_float(data, "creatinine"),
            age=int(data.get("age", 30)),
            gender=_get_str(data, "gender", "male"),
        )
        return jsonify({"status": "success", "data": result})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


@health_bp.route("/api/ldl", methods=["POST"])
def api_ldl():
    data = request.get_json()
    try:
        result = calc_ldl_friedewald(
            total_cholesterol=_get_float(data, "total_cholesterol"),
            hdl=_get_float(data, "hdl"),
            triglycerides=_get_float(data, "triglycerides"),
        )
        return jsonify({"status": "success", "data": result})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


@health_bp.route("/api/homa-ir", methods=["POST"])
def api_homa_ir():
    data = request.get_json()
    try:
        result = calc_homa_ir(
            fasting_glucose=_get_float(data, "fasting_glucose"),
            fasting_insulin=_get_float(data, "fasting_insulin"),
        )
        return jsonify({"status": "success", "data": result})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


@health_bp.route("/api/hba1c", methods=["POST"])
def api_hba1c():
    data = request.get_json()
    try:
        hba1c = _get_float(data, "hba1c")
        avg_glucose = _get_float(data, "avg_glucose")
        result = calc_hba1c_to_glucose(hba1c=hba1c, avg_glucose=avg_glucose)
        return jsonify({"status": "success", "data": result})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


@health_bp.route("/api/corrected-calcium", methods=["POST"])
def api_corrected_calcium():
    data = request.get_json()
    try:
        result = calc_corrected_calcium(
            total_calcium=_get_float(data, "total_calcium"),
            albumin=_get_float(data, "albumin"),
        )
        return jsonify({"status": "success", "data": result})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


@health_bp.route("/api/atherogenic-index", methods=["POST"])
def api_atherogenic_index():
    data = request.get_json()
    try:
        result = calc_atherogenic_index(
            triglycerides=_get_float(data, "triglycerides"),
            hdl=_get_float(data, "hdl"),
        )
        return jsonify({"status": "success", "data": result})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


@health_bp.route("/api/ffmi", methods=["POST"])
def api_ffmi():
    data = request.get_json()
    try:
        result = calc_ffmi(
            weight_kg=_get_float(data, "weight_kg"),
            height_cm=_get_float(data, "height_cm"),
            body_fat_percent=_get_float(data, "body_fat_percent"),
        )
        return jsonify({"status": "success", "data": result})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


@health_bp.route("/api/lean-body-mass", methods=["POST"])
def api_lean_body_mass():
    data = request.get_json()
    try:
        result = calc_lean_body_mass(
            weight_kg=_get_float(data, "weight_kg"),
            body_fat_percent=_get_float(data, "body_fat_percent"),
            height_cm=_get_float(data, "height_cm"),
            gender=_get_str(data, "gender", "male"),
        )
        return jsonify({"status": "success", "data": result})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


@health_bp.route("/api/protein-intake", methods=["POST"])
def api_protein_intake():
    data = request.get_json()
    try:
        result = calc_protein_intake(
            weight_kg=_get_float(data, "weight_kg"),
            goal=_get_str(data, "goal", "maintain"),
            body_fat_percent=_get_float(data, "body_fat_percent"),
            activity_level=_get_str(data, "activity_level", "moderate"),
        )
        return jsonify({"status": "success", "data": result})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


@health_bp.route("/api/ideal-body-weight", methods=["POST"])
def api_ideal_body_weight():
    data = request.get_json()
    try:
        result = calc_ideal_body_weight(
            height_cm=_get_float(data, "height_cm"),
            gender=_get_str(data, "gender", "male"),
        )
        return jsonify({"status": "success", "data": result})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400
