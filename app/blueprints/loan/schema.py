from marshmallow import fields

from app.extensions import ma
from app.models import Loan


class LoanSchema(ma.SQLAlchemyAutoSchema):
    book_ids = fields.List(fields.Int(), load_only=True)
    books = fields.Method("get_book_ids", dump_only=True)

    class Meta:
        model = Loan
        load_instance = False
        include_fk = True

    def get_book_ids(self, obj: Loan):
        return [book.id for book in obj.books]

class EditLoanSchema(ma.Schema):
    add_book_ids = fields.List(fields.Int(), required=True)
    remove_book_ids = fields.List(fields.Int(), required=True)
    class Meta:
        fields = ("add_book_ids", "remove_book_ids")

loan_schema = LoanSchema()
loans_schema = LoanSchema(many=True)
edit_loan_schema = EditLoanSchema()


