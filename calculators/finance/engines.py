def calc_retirement_readiness(corpus_needed, projected_corpus, years_to_retire):
    """Score retirement readiness 0–100 based on corpus gap."""
    if corpus_needed <= 0:
        return {"error": "Corpus needed must be greater than 0"}

    score = min(100, (projected_corpus / corpus_needed) * 100)
    shortfall = max(0, corpus_needed - projected_corpus)
    surplus = max(0, projected_corpus - corpus_needed)

    if score >= 100:
        status, color = "On Track", "green"
        message = "You're on track to meet your retirement goal."
    elif score >= 75:
        status, color = "Good Progress", "green"
        message = "Good progress — small adjustments will get you there."
    elif score >= 50:
        status, color = "Needs Attention", "orange"
        message = "You need to increase your monthly savings."
    elif score >= 25:
        status, color = "Behind Schedule", "red"
        message = "Significant savings increase required."
    else:
        status, color = "Critical Gap", "red"
        message = "Immediate action needed to close the retirement gap."

    extra_monthly = 0
    if shortfall > 0 and years_to_retire > 0:
        monthly_rate = 0.12 / 12
        months = years_to_retire * 12
        extra_monthly = shortfall * monthly_rate / (((1 + monthly_rate) ** months - 1) * (1 + monthly_rate))

    return {
        "readiness_score": round(score, 1),
        "status": status,
        "color": color,
        "message": message,
        "corpus_needed": round(corpus_needed, 2),
        "projected_corpus": round(projected_corpus, 2),
        "shortfall": round(shortfall, 2),
        "surplus": round(surplus, 2),
        "extra_monthly_needed": round(extra_monthly, 2),
        "years_to_retire": years_to_retire,
    }


def calc_inflation_corpus(corpus, years, inflation_rate=6.0):
    """Real purchasing power of a corpus after inflation."""
    if inflation_rate <= 0:
        return {
            "nominal_corpus": round(corpus, 2),
            "real_corpus": round(corpus, 2),
            "purchasing_power_loss": 0,
            "loss_percent": 0,
            "price_level_multiplier": 1.0,
            "inflation_rate": inflation_rate,
            "years": years,
        }

    factor = (1 + inflation_rate / 100) ** years
    real_corpus = corpus / factor
    loss = corpus - real_corpus

    return {
        "nominal_corpus": round(corpus, 2),
        "real_corpus": round(real_corpus, 2),
        "purchasing_power_loss": round(loss, 2),
        "loss_percent": round((loss / corpus) * 100, 1),
        "price_level_multiplier": round(factor, 2),
        "inflation_rate": inflation_rate,
        "years": years,
    }


def adjust_for_inflation(result, inflation_rate, years):
    if inflation_rate <= 0:
        return result
    factor = (1 + inflation_rate / 100) ** years
    adjusted = {}
    for key, val in result.items():
        if key == "yearly_breakdown":
            adj_breakdown = []
            for row in val:
                adj_row = {}
                yr = row.get("year", 1)
                yr_factor = (1 + inflation_rate / 100) ** yr
                for k, v in row.items():
                    if isinstance(v, (int, float)) and k != "year":
                        adj_row[k] = round(v / yr_factor, 2)
                    else:
                        adj_row[k] = v
                adj_breakdown.append(adj_row)
            adjusted[key] = adj_breakdown
        elif isinstance(val, (int, float)) and key not in (
            "time_years", "expected_return_rate", "monthly_investment",
            "annual_stepup_percent", "years_of_service", "is_covered_under_act",
            "max_exempt_limit", "employee_contrib_percent", "employer_contrib_percent",
            "epf_interest_rate", "annual_increment_percent", "da_percent",
            "interest_rate", "tenure_months", "tenure_years", "ppf_interest_rate",
            "fd_interest_rate", "compounding_frequency",
            "current_age", "retirement_age", "life_expectancy",
            "expected_return_pre", "expected_return_post", "monthly_expenses",
        ):
            adjusted[key] = round(val / factor, 2)
        else:
            adjusted[key] = val
    return adjusted


