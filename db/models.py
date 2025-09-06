from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.types import BigInteger
from sqlalchemy import ForeignKey

class Base(AsyncAttrs, DeclarativeBase):
    pass

class User(Base):
    __tablename__ = 'pas_users'
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    username: Mapped[str]
    password: Mapped[str]
    accounts: Mapped[list["Account"]] = relationship("Account", back_populates="user")

    def __str__(self):
        text = f"id: {self.id}, username: {self.username}"
        return text

    def __repr__(self):
        text = f"id: {self.id}, username: {self.username}"
        return text

    def model_dump(self):
        return {'id': self.id, "username": self.username, "password": self.password}

class Account(Base):
    __tablename__ = 'accounts'
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('pas_users.id'))
    user: Mapped['User'] = relationship('User', back_populates='accounts')
    params: Mapped[list['ParOfAcc']] = relationship('ParOfAcc', back_populates='account')

    def __str__(self):
        text = f"id: {self.id}"
        return text

    def __repr__(self):
        text = f"id: {self.id}"
        return text

    def model_dump(self):
        return {'id': self.id}

class ParOfAcc(Base):
    __tablename__ = 'params'
    id : Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    acc_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('accounts.id'))
    account: Mapped['Account'] = relationship('Account', back_populates='params')
    name: Mapped[str]
    content: Mapped[str]

    def __str__(self):
        text = f"id: {self.id}, name: {self.name}, content: {self.content}"
        return text

    def __repr__(self):
        text = f"id: {self.id}, name: {self.name}, content: {self.content}"
        return text

    def model_dump(self):
        return {'id': self.id, 'name': self.name, 'content': self.content}

