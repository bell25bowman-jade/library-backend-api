# pyright: reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnknownArgumentType=false, reportUntypedFunctionDecorator=false

from typing import Any, cast
from flask import request, jsonify
from marshmallow import ValidationError
from sqlalchemy import select
from app.models import Member, db
from . import members_bp
from .schema import member_schema, members_schema
from app.extensions import limiter, cache
from app.blueprints.utils.util import encode_token


@members_bp.route('/login', methods=['POST'])
def login():
    try:
        credentials = request.json
        username = credentials['email']
        password = credentials['password']
    except KeyError:
        return jsonify({'messages': 'Invalid payload, expecting username and password'}), 400
    
    query =select(Member).where(Member.email == username) 
    member = db.session.execute(query).scalar_one_or_none() #Query user table for a user with this email

    if member and member.password == password: #if we have a user associated with the username, validate the password
        auth_token = encode_token(member.id)

        response = {
            "status": "success",
            "message": "Successfully Logged In",
            "auth_token": auth_token
        }
        return jsonify(response), 200
    else:
        return jsonify({'messages': "Invalid email or password"}), 401
                   
                   
                   
#CREATE member
@members_bp.route("/", methods=["POST"])
@limiter.limit("3 per hour")
def create_member():
    # Accept proper JSON requests, but also handle clients that forget headers.
    raw_payload = request.get_json(silent=True)
    if raw_payload is None and not request.is_json:
        raw_payload = request.get_json(silent=True, force=True)

    # Support form-encoded submissions as a fallback.
    if raw_payload is None and request.form:
        raw_payload = request.form.to_dict()

    if raw_payload is None:
        return jsonify({"error": "Provide a JSON object body (or form data) with member fields."}), 400

    if not isinstance(raw_payload, dict):
        return jsonify({"error": "JSON body must be an object."}), 400

    payload = cast(dict[str, Any], raw_payload)

    if "dob" in payload and "DOB" not in payload:
        payload["DOB"] = payload.pop("dob")

    try:
        member_data = cast(dict[str, Any], member_schema.load(payload))
    except ValidationError as err:
        return jsonify(cast(Any, err.messages)), 400

    query = select(Member).where(Member.email == member_data["email"])
    existing_member = db.session.execute(query).scalars().first()
    if existing_member:
        return jsonify({"error": "A member with this email already exists."}), 400

    new_member = Member(**member_data)
    db.session.add(new_member)
    db.session.commit()
    return jsonify(member_schema.dump(new_member)), 201

#GET all members
@members_bp.route("/", methods=["GET"])
@cache.cached(timeout=60)
def get_members():
    query = select(Member)
    members = db.session.execute(query).scalars().all()
    return jsonify(members_schema.dump(members)), 200

@members_bp.route("/<int:member_id>", methods=["GET"])
def get_member(member_id: int):
    member = db.session.get(Member, member_id)

    if member is None:
        return jsonify({"error": "Member not found."}), 404

    return jsonify(member_schema.dump(member)), 200

#UPDATE SPECIFIC MEMBER
@members_bp.route("/<int:member_id>", methods=['PUT'])
def update_member(member_id: int):
    member = db.session.get(Member, member_id)

    if not member:
        return jsonify({"error": "Member not found."}), 404
    
    raw_payload = request.get_json(silent=True)
    if raw_payload is None and not request.is_json:
        raw_payload = request.get_json(silent=True, force=True)

    if raw_payload is None and request.form:
        raw_payload = request.form.to_dict()

    if raw_payload is None:
        return jsonify({"error": "Provide a JSON object body (or form data) with member fields."}), 400

    if not isinstance(raw_payload, dict):
        return jsonify({"error": "JSON body must be an object."}), 400

    payload = cast(dict[str, Any], raw_payload)

    if "dob" in payload and "DOB" not in payload:
        payload["DOB"] = payload.pop("dob")

    try:
        member_data = cast(dict[str, Any], member_schema.load(payload))
    except ValidationError as err:
        return jsonify(cast(Any, err.messages)), 400
    
    for key, value in member_data.items():
        setattr(member, key, value)

    db.session.commit()
    return jsonify(member_schema.dump(member)), 200

#DELETE SPECIFIC MEMBER
@members_bp.route("/<int:member_id>", methods=['DELETE'])
def delete_member(member_id: int):
    member = db.session.get(Member, member_id)

    if not member:
        return jsonify({"error": "Member not found."}), 404
    
    db.session.delete(member)
    db.session.commit()
    return jsonify({"message": f'Member id: {member_id}, successfully deleted.'}), 200
    