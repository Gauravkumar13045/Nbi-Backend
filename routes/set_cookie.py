from flask import Flask, request, make_response, jsonify

set_cookie = Flask(__name__)


@set_cookie.route("/set-cookie")
def set_cookie():
    responce = make_response(jsonify({"message": "Cookies set successfully"}))
    responce.set_cookie(
        "demo_token",
        "hello123",
        httponly=True,
        secure=False,
        samesite="Lax",
        max_age=300,
    )
    return responce


def read_cookie():
    token = request.cookies.get("demo_token")

    return jsonify({"cookie_value": token})


def delete_cookie():
    response = make_response(jsonify({"message": "Cookie deleted"}))

    response.delete_cookie("demo_taken")

    return response


if __name__ == "__main__":
    set_cookie.run(debug=True)
