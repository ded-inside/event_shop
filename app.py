from app import app, generate_default_state
from app import routes

if __name__ == "__main__":
    generate_default_state()
    app.run(port=5000)
