from flask import Flask
from flask_restful import Resource, Api
from flask_cors import CORS
from flask import request

app = Flask(__name__)
CORS(app)
api = Api(app)

environments = {
    "ivt-nama": { "id": "ivt-nama", "name": "IVT Nama", "type": "ssh", "status": "idle" },
    "euler": { "id": "euler", "name": "Euler", "type": "lsf", "status": "idle" },
    "local": { "id": "local", "name": "Local", "type": "local_linux", "status": "idle" }
}

simulations = {}

import os
import environment as env

class ListEnvironments(Resource):
    def get(self):
        return environments

class Environment(Resource):
    def get(self, id):
        return environments[id]

    def delete(self, id):
        del environments[id]

    def put(self, id):
        if id in environments:
            return { "error": "ID exists already" }, 400

        if request.json["type"] == "local":
            try:
                environment = env.LocalEnvironment(request.json["path"])
                environments[id] = request.json
                return {}, 200
            except RuntimeError as e:
                return { "error": str(e) }, 400

        elif request.json["type"] == "ssh":
            print("SSH")
        elif request.json["type"] == "lsf":
            print("LSF")
        else:
            return { "error": "Invalid type" }, 400

        return {}, 500

class ListSimulations(Resource):
    def get(self):
        return simulations

class Simulation(Resource):
    def get(self, id):
        return simulations[id]

    def delete(self, id):
        del simulations[id]

    def put(self, id):
        if id in simulations:
            return { "error": "ID exists already" }, 400

        simulations[id] = request.json
        return {}, 200

api.add_resource(ListEnvironments, '/environments')
api.add_resource(Environment, '/environment/<string:id>')
api.add_resource(ListSimulations, '/simulations')
api.add_resource(Simulation, '/simulation/<string:id>')

if __name__ == '__main__':
    app.run(debug = True)
