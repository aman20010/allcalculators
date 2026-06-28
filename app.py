from flask import Flask, render_template
from calculators.finance.routes import finance_bp
from calculators.health.routes import health_bp


def create_app():
    app = Flask(__name__)
    app.register_blueprint(finance_bp)
    app.register_blueprint(health_bp)

    @app.route("/")
    def home():
        return render_template("home.html")

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=5050)