def calc_pf(basic_salary, da_percent, employee_contrib_percent, employer_contrib_percent,
            current_epf_balance, annual_increment_percent, years_to_retirement, epf_interest_rate):
    monthly_basic = basic_salary
    da = monthly_basic * da_percent / 100
    base = monthly_basic + da

    employee_rate = employee_contrib_percent / 100
    employer_rate = employer_contrib_percent / 100
    annual_rate = epf_interest_rate / 100
    monthly_rate = annual_rate / 12
    increment_rate = annual_increment_percent / 100

    balance = current_epf_balance
    total_employee = 0
    total_employer = 0
    total_interest = 0
    yearly_breakdown = []

    for year in range(1, years_to_retirement + 1):
        yearly_interest = 0
        yearly_emp_contrib = 0
        yearly_empr_contrib = 0

        for month in range(12):
            emp_contrib = base * employee_rate
            empr_contrib = base * employer_rate
            interest = balance * monthly_rate
            balance += emp_contrib + empr_contrib + interest
            yearly_emp_contrib += emp_contrib
            yearly_empr_contrib += empr_contrib
            yearly_interest += interest

        total_employee += yearly_emp_contrib
        total_employer += yearly_empr_contrib
        total_interest += yearly_interest

        yearly_breakdown.append({
            "year": year,
            "employee_contribution": round(yearly_emp_contrib, 2),
            "employer_contribution": round(yearly_empr_contrib, 2),
            "interest_earned": round(yearly_interest, 2),
            "balance": round(balance, 2),
        })
        base *= (1 + increment_rate)

    return {
        "maturity_amount": round(balance, 2),
        "total_employee_contribution": round(total_employee, 2),
        "total_employer_contribution": round(total_employer, 2),
        "total_interest_earned": round(total_interest, 2),
        "total_investment": round(total_employee + total_employer, 2),
        "yearly_breakdown": yearly_breakdown,
    }


def calc_sip(monthly_investment, expected_return_rate, time_years):
    monthly_rate = expected_return_rate / 100 / 12
    months = time_years * 12
    total_invested = monthly_investment * months

    if monthly_rate == 0:
        future_value = total_invested
    else:
        future_value = monthly_investment * (((1 + monthly_rate) ** months - 1) / monthly_rate) * (1 + monthly_rate)

    return {
        "invested_amount": round(total_invested, 2),
        "estimated_returns": round(future_value - total_invested, 2),
        "total_value": round(future_value, 2),
        "monthly_investment": monthly_investment,
        "time_years": time_years,
        "expected_return_rate": expected_return_rate,
    }


def calc_sip_stepup(monthly_investment, expected_return_rate, time_years, annual_stepup_percent):
    monthly_rate = expected_return_rate / 100 / 12
    total_invested = 0
    future_value = 0
    current_sip = monthly_investment
    yearly_breakdown = []

    for year in range(1, time_years + 1):
        yearly_invested = 0
        year_start_value = future_value

        for month in range(12):
            future_value = (future_value + current_sip) * (1 + monthly_rate)
            total_invested += current_sip
            yearly_invested += current_sip

        yearly_breakdown.append({
            "year": year,
            "monthly_sip": round(current_sip, 2),
            "yearly_invested": round(yearly_invested, 2),
            "corpus_at_year_end": round(future_value, 2),
            "gain_this_year": round(future_value - year_start_value - yearly_invested, 2),
        })
        current_sip *= (1 + annual_stepup_percent / 100)

    return {
        "invested_amount": round(total_invested, 2),
        "estimated_returns": round(future_value - total_invested, 2),
        "total_value": round(future_value, 2),
        "final_monthly_sip": round(current_sip / (1 + annual_stepup_percent / 100), 2),
        "yearly_breakdown": yearly_breakdown,
    }


