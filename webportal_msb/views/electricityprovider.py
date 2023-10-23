from flask import Blueprint, make_response

provider = Blueprint("provider", __name__)

provider.route("/new-contract/", methods=["POST"])
def create_new_contract():
    return "New contract established", 200
