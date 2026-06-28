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