def calc_sip_stepup_lumpsum(monthly_investment, expected_return_rate, time_years,
                             annual_stepup_percent, initial_lumpsum):
    monthly_rate = expected_return_rate / 100 / 12
    lumpsum_fv = initial_lumpsum * ((1 + monthly_rate) ** (time_years * 12))
    sip_result = calc_sip_stepup(monthly_investment, expected_return_rate, time_years, annual_stepup_percent)

    total_value = sip_result["total_value"] + lumpsum_fv
    total_invested = sip_result["invested_amount"] + initial_lumpsum

    return {
        "invested_amount": round(total_invested, 2),
        "estimated_returns": round(total_value - total_invested, 2),
        "total_value": round(total_value, 2),
        "lumpsum_growth": round(lumpsum_fv, 2),
        "sip_corpus": round(sip_result["total_value"], 2),
        "initial_lumpsum": initial_lumpsum,
        "yearly_breakdown": sip_result["yearly_breakdown"],
    }


def calc_gratuity(last_drawn_salary, years_of_service, is_covered_under_act=True):
    if is_covered_under_act:
        gratuity = (15 * last_drawn_salary * years_of_service) / 26
    else:
        gratuity = (15 * last_drawn_salary * years_of_service) / 30

    max_gratuity = 2500000
    taxable = max(0, gratuity - max_gratuity) if gratuity > max_gratuity else 0

    return {
        "gratuity_amount": round(gratuity, 2),
        "tax_exempt_amount": round(min(gratuity, max_gratuity), 2),
        "taxable_amount": round(taxable, 2),
        "last_drawn_salary": last_drawn_salary,
        "years_of_service": years_of_service,
        "is_covered_under_act": is_covered_under_act,
        "max_exempt_limit": max_gratuity,
    }


def calc_emi(principal, interest_rate, tenure_months):
    monthly_rate = interest_rate / 100 / 12
    if monthly_rate == 0:
        emi = principal / tenure_months
    else:
        emi = principal * monthly_rate * ((1 + monthly_rate) ** tenure_months) / (((1 + monthly_rate) ** tenure_months) - 1)

    total_payment = emi * tenure_months
    total_interest = total_payment - principal

    balance = principal
    yearly_breakdown = []
    yr_principal = 0
    yr_interest = 0

    for month in range(1, tenure_months + 1):
        interest_component = balance * monthly_rate
        principal_component = emi - interest_component
        balance -= principal_component
        yr_principal += principal_component
        yr_interest += interest_component

        if month % 12 == 0 or month == tenure_months:
            yearly_breakdown.append({
                "year": (month - 1) // 12 + 1,
                "principal_paid": round(yr_principal, 2),
                "interest_paid": round(yr_interest, 2),
                "balance": round(max(balance, 0), 2),
            })
            yr_principal = 0
            yr_interest = 0

    return {
        "emi": round(emi, 2),
        "total_payment": round(total_payment, 2),
        "total_interest": round(total_interest, 2),
        "principal": principal,
        "interest_rate": interest_rate,
        "tenure_months": tenure_months,
        "yearly_breakdown": yearly_breakdown,
    }


def calc_ppf(yearly_investment, ppf_interest_rate, time_years):
    rate = ppf_interest_rate / 100
    balance = 0
    total_invested = 0
    total_interest = 0
    yearly_breakdown = []

    for year in range(1, time_years + 1):
        balance += yearly_investment
        total_invested += yearly_investment
        interest = balance * rate
        balance += interest
        total_interest += interest

        yearly_breakdown.append({
            "year": year,
            "deposit": round(yearly_investment, 2),
            "interest_earned": round(interest, 2),
            "balance": round(balance, 2),
        })

    return {
        "maturity_amount": round(balance, 2),
        "total_invested": round(total_invested, 2),
        "total_interest": round(total_interest, 2),
        "ppf_interest_rate": ppf_interest_rate,
        "time_years": time_years,
        "yearly_breakdown": yearly_breakdown,
    }


