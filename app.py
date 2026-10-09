"""Entry point for the ACEest Fitness & Gym Flask application.

Run locally with:
    python app.py
"""

import os

from aceest import create_app

app = create_app(os.environ.get("FLASK_CONFIG", "config.DevelopmentConfig"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
