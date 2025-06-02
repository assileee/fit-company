from flask import Flask
from .routes.userRoute import users_bp
from .routes.oauthRoute import auth_bp
from .routes.fitnessRoute import fitness_bp
from .routes.healthRoute import health_bp
from .database import init_db
from .services.fitness_data_init import init_fitness_data

app = Flask(__name__)

init_db()
init_fitness_data()

app.register_blueprint(health_bp)
app.register_blueprint(users_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(fitness_bp)

app.run(host="0.0.0.0", port=5000, debug=True)