def calc_fd(principal, interest_rate, tenure_years, compounding_frequency=4):
    n = compounding_frequency
    r = interest_rate / 100
    t = tenure_years

    maturity = principal * ((1 + r / n) ** (n * t))
    total_interest = maturity - principal

    yearly_breakdown = []
    for year in range(1, int(t) + 1):
        val = principal * ((1 + r / n) ** (n * year))
        yearly_breakdown.append({
            "year": year,
            "value": round(val, 2),
            "interest_this_year": round(val - (principal if year == 1 else yearly_breakdown[-2]["value"]), 2),
        })

    if t != int(t):
        val = principal * ((1 + r / n) ** (n * t))
        yearly_breakdown.append({
            "year": round(t, 1),
            "value": round(val, 2),
            "interest_this_year": round(val - yearly_breakdown[-1]["value"], 2) if yearly_breakdown else round(val - principal, 2),
        })

    return {
        "maturity_amount": round(maturity, 2),
        "total_interest": round(total_interest, 2),
        "principal": principal,
        "interest_rate": interest_rate,
        "tenure_years": tenure_years,
        "compounding_frequency": compounding_frequency,
        "yearly_breakdown": yearly_breakdown,
    }


def calc_lumpsum(principal, expected_return_rate, time_years):
    monthly_rate = expected_return_rate / 100 / 12
    months = time_years * 12
    future_value = principal * ((1 + monthly_rate) ** months)
    total_returns = future_value - principal

    yearly_breakdown = []
    for year in range(1, time_years + 1):
        val = principal * ((1 + monthly_rate) ** (year * 12))
        prev_val = principal if year == 1 else principal * ((1 + monthly_rate) ** ((year - 1) * 12))
        yearly_breakdown.append({
            "year": year,
            "value": round(val, 2),
            "gain_this_year": round(val - prev_val, 2),
        })

    return {
        "invested_amount": principal,
        "estimated_returns": round(total_returns, 2),
        "total_value": round(future_value, 2),
        "expected_return_rate": expected_return_rate,
        "time_years": time_years,
        "yearly_breakdown": yearly_breakdown,
    }


def calc_retirement(current_age, retirement_age, life_expectancy, monthly_expenses,
                    expected_return_pre, expected_return_post, existing_corpus=0):
    years_to_retire = retirement_age - current_age
    years_in_retirement = life_expectancy - retirement_age
    inflation = 6

    future_monthly_expenses = monthly_expenses * ((1 + inflation / 100) ** years_to_retire)
    future_yearly_expenses = future_monthly_expenses * 12

    post_rate = (expected_return_post - inflation) / 100
    if post_rate <= 0:
        corpus_needed = future_yearly_expenses * years_in_retirement
    else:
        corpus_needed = future_yearly_expenses * (1 - (1 + post_rate) ** (-years_in_retirement)) / post_rate

    pre_monthly_rate = expected_return_pre / 100 / 12
    existing_fv = existing_corpus * ((1 + pre_monthly_rate) ** (years_to_retire * 12))
    gap = max(0, corpus_needed - existing_fv)

    if pre_monthly_rate == 0:
        monthly_saving = gap / (years_to_retire * 12)
    else:
        months = years_to_retire * 12
        monthly_saving = gap * pre_monthly_rate / (((1 + pre_monthly_rate) ** months - 1) * (1 + pre_monthly_rate))

    return {
        "corpus_needed": round(corpus_needed, 2),
        "future_monthly_expenses": round(future_monthly_expenses, 2),
        "existing_corpus_future_value": round(existing_fv, 2),
        "gap": round(gap, 2),
        "monthly_saving_required": round(monthly_saving, 2),
        "yearly_saving_required": round(monthly_saving * 12, 2),
        "current_age": current_age,
        "retirement_age": retirement_age,
        "life_expectancy": life_expectancy,
        "years_to_retire": years_to_retire,
        "years_in_retirement": years_in_retirement,
        "monthly_expenses": monthly_expenses,
        "expected_return_pre": expected_return_pre,
        "expected_return_post": expected_return_post,
    }


# ── New engines ──

def _slab_tax(taxable, slabs):
    tax = 0.0
    prev = 0
    for upper, rate in slabs:
        if upper is None:
            tax += max(0, taxable - prev) * rate
            break
        if taxable > prev:
            tax += (min(taxable, upper) - prev) * rate
        prev = upper
    return tax


