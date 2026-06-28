# CalcHub

A full-stack calculator web application built with **Flask** and **Jinja2**, featuring **71 calculators** across Health, Finance, and Utility categories.

---

## Features

- **Primary / Derived taxonomy** — Health and Finance categories split calculators into standalone (Primary) and output-reusing (Derived) sections via a segmented tab UI
- **Auto-prefill** — Derived calculators read results from prerequisites stored in `localStorage`, eliminating re-entry
- **Pure-JS Utility calculators** — All Utility calculators run entirely in the browser with no backend API calls
- **Blueprint architecture** — `health_bp`, `finance_bp`, and `utility_bp` Flask blueprints keep routes isolated
- **INR formatting** — Finance results formatted with Indian locale (`formatINR`, `formatLakhsCr`)

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3, Flask, Blueprints |
| Templates | Jinja2 (extends `base.html`) |
| Frontend | Vanilla JS, CSS custom properties |
| Persistence | `localStorage` (key prefix `calcHub_`) |
| Formulas | US Navy / Mifflin-St Jeor / CKD-EPI / Friedewald / FFMI / Boer / James |

---

## Calculator Inventory

### Health (14 calculators)

#### Primary — Body Composition
| Calculator | URL | Description |
|---|---|---|
| BMI | `/health/bmi` | Body Mass Index (metric & imperial) |
| Body Fat % | `/health/body-fat` | US Navy method (skinfold) |
| BMR / TDEE | `/health/bmr-tdee` | Mifflin-St Jeor + activity multiplier |
| Water Intake | `/health/water-intake` | Daily hydration by weight & climate |

#### Primary — Heart & Lipids
| Calculator | URL | Description |
|---|---|---|
| LDL Cholesterol | `/health/ldl` | Friedewald equation |
| AIP | `/health/aip` | Atherogenic Index of Plasma |

#### Primary — Diabetes
| Calculator | URL | Description |
|---|---|---|
| HbA1c | `/health/hba1c` | Estimated average glucose |
| HOMA-IR | `/health/homa-ir` | Insulin resistance index |

#### Primary — Kidney & Electrolytes
| Calculator | URL | Description |
|---|---|---|
| eGFR | `/health/egfr` | CKD-EPI equation |
| Corrected Calcium | `/health/corrected-calcium` | Albumin-adjusted calcium |

#### Derived — Body Composition
| Calculator | URL | Uses |
|---|---|---|
| FFMI | `/health/ffmi` | Body Fat % + BMI |
| Lean Body Mass | `/health/lean-body-mass` | Body Fat % |
| Ideal Body Weight | `/health/ideal-body-weight` | BMI (height) |

#### Derived — Nutrition
| Calculator | URL | Uses |
|---|---|---|
| Protein Intake | `/health/protein-intake` | BMR/TDEE + Body Fat % |

---

### Finance (12 calculators)

#### Primary — Investments
| Calculator | URL | Description |
|---|---|---|
| SIP | `/finance/sip` | Systematic Investment Plan returns |
| Lumpsum | `/finance/lumpsum` | One-time investment growth |
| PPF | `/finance/ppf` | Public Provident Fund |
| FD | `/finance/fd` | Fixed Deposit maturity |
| RD | `/finance/rd` | Recurring Deposit |
| NPS | `/finance/nps` | National Pension Scheme |

#### Primary — Loans & Personal
| Calculator | URL | Description |
|---|---|---|
| EMI | `/finance/emi` | Loan EMI & amortisation |
| Home Loan | `/finance/home-loan` | Mortgage with prepayment |
| FIRE | `/finance/fire` | Financial Independence corpus |
| Retirement | `/finance/retirement` | Corpus needed at retirement |

#### Derived — Planning
| Calculator | URL | Uses |
|---|---|---|
| Retirement Readiness | `/finance/retirement-readiness` | Retirement + SIP |
| Inflation-adjusted Corpus | `/finance/inflation-corpus` | SIP / Lumpsum |

---

### Utility (45 calculators)

#### Time & Date (9)
| Calculator | URL |
|---|---|
| Age Calculator | `/utility/age` |
| Date Difference | `/utility/date-difference` |
| Business Days | `/utility/business-days` |
| Time Duration | `/utility/time-duration` |
| Countdown Timer | `/utility/countdown` |
| Day of Week | `/utility/day-of-week` |
| Leap Year Checker | `/utility/leap-year` |
| Time Zone Converter | `/utility/time-zone` |
| Unix Timestamp | `/utility/unix-timestamp` |

