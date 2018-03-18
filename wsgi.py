from blockdeals import app
from app.views import users

app.register_blueprint(users.user_blueprint)

if __name__ == '__main__':
    app.run()