def _old_regime_tax(taxable, age_group="below60"):
    exemption = {"below60": 250000, "60to80": 300000, "above80": 500000}.get(age_group, 250000)
    if exemption == 500000:
        slabs = [(500000, 0), (1000000, 0.2), (None, 0.3)]
    elif exemption == 300000:
        slabs = [(300000, 0), (500000, 0.05), (1000000, 0.2), (None, 0.3)]
    else:
        slabs = [(250000, 0), (500000, 0.05), (1000000, 0.2), (None, 0.3)]
    tax_raw = _slab_tax(taxable, slabs)
    rebate = tax_raw if taxable <= 500000 else 0
    tax = max(0, tax_raw - rebate)
    cess = tax * 0.04
    total = tax + cess
    return {
        "taxable_income": round(taxable, 2),
        "tax_before_cess": round(tax, 2),
        "cess": round(cess, 2),
        "total_tax": round(total, 2),
        "rebate_applied": round(rebate, 2),
        "effective_rate": round((total / taxable * 100) if taxable else 0, 2),
        "monthly_tax": round(total / 12, 2),
    }


def _new_regime_tax(taxable):
    slabs = [
        (400000, 0), (800000, 0.05), (1200000, 0.10),
        (1600000, 0.15), (2000000, 0.20), (2400000, 0.25), (None, 0.30),
    ]
    tax_raw = _slab_tax(taxable, slabs)
    rebate = tax_raw if taxable <= 1200000 else 0
    tax = max(0, tax_raw - rebate)
    cess = tax * 0.04
    total = tax + cess
    return {
        "taxable_income": round(taxable, 2),
        "tax_before_cess": round(tax, 2),
        "cess": round(cess, 2),
        "total_tax": round(total, 2),
        "rebate_applied": round(rebate, 2),
        "effective_rate": round((total / taxable * 100) if taxable else 0, 2),
        "monthly_tax": round(total / 12, 2),
    }


def calc_income_tax(annual_income, deductions_80c=0, hra_exemption=0,
                    other_deductions=0, age_group="below60", standard_deduction=True):
    old_taxable = max(0, annual_income
                      - (50000 if standard_deduction else 0)
                      - deductions_80c - hra_exemption - other_deductions)
    new_taxable = max(0, annual_income - (75000 if standard_deduction else 0))
    old = _old_regime_tax(old_taxable, age_group)
    new = _new_regime_tax(new_taxable)
    recommended = "new" if new["total_tax"] <= old["total_tax"] else "old"
    savings = abs(old["total_tax"] - new["total_tax"])
    return {
        "annual_income": round(annual_income, 2),
        "old_regime": old,
        "new_regime": new,
        "recommended_regime": recommended,
        "tax_savings": round(savings, 2),
        "in_hand_old": round(annual_income - old["total_tax"], 2),
        "in_hand_new": round(annual_income - new["total_tax"], 2),
    }


def calc_hra_exemption(basic_salary, hra_received, rent_paid, da=0, is_metro=True):
    base = basic_salary + da
    rent_minus_10 = max(0, rent_paid - 0.10 * base)
    metro_limit = base * (0.50 if is_metro else 0.40)
    exempt = min(hra_received, rent_minus_10, metro_limit)
    taxable_hra = max(0, hra_received - exempt)
    return {
        "monthly_exempt_hra": round(exempt, 2),
        "annual_exempt_hra": round(exempt * 12, 2),
        "monthly_taxable_hra": round(taxable_hra, 2),
        "annual_taxable_hra": round(taxable_hra * 12, 2),
        "actual_hra_received": round(hra_received, 2),
        "rent_minus_10pct_salary": round(rent_minus_10, 2),
        "metro_limit": round(metro_limit, 2),
    }


