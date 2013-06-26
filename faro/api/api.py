from flask import Blueprint, jsonify, abort

api_endpoint = Blueprint('api_endpoint', __name__)

@api_endpoint.route('/')
def show():
    endpoints = ["v1.0"]
    try:
        return jsonify(endpoints=endpoints)
    except:
        abort(404)
