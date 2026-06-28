from flask import Blueprint, request, jsonify, render_template
from .engines import (
    calc_pf, calc_sip, calc_sip_stepup, calc_sip_stepup_lumpsum,
    calc_gratuity, calc_emi, calc_ppf, calc_fd, calc_lumpsum,
    calc_retirement, adjust_for_inflation,
    calc_retirement_readiness, calc_inflation_corpus,
)

finance_bp = Blueprint("finance", __name__, url_prefix="/finance")


def _get_float(data, key, default=None):
    val = data.get(key, default)
    if val is None:
        return None
    return float(val)


def _get_bool(data, key, default=True):
    val = data.get(key, default)
    if isinstance(val, bool):
        return val
    if isinstance(val, str):
        return val.lower() in ("true", "1", "yes")
    return bool(val)


def _with_inflation(result, data, default_years_key="time_years"):
    inflation_rate = _get_float(data, "inflation_rate", 0)
    years = _get_float(data, default_years_key, 10)
    if inflation_rate and inflation_rate > 0 and years:
        result["inflation_adjusted"] = adjust_for_inflation(result, inflation_rate, years)
        result["inflation_rate"] = inflation_rate
    return result


# ── Page routes ──

@finance_bp.route("/")
def index():
    return render_template("finance/index.html")

@finance_bp.route("/pf")
def pf_page():
    return render_template("finance/pf.html")

@finance_bp.route("/sip")
def sip_page():
    return render_template("finance/sip.html")

@finance_bp.route("/sip-stepup")
def sip_stepup_page():
    return render_template("finance/sip_stepup.html")

@finance_bp.route("/sip-stepup-lumpsum")
def sip_stepup_lumpsum_page():
    return render_template("finance/sip_stepup_lumpsum.html")

@finance_bp.route("/gratuity")
def gratuity_page():
    return render_template("finance/gratuity.html")

@finance_bp.route("/emi")
def emi_page():
    return render_template("finance/emi.html")

@finance_bp.route("/ppf")
def ppf_page():
    return render_template("finance/ppf.html")

@finance_bp.route("/fd")
def fd_page():
    return render_template("finance/fd.html")

@finance_bp.route("/lumpsum")
def lumpsum_page():
    return render_template("finance/lumpsum.html")

@finance_bp.route("/retirement")
def retirement_page():
    return render_template("finance/retirement.html")

@finance_bp.route("/retirement-readiness")
def retirement_readiness_page():
    return render_template("finance/retirement_readiness.html")

@finance_bp.route("/inflation-corpus")
def inflation_corpus_page():
    return render_template("finance/inflation_corpus.html")


# ── API routes ──

@finance_bp.route("/api/pf", methods=["POST"])
def api_pf():
    data = request.get_json()
    try:
        result = calc_pf(
            basic_salary=_get_float(data, "basic_salary"),
            da_percent=_get_float(data, "da_percent", 0),
            employee_contrib_percent=_get_float(data, "employee_contrib_percent", 12),
            employer_contrib_percent=_get_float(data, "employer_contrib_percent", 3.67),
            current_epf_balance=_get_float(data, "current_epf_balance", 0),
            annual_increment_percent=_get_float(data, "annual_increment_percent", 5),
            years_to_retirement=int(data.get("years_to_retirement", 30)),
            epf_interest_rate=_get_float(data, "epf_interest_rate", 8.25),
        )
        result = _with_inflation(result, data, "years_to_retirement")
        return jsonify({"status": "success", "data": result})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


@finance_bp.route("/api/sip", methods=["POST"])
def api_sip():
    data = request.get_json()
    try:
        result = calc_sip(
            monthly_investment=_get_float(data, "monthly_investment"),
            expected_return_rate=_get_float(data, "expected_return_rate", 12),
            time_years=int(data.get("time_years", 10)),
        )
        result = _with_inflation(result, data)
        return jsonify({"status": "success", "data": result})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


@finance_bp.route("/api/sip-stepup", methods=["POST"])
def api_sip_stepup():
    data = request.get_json()
    try:
        result = calc_sip_stepup(
            monthly_investment=_get_float(data, "monthly_investment"),
            expected_return_rate=_get_float(data, "expected_return_rate", 12),
            time_years=int(data.get("time_years", 10)),
            annual_stepup_percent=_get_float(data, "annual_stepup_percent", 10),
        )
        result = _with_inflation(result, data)
        return jsonify({"status": "success", "data": result})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