def calc_take_home_salary(ctc, bonus=0, basic_percent=50, employer_pf_percent=12,
                           employee_pf_percent=12, professional_tax=2400,
                           regime="new", other_deductions=0):
    fixed_ctc = ctc - bonus
    basic = fixed_ctc * (basic_percent / 100)
    employer_pf = basic * (employer_pf_percent / 100)
    gratuity = basic * 0.0481
    gross_salary = fixed_ctc - employer_pf - gratuity
    employee_pf = basic * (employee_pf_percent / 100)
    taxable_gross = gross_salary - employee_pf - other_deductions
    tax_result = calc_income_tax(taxable_gross, standard_deduction=True)
    income_tax = (tax_result["new_regime"]["total_tax"] if regime == "new"
                  else tax_result["old_regime"]["total_tax"])
    annual_take_home = gross_salary - employee_pf - professional_tax - income_tax + bonus
    return {
        "ctc": round(ctc, 2),
        "gross_salary": round(gross_salary, 2),
        "basic_salary": round(basic, 2),
        "employer_pf": round(employer_pf, 2),
        "gratuity_contribution": round(gratuity, 2),
        "employee_pf": round(employee_pf, 2),
        "professional_tax": round(professional_tax, 2),
        "income_tax": round(income_tax, 2),
        "bonus": round(bonus, 2),
        "annual_take_home": round(annual_take_home, 2),
        "monthly_take_home": round(annual_take_home / 12, 2),
        "regime": regime,
        "monthly_gross": round(gross_salary / 12, 2),
    }


def calc_gst(amount, gst_rate=18, calculation_type="exclusive"):
    rate = gst_rate / 100
    if calculation_type == "exclusive":
        gst_amount = amount * rate
        base = amount
        total = amount + gst_amount
    else:
        base = amount / (1 + rate)
        gst_amount = amount - base
        total = amount
    return {
        "base_amount": round(base, 2),
        "gst_amount": round(gst_amount, 2),
        "cgst": round(gst_amount / 2, 2),
        "sgst": round(gst_amount / 2, 2),
        "total_amount": round(total, 2),
        "gst_rate": gst_rate,
        "calculation_type": calculation_type,
    }


def calc_nps(monthly_contribution, current_age, retirement_age=60,
             expected_return_rate=10, annuity_percent=40, annuity_rate=6):
    months = (retirement_age - current_age) * 12
    monthly_rate = expected_return_rate / 100 / 12
    if monthly_rate == 0:
        corpus = monthly_contribution * months
    else:
        corpus = monthly_contribution * (((1 + monthly_rate) ** months - 1) / monthly_rate) * (1 + monthly_rate)
    total_invested = monthly_contribution * months
    lump_sum = corpus * (1 - annuity_percent / 100)
    annuity_corpus = corpus * (annuity_percent / 100)
    monthly_pension = annuity_corpus * (annuity_rate / 100) / 12
    return {
        "total_corpus": round(corpus, 2),
        "total_invested": round(total_invested, 2),
        "estimated_returns": round(corpus - total_invested, 2),
        "lump_sum_withdrawal": round(lump_sum, 2),
        "annuity_corpus": round(annuity_corpus, 2),
        "monthly_pension": round(monthly_pension, 2),
        "years_to_retirement": retirement_age - current_age,
    }


def calc_credit_card_payoff(balance, apr, monthly_payment):
    monthly_rate = apr / 100 / 12
    min_required = balance * monthly_rate
    if monthly_payment <= min_required:
        return {"error": f"Monthly payment must exceed ₹{round(min_required, 2)} to pay off this balance."}
    bal = float(balance)
    months = 0
    total_interest = 0.0
    schedule = []
    while bal > 0.005 and months < 600:
        interest = bal * monthly_rate
        principal_paid = min(monthly_payment - interest, bal)
        bal = max(0, bal - principal_paid)
        total_interest += interest
        months += 1
        if months <= 24 or bal <= 0:
            schedule.append({
                "month": months,
                "interest": round(interest, 2),
                "principal": round(principal_paid, 2),
                "balance": round(bal, 2),
            })
    return {
        "months_to_payoff": months,
        "years_to_payoff": months // 12,
        "remaining_months": months % 12,
        "total_interest_paid": round(total_interest, 2),
        "total_paid": round(balance + total_interest, 2),
        "schedule": schedule,
    }


