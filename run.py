"""Development entry point: ``python run.py`` or ``flask --app run:app run``."""
from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True, port=5000)
