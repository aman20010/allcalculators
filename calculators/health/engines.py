import math


# ── General Health ──

def calc_bmi(weight_kg, height_cm):
    height_m = height_cm / 100
    bmi = weight_kg / (height_m ** 2)

    if bmi < 18.5:
        category = "Underweight"
        risk = "Low (but increased health risks from malnutrition)"
    elif bmi < 25:
        category = "Normal"
        risk = "Low"
    elif bmi < 30:
        category = "Overweight"
        risk = "Moderate"
    elif bmi < 35:
        category = "Obese (Class I)"
        risk = "High"
    elif bmi < 40:
        category = "Obese (Class II)"
        risk = "Very High"
    else:
        category = "Obese (Class III)"
        risk = "Extremely High"

    ideal_low = 18.5 * (height_m ** 2)
    ideal_high = 24.9 * (height_m ** 2)

    return {
        "bmi": round(bmi, 1),
        "category": category,
        "health_risk": risk,
        "ideal_weight_low": round(ideal_low, 1),
        "ideal_weight_high": round(ideal_high, 1),
        "weight_kg": weight_kg,
        "height_cm": height_cm,
    }


def calc_bmr_tdee(weight_kg, height_cm, age, gender, activity_level):
    """Mifflin-St Jeor equation."""
    if gender == "male":
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age + 5
    else:
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age - 161

    multipliers = {
        "sedentary": 1.2,
        "light": 1.375,
        "moderate": 1.55,
        "active": 1.725,
        "very_active": 1.9,
    }
    mult = multipliers.get(activity_level, 1.55)
    tdee = bmr * mult

    return {
        "bmr": round(bmr, 0),
        "tdee": round(tdee, 0),
        "activity_level": activity_level,
        "activity_multiplier": mult,
        "calories_to_lose_05kg": round(tdee - 500, 0),
        "calories_to_lose_1kg": round(tdee - 1000, 0),
        "calories_to_gain_05kg": round(tdee + 500, 0),
        "protein_g": round(weight_kg * 1.6, 0),
        "weight_kg": weight_kg,
        "height_cm": height_cm,
        "age": age,
        "gender": gender,
    }


def calc_body_fat(weight_kg, height_cm, age, gender, waist_cm, neck_cm, hip_cm=None):
    """US Navy method."""
    height_cm = max(height_cm, 1)
    if gender == "male":
        if waist_cm <= neck_cm:
            bf = 0
        else:
            bf = (
                86.010 * math.log10(waist_cm - neck_cm)
                - 70.041 * math.log10(height_cm)
                + 36.76
            )
    else:
        hip_cm = hip_cm or 0
        denom = waist_cm + hip_cm - neck_cm
        if denom <= 0:
            bf = 0
        else:
            bf = (
                163.205 * math.log10(denom)
                - 97.684 * math.log10(height_cm)
                - 78.387
            )

    bf = max(bf, 0)
    fat_mass = weight_kg * bf / 100
    lean_mass = weight_kg - fat_mass

    if gender == "male":
        if bf < 6:
            category = "Essential Fat"
        elif bf < 14:
            category = "Athletic"
        elif bf < 18:
            category = "Fitness"
        elif bf < 25:
            category = "Average"
        else:
            category = "Above Average"
    else:
        if bf < 14:
            category = "Essential Fat"
        elif bf < 21:
            category = "Athletic"
        elif bf < 25:
            category = "Fitness"
        elif bf < 32:
            category = "Average"
        else:
            category = "Above Average"

    return {
        "body_fat_percent": round(bf, 1),
        "category": category,
        "fat_mass_kg": round(fat_mass, 1),
        "lean_mass_kg": round(lean_mass, 1),
        "gender": gender,
    }


def calc_water_intake(weight_kg, activity_level, climate):
    base = weight_kg * 35  # ml per kg
    activity_add = {"sedentary": 0, "light": 350, "moderate": 700, "active": 1000, "very_active": 1400}
    climate_add = {"temperate": 0, "hot": 500, "humid": 400, "cold": 0}

    total_ml = base + activity_add.get(activity_level, 350) + climate_add.get(climate, 0)
    glasses = total_ml / 250

    return {
        "daily_water_ml": round(total_ml, 0),
        "daily_water_litres": round(total_ml / 1000, 1),
        "glasses_250ml": round(glasses, 0),
        "weight_kg": weight_kg,
        "activity_level": activity_level,
        "climate": climate,
    }


# ── Blood Report Markers ──

def calc_egfr(creatinine, age, gender, race_black=False):
    """CKD-EPI 2021 equation (race-free)."""
    scr = creatinine
    if gender == "female":
        kappa = 0.7
        alpha = -0.241
        female_mult = 1.012
    else:
        kappa = 0.9
        alpha = -0.302
        female_mult = 1.0

    egfr = 142 * (min(scr / kappa, 1) ** alpha) * (max(scr / kappa, 1) ** (-1.200)) * (0.9938 ** age) * female_mult

    if egfr >= 90:
        stage = "G1 — Normal or High"
        desc = "Normal kidney function"
    elif egfr >= 60:
        stage = "G2 — Mildly Decreased"
        desc = "Mildly reduced kidney function"
    elif egfr >= 45:
        stage = "G3a — Mild to Moderate"
        desc = "Mild to moderately reduced kidney function"
    elif egfr >= 30:
        stage = "G3b — Moderate to Severe"
        desc = "Moderately to severely reduced kidney function"
    elif egfr >= 15:
        stage = "G4 — Severely Decreased"
        desc = "Severely reduced kidney function"
    else:
        stage = "G5 — Kidney Failure"
        desc = "Kidney failure — dialysis or transplant may be needed"

    return {
        "egfr": round(egfr, 1),
        "stage": stage,
        "description": desc,
        "creatinine": creatinine,
        "age": age,
        "gender": gender,
        "unit": "mL/min/1.73m²",
    }