@finance_bp.route("/api/sip-stepup-lumpsum", methods=["POST"])
def api_sip_stepup_lumpsum():
    data = request.get_json()
    try:
        result = calc_sip_stepup_lumpsum(
            monthly_investment=_get_float(data, "monthly_investment"),
            expected_return_rate=_get_float(data, "expected_return_rate", 12),
            time_years=int(data.get("time_years", 10)),
            annual_stepup_percent=_get_float(data, "annual_stepup_percent", 10),
            initial_lumpsum=_get_float(data, "initial_lumpsum", 0),
        )
        result = _with_inflation(result, data)
        return jsonify({"status": "success", "data": result})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


@finance_bp.route("/api/gratuity", methods=["POST"])
def api_gratuity():
    data = request.get_json()
    try:
        result = calc_gratuity(
            last_drawn_salary=_get_float(data, "last_drawn_salary"),
            years_of_service=_get_float(data, "years_of_service"),
            is_covered_under_act=_get_bool(data, "is_covered_under_act", True),
        )
        result = _with_inflation(result, data, "years_of_service")
        return jsonify({"status": "success", "data": result})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


@finance_bp.route("/api/emi", methods=["POST"])
def api_emi():
    data = request.get_json()
    try:
        result = calc_emi(
            principal=_get_float(data, "principal"),
            interest_rate=_get_float(data, "interest_rate", 8.5),
            tenure_months=int(data.get("tenure_months", 240)),
        )
        tenure_years = int(data.get("tenure_months", 240)) / 12
        data["time_years"] = tenure_years
        result = _with_inflation(result, data)
        return jsonify({"status": "success", "data": result})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


@finance_bp.route("/api/ppf", methods=["POST"])
def api_ppf():
    data = request.get_json()
    try:
        result = calc_ppf(
            yearly_investment=_get_float(data, "yearly_investment"),
            ppf_interest_rate=_get_float(data, "ppf_interest_rate", 7.1),
            time_years=int(data.get("time_years", 15)),
        )
        result = _with_inflation(result, data)
        return jsonify({"status": "success", "data": result})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


@finance_bp.route("/api/fd", methods=["POST"])
def api_fd():
    data = request.get_json()
    try:
        result = calc_fd(
            principal=_get_float(data, "principal"),
            interest_rate=_get_float(data, "interest_rate", 7),
            tenure_years=_get_float(data, "tenure_years", 5),
            compounding_frequency=int(data.get("compounding_frequency", 4)),
        )
        data["time_years"] = data.get("tenure_years", 5)
        result = _with_inflation(result, data)
        return jsonify({"status": "success", "data": result})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


@finance_bp.route("/api/lumpsum", methods=["POST"])
def api_lumpsum():
    data = request.get_json()
    try:
        result = calc_lumpsum(
            principal=_get_float(data, "principal"),
            expected_return_rate=_get_float(data, "expected_return_rate", 12),
            time_years=int(data.get("time_years", 10)),
        )
        result = _with_inflation(result, data)
        return jsonify({"status": "success", "data": result})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


@finance_bp.route("/api/retirement", methods=["POST"])
def api_retirement():
    data = request.get_json()
    try:
        result = calc_retirement(
            current_age=int(data.get("current_age", 30)),
            retirement_age=int(data.get("retirement_age", 60)),
            life_expectancy=int(data.get("life_expectancy", 80)),
            monthly_expenses=_get_float(data, "monthly_expenses", 50000),
            expected_return_pre=_get_float(data, "expected_return_pre", 12),
            expected_return_post=_get_float(data, "expected_return_post", 8),
            existing_corpus=_get_float(data, "existing_corpus", 0),
        )
        years = int(data.get("retirement_age", 60)) - int(data.get("current_age", 30))
        data["time_years"] = years
        result = _with_inflation(result, data)
        return jsonify({"status": "success", "data": result})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


@finance_bp.route("/api/retirement-readiness", methods=["POST"])
def api_retirement_readiness():
    data = request.get_json()
    try:
        result = calc_retirement_readiness(
            corpus_needed=_get_float(data, "corpus_needed"),
            projected_corpus=_get_float(data, "projected_corpus"),
            years_to_retire=int(data.get("years_to_retire", 30)),
        )
        return jsonify({"status": "success", "data": result})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


@finance_bp.route("/api/inflation-corpus", methods=["POST"])
def api_inflation_corpus():
    data = request.get_json()
    try:
        result = calc_inflation_corpus(
            corpus=_get_float(data, "corpus"),
            years=int(data.get("years", 20)),
            inflation_rate=_get_float(data, "inflation_rate", 6.0),
        )
        return jsonify({"status": "success", "data": result})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400
