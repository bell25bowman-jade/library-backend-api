from typing import Any, cast

from .schema import edit_loan_schema, loan_schema, loans_schema
from flask import jsonify, request
from marshmallow import ValidationError
from sqlalchemy import select
from app.models import Book, Loan, Member, db
from . import loan_bp


@loan_bp.route("/", methods=["POST"])
def create_loan():
    raw_payload = request.get_json(silent=True)
    if raw_payload is None and not request.is_json:
        raw_payload = request.get_json(silent=True, force=True)

    if raw_payload is None and request.form:
        raw_payload = request.form.to_dict()

    if raw_payload is None:
        return jsonify({"error": "Provide a JSON object body (or form data) with loan fields."}), 400

    if not isinstance(raw_payload, dict):
        return jsonify({"error": "JSON body must be an object."}), 400

    payload = cast(dict[str, Any], raw_payload)

    # Accept common client-side key formats.
    if "memberId" in payload and "member_id" not in payload:
        payload["member_id"] = payload.pop("memberId")
    if "memberID" in payload and "member_id" not in payload:
        payload["member_id"] = payload.pop("memberID")
    if "member id" in payload and "member_id" not in payload:
        payload["member_id"] = payload.pop("member id")
    if "loanDate" in payload and "loan_date" not in payload:
        payload["loan_date"] = payload.pop("loanDate")
    if "loan date" in payload and "loan_date" not in payload:
        payload["loan_date"] = payload.pop("loan date")

    if "member_id" in payload and isinstance(payload["member_id"], str):
        raw_member_id = payload["member_id"].strip()
        if raw_member_id.isdigit():
            payload["member_id"] = int(raw_member_id)

    # Accept form-style values like "1,2,3" or "[1,2,3]" for book_ids.
    if "book_ids" in payload and isinstance(payload["book_ids"], str):
        raw_book_ids = payload["book_ids"].strip()
        if raw_book_ids == "":
            payload["book_ids"] = []
        else:
            cleaned = raw_book_ids.replace("[", "").replace("]", "")
            try:
                payload["book_ids"] = [int(part.strip()) for part in cleaned.split(",") if part.strip()]
            except ValueError:
                return jsonify({"error": "book_ids must be a list of integers."}), 400

    try:
        loan_data = loan_schema.load(payload)
    except ValidationError as err:
        return jsonify(err.messages), 400

    member = db.session.get(Member, loan_data["member_id"])
    if member is None:
        return jsonify({"error": "Member not found."}), 404

    book_ids = loan_data.pop("book_ids", [])
    books: list[Book] = []
    if book_ids:
        query = select(Book).where(Book.id.in_(book_ids))
        books = list(db.session.execute(query).scalars().all())
        if len(books) != len(set(book_ids)):
            return jsonify({"error": "One or more book_ids are invalid."}), 400

    new_loan = Loan(**loan_data)
    new_loan.books = books
    db.session.add(new_loan)
    db.session.commit()
    return loan_schema.jsonify(new_loan), 201


@loan_bp.route("/", methods=["GET"])
def get_loans():
    query = select(Loan)
    loans = db.session.execute(query).scalars().all()
    return loans_schema.jsonify(loans), 200


@loan_bp.route("/<int:loan_id>", methods=["GET"])
def get_loan(loan_id: int):
    loan = db.session.get(Loan, loan_id)

    if loan is None:
        return jsonify({"error": "Loan not found."}), 404

    return loan_schema.jsonify(loan), 200


@loan_bp.route("/<int:loan_id>", methods=["PUT"])
def edit_loan(loan_id: int):
    loan = db.session.get(Loan, loan_id)

    if loan is None:
        return jsonify({"error": "Loan not found."}), 404

    try:
        load_edits = cast(dict[str, list[int]], edit_loan_schema.load(request.json))
    except ValidationError as err:
        return jsonify(err.messages), 400

    for book_id in load_edits["add_book_ids"]:
        query = select(Book).where(Book.id == book_id)
        book = db.session.execute(query).scalars().first()

        if book and book not in loan.books:
            loan.books.append(book)

    for book_id in load_edits["remove_book_ids"]:
        query = select(Book).where(Book.id == book_id)
        book = db.session.execute(query).scalars().first()

        if book and book in loan.books:
            loan.books.remove(book)

    db.session.commit()
    return loan_schema.jsonify(loan), 200
            
@loan_bp.route("/<int:loan_id>", methods=["DELETE"])
def delete_loan(loan_id: int):
    loan = db.session.get(Loan, loan_id)

    if not loan:
        return jsonify({"error": "Loan not found."}), 404

    db.session.delete(loan)
    db.session.commit()
    return jsonify({"message": f"Loan id: {loan_id}, successfully deleted."}), 200
   
   