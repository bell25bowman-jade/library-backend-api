from typing import Any, cast

from .schema import book_schema, books_schema
from flask import jsonify, request
from marshmallow import ValidationError
from sqlalchemy import select
from app.models import Book, db
from . import book_bp


@book_bp.route("/", methods=["POST"])
def create_book():
    raw_payload = request.get_json(silent=True)
    if raw_payload is None and not request.is_json:
        raw_payload = request.get_json(silent=True, force=True)

    if raw_payload is None and request.form:
        raw_payload = request.form.to_dict()

    if raw_payload is None:
        return jsonify({"error": "Provide a JSON object body (or form data) with book fields."}), 400

    if not isinstance(raw_payload, dict):
        return jsonify({"error": "JSON body must be an object."}), 400

    payload = cast(dict[str, Any], raw_payload)

    try:
        book_data = book_schema.load(payload)
    except ValidationError as err:
        return jsonify(err.messages), 400

    query = select(Book).where(Book.title == book_data["title"], Book.author == book_data["author"])
    existing_book = db.session.execute(query).scalars().first()
    if existing_book:
        return jsonify({"error": "This book already exists."}), 400

    new_book = Book(**book_data)
    db.session.add(new_book)
    db.session.commit()
    return book_schema.jsonify(new_book), 201


@book_bp.route("/", methods=["GET"])
def get_books():
    query = select(Book)
    books = db.session.execute(query).scalars().all()
    return books_schema.jsonify(books), 200


@book_bp.route("/<int:book_id>", methods=["GET"])
def get_book(book_id: int):
    book = db.session.get(Book, book_id)

    if book is None:
        return jsonify({"error": "Book not found."}), 404

    return book_schema.jsonify(book), 200


@book_bp.route("/<int:book_id>", methods=["PUT"])
def update_book(book_id: int):
    book = db.session.get(Book, book_id)

    if not book:
        return jsonify({"error": "Book not found."}), 404

    try:
        book_data = book_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400

    for key, value in book_data.items():
        setattr(book, key, value)

    db.session.commit()
    return book_schema.jsonify(book), 200


@book_bp.route("/<int:book_id>", methods=["DELETE"])
def delete_book(book_id: int):
    book = db.session.get(Book, book_id)

    if not book:
        return jsonify({"error": "Book not found."}), 404

    db.session.delete(book)
    db.session.commit()
    return jsonify({"message": f"Book id: {book_id}, successfully deleted."}), 200
