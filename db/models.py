from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.types import BigInteger
from sqlalchemy import ForeignKey

class Base(AsyncAttrs, DeclarativeBase):
    pass

class User(Base):
    __tablename__ = 'bot_user'
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, default=1, autoincrement=True)
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
        return {'id': self.id, "username": self.username}

class Account(Base):
    __tablename__ = 'accounts'
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, default=1, autoincrement=True)
    resource: Mapped[str]
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('bot_user.id'))
    user: Mapped['User'] = relationship('User', back_populates='accounts')

    def __str__(self):
        text = f"id: {self.id}, resource: {self.resource}"
        return text

    def __repr__(self):
        text = f"id: {self.id}, resource: {self.resource}"
        return text

    def model_dump(self):
        return {'id': self.id, 'resource': self.resource}