def calc_ldl_friedewald(total_cholesterol, hdl, triglycerides):
    """Friedewald formula: LDL = TC - HDL - (TG/5). Valid when TG < 400."""
    if triglycerides >= 400:
        return {
            "error": "Friedewald formula is not reliable when triglycerides >= 400 mg/dL. Use direct LDL measurement.",
            "triglycerides": triglycerides,
        }

    ldl = total_cholesterol - hdl - (triglycerides / 5)
    vldl = triglycerides / 5
    non_hdl = total_cholesterol - hdl
    tc_hdl_ratio = total_cholesterol / hdl if hdl > 0 else 0

    if ldl < 100:
        ldl_cat = "Optimal"
    elif ldl < 130:
        ldl_cat = "Near Optimal"
    elif ldl < 160:
        ldl_cat = "Borderline High"
    elif ldl < 190:
        ldl_cat = "High"
    else:
        ldl_cat = "Very High"

    if tc_hdl_ratio < 3.5:
        risk_cat = "Low Risk"
    elif tc_hdl_ratio < 5.0:
        risk_cat = "Moderate Risk"
    else:
        risk_cat = "High Risk"

    return {
        "ldl": round(ldl, 1),
        "ldl_category": ldl_cat,
        "vldl": round(vldl, 1),
        "non_hdl": round(non_hdl, 1),
        "tc_hdl_ratio": round(tc_hdl_ratio, 2),
        "cardiovascular_risk": risk_cat,
        "total_cholesterol": total_cholesterol,
        "hdl": hdl,
        "triglycerides": triglycerides,
        "unit": "mg/dL",
    }


def calc_homa_ir(fasting_glucose, fasting_insulin):
    """HOMA-IR = (Fasting Glucose mg/dL × Fasting Insulin µU/mL) / 405"""
    homa_ir = (fasting_glucose * fasting_insulin) / 405

    if homa_ir < 1.0:
        category = "Optimal — Insulin Sensitive"
    elif homa_ir < 1.9:
        category = "Normal"
    elif homa_ir < 2.9:
        category = "Early Insulin Resistance"
    else:
        category = "Significant Insulin Resistance"

    return {
        "homa_ir": round(homa_ir, 2),
        "category": category,
        "fasting_glucose": fasting_glucose,
        "fasting_insulin": fasting_insulin,
        "glucose_unit": "mg/dL",
        "insulin_unit": "µU/mL",
        "formula": f"({fasting_glucose} × {fasting_insulin}) / 405 = {round(homa_ir, 2)}",
    }


def calc_hba1c_to_glucose(hba1c=None, avg_glucose=None):
    """
    ADAG formula:
    eAG (mg/dL) = 28.7 × HbA1c − 46.7
    HbA1c = (eAG + 46.7) / 28.7
    """
    result = {}
    if hba1c is not None:
        eag = 28.7 * hba1c - 46.7
        result["hba1c"] = hba1c
        result["estimated_avg_glucose_mg_dl"] = round(eag, 1)
        result["estimated_avg_glucose_mmol_l"] = round(eag / 18.0, 1)
        result["direction"] = "hba1c_to_glucose"
    elif avg_glucose is not None:
        hba1c_val = (avg_glucose + 46.7) / 28.7
        result["avg_glucose_mg_dl"] = avg_glucose
        result["estimated_hba1c"] = round(hba1c_val, 1)
        result["direction"] = "glucose_to_hba1c"

    if "hba1c" in result:
        val = result["hba1c"]
    else:
        val = result.get("estimated_hba1c", 5.7)

    if val < 5.7:
        result["category"] = "Normal"
    elif val < 6.5:
        result["category"] = "Pre-Diabetic"
    else:
        result["category"] = "Diabetic Range"

    return result


def calc_corrected_calcium(total_calcium, albumin):
    """Corrected Calcium = Total Ca + 0.8 × (4.0 − Albumin)"""
    corrected = total_calcium + 0.8 * (4.0 - albumin)

    if corrected < 8.5:
        category = "Low (Hypocalcemia)"
    elif corrected <= 10.5:
        category = "Normal"
    else:
        category = "High (Hypercalcemia)"

    return {
        "corrected_calcium": round(corrected, 2),
        "category": category,
        "total_calcium": total_calcium,
        "albumin": albumin,
        "unit": "mg/dL",
        "formula": f"{total_calcium} + 0.8 × (4.0 − {albumin}) = {round(corrected, 2)}",
        "normal_range": "8.5 – 10.5 mg/dL",
    }


def calc_atherogenic_index(triglycerides, hdl):
    """AIP = log10(Triglycerides / HDL) — both in mg/dL."""
    if hdl <= 0:
        return {"error": "HDL must be greater than 0"}

    tg_mmol = triglycerides / 88.57
    hdl_mmol = hdl / 38.67
    aip = math.log10(tg_mmol / hdl_mmol)

    if aip < 0.11:
        risk = "Low Risk"
    elif aip < 0.21:
        risk = "Intermediate Risk"
    else:
        risk = "High Risk"

    return {
        "aip": round(aip, 3),
        "cardiovascular_risk": risk,
        "triglycerides": triglycerides,
        "hdl": hdl,
        "tg_hdl_ratio": round(triglycerides / hdl, 2),
        "unit": "mg/dL",
    }
