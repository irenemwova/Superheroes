from flask import Flask, request, jsonify
from flask_migrate import Migrate
from flask_restful import Api, Resource
from models import db, Hero, Power, HeroPower
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)
api = Api(app)

db.init_app(app)

@app.route('/')
def index():
    return '<h1>Code challenge</h1>'

class HeroListResource(Resource):
    def get(self):
        heroes = Hero.query.all()
        return jsonify([hero.to_dict(only=('id', 'name', 'super_name')) for hero in heroes])

class HeroResource(Resource):
    def get(self, hero_id):
        hero = Hero.query.get(hero_id)
        if hero:
            return jsonify(hero.to_dict())
        return jsonify({"error": "Hero not found"}), 404

class PowerListResource(Resource):
    def get(self):
        powers = Power.query.all()
        return jsonify([power.to_dict() for power in powers])

class PowerResource(Resource):
    def get(self, power_id):
        power = Power.query.get(power_id)
        if power:
            return jsonify(power.to_dict())
        return jsonify({"error": "Power not found"}), 404

    def patch(self, power_id):
        power = Power.query.get(power_id)
        if not power:
            return jsonify({"error": "Power not found"}), 404

        data = request.get_json()
        try:
            if 'description' in data:
                power.description = data['description']
                db.session.commit()
                return jsonify(power.to_dict())
        except ValueError as e:
            return jsonify({"errors": [str(e)]}), 400

class HeroPowerResource(Resource):
    def post(self):
        data = request.get_json()
        try:
            hero_power = HeroPower(
                strength=data['strength'],
                hero_id=data['hero_id'],
                power_id=data['power_id']
            )
            db.session.add(hero_power)
            db.session.commit()
            return jsonify(hero_power.to_dict())
        except ValueError as e:
            return jsonify({"errors": [str(e)]}), 400

api.add_resource(HeroListResource, '/heroes')
api.add_resource(HeroResource, '/heroes/<int:hero_id>')
api.add_resource(PowerListResource, '/powers')
api.add_resource(PowerResource, '/powers/<int:power_id>')
api.add_resource(HeroPowerResource, '/hero_powers')

if __name__ == '__main__':
    app.run(port=5555, debug=True)