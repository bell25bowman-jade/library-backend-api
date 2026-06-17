from datetime import date
from typing import List

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)


loan_book = db.Table(
    "loan_book",
    Base.metadata,
    db.Column("loan_id", db.ForeignKey("loans.id"), primary_key=True),
    db.Column("book_id", db.ForeignKey("books.id"), primary_key=True),
)


class Member(Base):
    __tablename__ = "members"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(255), nullable=False)
    email: Mapped[str] = mapped_column(db.String(360), nullable=False, unique=True)
    DOB: Mapped[date]
    password: Mapped[str] = mapped_column(db.String(255), nullable=False)

    loans: Mapped[List["Loan"]] = relationship(back_populates="member", cascade="all, delete")


class Loan(Base):
    __tablename__ = "loans"

    id: Mapped[int] = mapped_column(primary_key=True)
    loan_date: Mapped[date] = mapped_column(db.Date)
    member_id: Mapped[int] = mapped_column(db.ForeignKey("members.id"), nullable=False)

    member: Mapped["Member"] = relationship(back_populates="loans")
    books: Mapped[List["Book"]] = relationship(secondary=loan_book, back_populates="loans")


class Book(Base):
    __tablename__ = "books"

    id: Mapped[int] = mapped_column(primary_key=True)
    author: Mapped[str] = mapped_column(db.String(255), nullable=False)
    genre: Mapped[str] = mapped_column(db.String(255), nullable=False)
    desc: Mapped[str] = mapped_column(db.String(255), nullable=False)
    title: Mapped[str] = mapped_column(db.String(255), nullable=False)

    loans: Mapped[List["Loan"]] = relationship(secondary=loan_book, back_populates="books")