#### Percentage (8)
| Calculator | URL |
|---|---|
| Percentage | `/utility/percentage` |
| Percentage Increase | `/utility/percentage-increase` |
| Percentage Decrease | `/utility/percentage-decrease` |
| Percentage Difference | `/utility/percentage-difference` |
| Reverse Percentage | `/utility/reverse-percentage` |
| Discount | `/utility/discount` |
| Markup | `/utility/markup` |
| Margin | `/utility/margin` |

#### Unit Conversion (1 page, 12 categories)
| Page | URL | Categories |
|---|---|---|
| Unit Converter | `/utility/unit-converter` | Length, Weight, Temperature, Area, Volume, Speed, Pressure, Energy, Power, Fuel Economy, Data Storage, Cooking |

#### Mathematics (16)
| Calculator | URL |
|---|---|
| Scientific Calculator | `/utility/scientific` |
| Average | `/utility/average` |
| Median | `/utility/median` |
| Mode | `/utility/mode` |
| Standard Deviation | `/utility/std-dev` |
| Variance | `/utility/variance` |
| Fraction Calculator | `/utility/fraction` |
| Ratio | `/utility/ratio` |
| Decimal ↔ Fraction | `/utility/decimal-fraction` |
| Prime Number Checker | `/utility/prime-checker` |
| GCD & LCM | `/utility/gcd-lcm` |
| Factorial | `/utility/factorial` |
| Exponent | `/utility/exponent` |
| Square Root | `/utility/square-root` |
| Random Number Generator | `/utility/random-number` |

#### Everyday (8)
| Calculator | URL |
|---|---|
| Tip Calculator | `/utility/tip` |
| Split Bill | `/utility/split-bill` |
| Fuel Cost | `/utility/fuel-cost` |
| Electricity Cost | `/utility/electricity-cost` |
| Internet Speed Converter | `/utility/internet-speed` |
| Download Time | `/utility/download-time` |
| Pace Calculator | `/utility/pace` |
| Sleep Calculator | `/utility/sleep` |

---

## Project Structure

```
allcalculators/
├── app.py                        # Flask app factory, blueprint registration
├── calculators/
│   ├── metadata.py               # Central registry of all calculators
│   ├── health/
│   │   ├── __init__.py
│   │   ├── routes.py             # Page + API routes (health_bp)
│   │   └── engines.py            # Pure-Python calculation functions
│   ├── finance/
│   │   ├── __init__.py
│   │   ├── routes.py             # Page + API routes (finance_bp)
│   │   └── engines.py
│   └── utility/
│       ├── __init__.py
│       └── routes.py             # Page routes only (utility_bp)
├── templates/
│   ├── base.html                 # Navigation, head, shared layout
│   ├── home.html
│   ├── health/                   # 14 calculator templates
│   ├── finance/                  # 12 calculator templates
│   └── utility/
│       ├── index.html
│       ├── unit_converter.html
│       ├── time_date/            # 9 templates
│       ├── percentage/           # 8 templates
│       ├── math/                 # 16 templates (incl. scientific)
│       └── everyday/             # 8 templates
├── static/
│   ├── css/style.css             # Design system, segmented tabs, stat cards
│   └── js/utils.js               # localStorage helpers, slider sync, tab init
└── README.md
```

---

## Running Locally

```bash
# Install dependencies
pip install flask

# Run
python app.py
```

App starts at `http://localhost:5000`.

---

## Derived Calculator Flow

```
User runs BMI → result saved to localStorage["calcHub_bmi"]
User runs Body Fat → saved to localStorage["calcHub_bodyFat"]
User opens FFMI → weight/height/BF% auto-filled from stored results
                   Green "auto-filled" banner shown
```

If prerequisites are missing, an orange "Complete X first" banner guides the user.

---

## Formula References

| Calculator | Formula / Method |
|---|---|
| Body Fat % | US Navy circumference method |
| BMR | Mifflin-St Jeor equation |
| eGFR | CKD-EPI 2021 |
| LDL | Friedewald equation |
| FFMI | Fat-Free Mass Index (Kouri et al.) |
| LBM | Boer formula + James formula |
| IBW | Devine, Hamwi, Robinson formulas |
| SIP/Lumpsum | Compound interest with monthly compounding |
| EMI | Standard reducing-balance formula |
=======
# allcalculators
Fixing the typo