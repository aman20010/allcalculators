from flask import Blueprint, render_template

utility_bp = Blueprint("utility", __name__, url_prefix="/utility")


@utility_bp.route("/")
def index():
    return render_template("utility/index.html")


# ── Time & Date ──
@utility_bp.route("/age")
def age():
    return render_template("utility/time_date/age.html")

@utility_bp.route("/date-difference")
def date_difference():
    return render_template("utility/time_date/date_difference.html")

@utility_bp.route("/business-days")
def business_days():
    return render_template("utility/time_date/business_days.html")

@utility_bp.route("/time-duration")
def time_duration():
    return render_template("utility/time_date/time_duration.html")

@utility_bp.route("/countdown")
def countdown():
    return render_template("utility/time_date/countdown.html")

@utility_bp.route("/day-of-week")
def day_of_week():
    return render_template("utility/time_date/day_of_week.html")

@utility_bp.route("/leap-year")
def leap_year():
    return render_template("utility/time_date/leap_year.html")

@utility_bp.route("/time-zone")
def time_zone():
    return render_template("utility/time_date/time_zone.html")

@utility_bp.route("/unix-timestamp")
def unix_timestamp():
    return render_template("utility/time_date/unix_timestamp.html")


# ── Percentage ──
@utility_bp.route("/percentage")
def percentage():
    return render_template("utility/percentage/percentage.html")

@utility_bp.route("/percentage-increase")
def percentage_increase():
    return render_template("utility/percentage/percentage_increase.html")

@utility_bp.route("/percentage-decrease")
def percentage_decrease():
    return render_template("utility/percentage/percentage_decrease.html")

@utility_bp.route("/percentage-difference")
def percentage_difference():
    return render_template("utility/percentage/percentage_difference.html")

@utility_bp.route("/reverse-percentage")
def reverse_percentage():
    return render_template("utility/percentage/reverse_percentage.html")

@utility_bp.route("/discount")
def discount():
    return render_template("utility/percentage/discount.html")

@utility_bp.route("/markup")
def markup():
    return render_template("utility/percentage/markup.html")

@utility_bp.route("/margin")
def margin():
    return render_template("utility/percentage/margin.html")


# ── Unit Conversion ──
@utility_bp.route("/unit-converter")
def unit_converter():
    return render_template("utility/unit_converter.html")


# ── Mathematics ──
@utility_bp.route("/scientific")
def scientific():
    return render_template("utility/math/scientific.html")

@utility_bp.route("/average")
def average():
    return render_template("utility/math/average.html")

@utility_bp.route("/median")
def median():
    return render_template("utility/math/median.html")

@utility_bp.route("/mode")
def mode():
    return render_template("utility/math/mode.html")

@utility_bp.route("/std-dev")
def std_dev():
    return render_template("utility/math/std_dev.html")

@utility_bp.route("/variance")
def variance():
    return render_template("utility/math/variance.html")

@utility_bp.route("/fraction")
def fraction():
    return render_template("utility/math/fraction.html")

@utility_bp.route("/ratio")
def ratio():
    return render_template("utility/math/ratio.html")

@utility_bp.route("/decimal-fraction")
def decimal_fraction():
    return render_template("utility/math/decimal_fraction.html")

@utility_bp.route("/prime-checker")
def prime_checker():
    return render_template("utility/math/prime_checker.html")

@utility_bp.route("/gcd-lcm")
def gcd_lcm():
    return render_template("utility/math/gcd_lcm.html")

@utility_bp.route("/factorial")
def factorial():
    return render_template("utility/math/factorial.html")

@utility_bp.route("/exponent")
def exponent():
    return render_template("utility/math/exponent.html")

@utility_bp.route("/square-root")
def square_root():
    return render_template("utility/math/square_root.html")

@utility_bp.route("/random-number")
def random_number():
    return render_template("utility/math/random_number.html")


# ── Everyday ──
@utility_bp.route("/tip")
def tip():
    return render_template("utility/everyday/tip.html")

@utility_bp.route("/split-bill")
def split_bill():
    return render_template("utility/everyday/split_bill.html")

@utility_bp.route("/fuel-cost")
def fuel_cost():
    return render_template("utility/everyday/fuel_cost.html")

@utility_bp.route("/electricity-cost")
def electricity_cost():
    return render_template("utility/everyday/electricity_cost.html")

@utility_bp.route("/internet-speed")
def internet_speed():
    return render_template("utility/everyday/internet_speed.html")

@utility_bp.route("/download-time")
def download_time():
    return render_template("utility/everyday/download_time.html")

@utility_bp.route("/pace")
def pace():
    return render_template("utility/everyday/pace.html")

@utility_bp.route("/sleep")
def sleep():
    return render_template("utility/everyday/sleep.html")


# ── New tools ──
@utility_bp.route("/gpa-calculator")
def gpa_calculator():
    return render_template("utility/everyday/gpa.html")

@utility_bp.route("/aspect-ratio")
def aspect_ratio():
    return render_template("utility/everyday/aspect_ratio.html")

@utility_bp.route("/password-generator")
def password_generator():
    return render_template("utility/everyday/password_generator.html")

@utility_bp.route("/word-counter")
def word_counter():
    return render_template("utility/everyday/word_counter.html")
