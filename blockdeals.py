from app import app
from app.views import users

if __name__ == "__main__":
    app.register_blueprint(users.user_blueprint)
    app.run(host='0.0.0.0', port=8000, debug=True)