def calc_debt_snowball(debts, extra_payment=0):
    if not debts:
        return {"error": "Add at least one debt."}
    queue = sorted([dict(d) for d in debts], key=lambda d: d["balance"])
    for d in queue:
        d["remaining"] = float(d["balance"])
    snowball_pool = float(extra_payment)
    months = 0
    total_interest = 0.0
    payoff_order = []
    while any(d["remaining"] > 0.01 for d in queue) and months < 600:
        months += 1
        available_extra = snowball_pool
        for d in queue:
            if d["remaining"] <= 0.01:
                continue
            interest = d["remaining"] * (d["apr"] / 100 / 12)
            total_interest += interest
            d["remaining"] += interest
            payment = d["min_payment"]
            if available_extra > 0:
                payment += available_extra
                available_extra = 0
            paid = min(payment, d["remaining"])
            d["remaining"] = max(0, d["remaining"] - paid)
            if d["remaining"] <= 0.01 and d["name"] not in payoff_order:
                payoff_order.append(d["name"])
                snowball_pool += d["min_payment"]
    total_balance = sum(d["balance"] for d in debts)
    return {
        "months_to_debt_free": months,
        "years_to_debt_free": months // 12,
        "remaining_months": months % 12,
        "total_interest_paid": round(total_interest, 2),
        "total_starting_balance": round(total_balance, 2),
        "total_paid": round(total_balance + total_interest, 2),
        "payoff_order": payoff_order,
    }


def calc_compound_interest(principal, annual_rate, time_years,
                            compounding_frequency=12, monthly_addition=0):
    n = compounding_frequency
    r = annual_rate / 100
    lump_fv = principal * ((1 + r / n) ** (n * time_years))
    monthly_rate = r / 12
    months = int(time_years * 12)
    if monthly_addition and monthly_rate > 0:
        addition_fv = monthly_addition * (((1 + monthly_rate) ** months - 1) / monthly_rate) * (1 + monthly_rate)
    elif monthly_addition:
        addition_fv = monthly_addition * months
    else:
        addition_fv = 0
    total_value = lump_fv + addition_fv
    total_invested = principal + monthly_addition * months
    yearly_breakdown = []
    for yr in range(1, int(time_years) + 1):
        lv = principal * ((1 + r / n) ** (n * yr))
        av = 0
        if monthly_addition and monthly_rate > 0:
            av = monthly_addition * (((1 + monthly_rate) ** (yr * 12) - 1) / monthly_rate) * (1 + monthly_rate)
        elif monthly_addition:
            av = monthly_addition * yr * 12
        invested_yr = principal + monthly_addition * yr * 12
        yearly_breakdown.append({
            "year": yr,
            "value": round(lv + av, 2),
            "invested": round(invested_yr, 2),
            "interest": round(lv + av - invested_yr, 2),
        })
    return {
        "principal": principal,
        "total_invested": round(total_invested, 2),
        "interest_earned": round(total_value - total_invested, 2),
        "maturity_amount": round(total_value, 2),
        "annual_rate": annual_rate,
        "time_years": time_years,
        "compounding_frequency": n,
        "yearly_breakdown": yearly_breakdown,
    }


def calc_rd(monthly_deposit, interest_rate, tenure_months):
    quarterly_rate = interest_rate / 100 / 4
    balance = 0.0
    total_invested = 0.0
    for month in range(1, tenure_months + 1):
        balance += monthly_deposit
        total_invested += monthly_deposit
        if month % 3 == 0:
            balance += balance * quarterly_rate
    remainder = tenure_months % 3
    if remainder:
        balance += balance * quarterly_rate * (remainder / 3)
    return {
        "maturity_amount": round(balance, 2),
        "total_invested": round(total_invested, 2),
        "interest_earned": round(balance - total_invested, 2),
        "monthly_deposit": monthly_deposit,
        "interest_rate": interest_rate,
        "tenure_months": tenure_months,
    }
