from flask import jsonify

def bad_request(message="Bad request"):
    return jsonify({
        "success": False,
        "message": message,
        "data": None
    }), 400


def unauthorized(message="Unauthorized"):
    return jsonify({
        "success": False,
        "message": message,
        "data": None
    }), 401


def not_found(message="Resource not found"):
    return jsonify({
        "success": False,
        "message": message,
        "data": None
    }), 404


def conflict(message="Conflict"):
    return jsonify({
        "success": False,
        "message": message,
        "data": None
    }), 409


def server_error(message="Internal server error"):
    return jsonify({
        "success": False,
        "message": message,
        "data": None
    }), 500

