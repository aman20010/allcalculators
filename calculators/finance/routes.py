from flask import Blueprint, request, jsonify, render_template
from .engines import (
    calc_pf, calc_sip, calc_sip_stepup, calc_sip_stepup_lumpsum,
    calc_gratuity, calc_emi, calc_ppf, calc_fd, calc_lumpsum,
    calc_retirement, adjust_for_inflation,
    calc_retirement_readiness, calc_inflation_corpus,
    calc_income_tax, calc_hra_exemption, calc_take_home_salary,
    calc_gst, calc_nps, calc_credit_card_payoff, calc_debt_snowball,
    calc_compound_interest, calc_rd,
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

@finance_bp.route("/income-tax")
def income_tax_page():
    return render_template("finance/income_tax.html")

@finance_bp.route("/hra")
def hra_page():
    return render_template("finance/hra.html")

@finance_bp.route("/take-home-salary")
def take_home_salary_page():
    return render_template("finance/take_home_salary.html")

@finance_bp.route("/gst")
def gst_page():
    return render_template("finance/gst.html")

@finance_bp.route("/nps")
def nps_page():
    return render_template("finance/nps.html")

@finance_bp.route("/credit-card-payoff")
def credit_card_payoff_page():
    return render_template("finance/credit_card_payoff.html")

@finance_bp.route("/debt-snowball")
def debt_snowball_page():
    return render_template("finance/debt_snowball.html")

@finance_bp.route("/compound-interest")
def compound_interest_page():
    return render_template("finance/compound_interest.html")

@finance_bp.route("/rd")
def rd_page():
    return render_template("finance/rd.html")

@finance_bp.route("/mortgage-calculator")
def mortgage_page():
    return render_template("finance/mortgage.html")

@finance_bp.route("/car-loan-calculator")
def car_loan_page():
    return render_template("finance/car_loan.html")


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


@finance_bp.route("/api/income-tax", methods=["POST"])
def api_income_tax():
    data = request.get_json()
    try:
        result = calc_income_tax(
            annual_income=_get_float(data, "annual_income"),
            deductions_80c=_get_float(data, "deductions_80c", 0),
            hra_exemption=_get_float(data, "hra_exemption", 0),
            other_deductions=_get_float(data, "other_deductions", 0),
            age_group=data.get("age_group", "below60"),
            standard_deduction=_get_bool(data, "standard_deduction", True),
        )
        return jsonify({"status": "success", "data": result})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


@finance_bp.route("/api/hra", methods=["POST"])
def api_hra():
    data = request.get_json()
    try:
        result = calc_hra_exemption(
            basic_salary=_get_float(data, "basic_salary"),
            hra_received=_get_float(data, "hra_received"),
            rent_paid=_get_float(data, "rent_paid"),
            da=_get_float(data, "da", 0),
            is_metro=_get_bool(data, "is_metro", True),
        )
        return jsonify({"status": "success", "data": result})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


@finance_bp.route("/api/take-home-salary", methods=["POST"])
def api_take_home_salary():
    data = request.get_json()
    try:
        result = calc_take_home_salary(
            ctc=_get_float(data, "ctc"),
            bonus=_get_float(data, "bonus", 0),
            basic_percent=_get_float(data, "basic_percent", 50),
            employer_pf_percent=_get_float(data, "employer_pf_percent", 12),
            employee_pf_percent=_get_float(data, "employee_pf_percent", 12),
            professional_tax=_get_float(data, "professional_tax", 2400),
            regime=data.get("regime", "new"),
            other_deductions=_get_float(data, "other_deductions", 0),
        )
        return jsonify({"status": "success", "data": result})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


@finance_bp.route("/api/gst", methods=["POST"])
def api_gst():
    data = request.get_json()
    try:
        result = calc_gst(
            amount=_get_float(data, "amount"),
            gst_rate=_get_float(data, "gst_rate", 18),
            calculation_type=data.get("calculation_type", "exclusive"),
        )
        return jsonify({"status": "success", "data": result})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


@finance_bp.route("/api/nps", methods=["POST"])
def api_nps():
    data = request.get_json()
    try:
        result = calc_nps(
            monthly_contribution=_get_float(data, "monthly_contribution"),
            current_age=int(data.get("current_age", 30)),
            retirement_age=int(data.get("retirement_age", 60)),
            expected_return_rate=_get_float(data, "expected_return_rate", 10),
            annuity_percent=_get_float(data, "annuity_percent", 40),
            annuity_rate=_get_float(data, "annuity_rate", 6),
        )
        return jsonify({"status": "success", "data": result})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


@finance_bp.route("/api/credit-card-payoff", methods=["POST"])
def api_credit_card_payoff():
    data = request.get_json()
    try:
        result = calc_credit_card_payoff(
            balance=_get_float(data, "balance"),
            apr=_get_float(data, "apr", 36),
            monthly_payment=_get_float(data, "monthly_payment"),
        )
        if "error" in result:
            return jsonify({"status": "error", "message": result["error"]}), 400
        return jsonify({"status": "success", "data": result})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


@finance_bp.route("/api/debt-snowball", methods=["POST"])
def api_debt_snowball():
    data = request.get_json()
    try:
        debts = data.get("debts", [])
        result = calc_debt_snowball(
            debts=debts,
            extra_payment=_get_float(data, "extra_payment", 0),
        )
        if "error" in result:
            return jsonify({"status": "error", "message": result["error"]}), 400
        return jsonify({"status": "success", "data": result})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


@finance_bp.route("/api/compound-interest", methods=["POST"])
def api_compound_interest():
    data = request.get_json()
    try:
        result = calc_compound_interest(
            principal=_get_float(data, "principal"),
            annual_rate=_get_float(data, "annual_rate", 10),
            time_years=_get_float(data, "time_years", 10),
            compounding_frequency=int(data.get("compounding_frequency", 12)),
            monthly_addition=_get_float(data, "monthly_addition", 0),
        )
        return jsonify({"status": "success", "data": result})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


@finance_bp.route("/api/rd", methods=["POST"])
def api_rd():
    data = request.get_json()
    try:
        result = calc_rd(
            monthly_deposit=_get_float(data, "monthly_deposit"),
            interest_rate=_get_float(data, "interest_rate", 7),
            tenure_months=int(data.get("tenure_months", 24)),
        )
        return jsonify({"status": "success", "data": result})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


@finance_bp.route("/api/mortgage", methods=["POST"])
def api_mortgage():
    data = request.get_json()
    try:
        result = calc_emi(
            principal=_get_float(data, "principal"),
            interest_rate=_get_float(data, "interest_rate", 8.5),
            tenure_months=int(data.get("tenure_months", 240)),
        )
        return jsonify({"status": "success", "data": result})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


@finance_bp.route("/api/car-loan", methods=["POST"])
def api_car_loan():
    data = request.get_json()
    try:
        result = calc_emi(
            principal=_get_float(data, "principal"),
            interest_rate=_get_float(data, "interest_rate", 9.0),
            tenure_months=int(data.get("tenure_months", 60)),
        )
        return jsonify({"status": "success", "data": result})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400
