from sqlalchemy import ForeignKey
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.types import BigInteger, String


class Base(AsyncAttrs, DeclarativeBase):
    pass


class Users(Base):
    __tablename__ = "pas_users"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    username: Mapped[str]
    password: Mapped[str] = mapped_column(String(256))
    accounts: Mapped[list["Accounts"]] = relationship("Accounts", back_populates="user")
    actions: Mapped[list["UsersActions"]] = relationship(
        "UsersActions", back_populates="user"
    )
    roles: Mapped[list["UsersRoles"]] = relationship(
        "UsersRoles", back_populates="users"
    )

    def __str__(self):
        text = f"id: {self.id}, username: {self.username}"
        return text

    def __repr__(self):
        text = f"id: {self.id}, username: {self.username}"
        return text

    def model_dump(self):
        return {"id": self.id, "username": self.username, "password": self.password}


class Accounts(Base):
    __tablename__ = "accounts"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("pas_users.id", ondelete="CASCADE")
    )
    password: Mapped[str] = mapped_column(nullable=False)
    name: Mapped[str] = mapped_column(nullable=False)
    user: Mapped["Users"] = relationship("Users", back_populates="accounts")
    params: Mapped[list["Params"]] = relationship(
        "Params",
        back_populates="account",
        cascade="all, delete, delete-orphan",
        passive_deletes=True,
    )

    def __str__(self):
        text = f"id: {self.id}, {self.user_id}"
        return text

    def __repr__(self):
        text = f"id: {self.id}, {self.user_id}"
        return text

    def model_dump(self):
        return {"id": self.id, "user_id": self.user_id}


class Params(Base):
    __tablename__ = "params"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    acc_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("accounts.id", ondelete="CASCADE")
    )
    account: Mapped["Accounts"] = relationship("Accounts", back_populates="params")
    name: Mapped[str] = mapped_column(nullable=False)
    secret: Mapped[bool] = mapped_column(default=False)
    content: Mapped[str] = mapped_column(nullable=False)

    def __str__(self):
        text = f"id: {self.id}, name: {self.name}, content: {self.content}"
        return text

    def __repr__(self):
        text = f"id: {self.id}, name: {self.name}, content: {self.content}"
        return text

    def model_dump(self):
        return {
            "id": self.id,
            "acc_id": self.acc_id,
            "secret": self.secret,
            "name": self.name,
            "content": self.content,
        }


class Actions(Base):
    __tablename__ = "actions"
    action_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    action_name: Mapped[str] = mapped_column(nullable=False, unique=True)
    action_description: Mapped[str] = mapped_column(nullable=True)
    user_action: Mapped[list["UsersActions"]] = relationship(
        "UsersActions", back_populates="action"
    )
    action_to_roles: Mapped[list["RolesPermissions"]] = relationship(
        "RolesPermissions", back_populates="actions"
    )


class UsersActions(Base):
    __tablename__ = "users_actions"
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("pas_users.id"), primary_key=True
    )
    action_id: Mapped[int] = mapped_column(
        ForeignKey("actions.action_id"), primary_key=True
    )
    action: Mapped["Actions"] = relationship("Actions", back_populates="user_action")
    user: Mapped["Users"] = relationship("Users", back_populates="actions")


class Roles(Base):
    __tablename__ = "roles"
    role_id: Mapped[int] = mapped_column(primary_key=True)
    role_name: Mapped[str] = mapped_column(nullable=False, unique=True)
    role_permissions: Mapped[list["RolesPermissions"]] = relationship(
        "RolesPermissions", back_populates="roles"
    )
    users_roles: Mapped[list["UsersRoles"]] = relationship(
        "UsersRoles", back_populates="roles"
    )

    def model_dump(self):
        return {"role_id": self.role_id, "role_name": self.role_name}


class RolesPermissions(Base):
    __tablename__ = "roles_permissions"
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.role_id"), primary_key=True)
    action_id: Mapped[int] = mapped_column(
        ForeignKey("actions.action_id"), primary_key=True
    )
    roles: Mapped["Roles"] = relationship("Roles", back_populates="role_permissions")
    actions: Mapped["Actions"] = relationship(
        "Actions", back_populates="action_to_roles"
    )


class UsersRoles(Base):
    __tablename__ = "users_roles"
    user_id: Mapped[int] = mapped_column(ForeignKey("pas_users.id"), primary_key=True)
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.role_id"), primary_key=True)
    users: Mapped["Users"] = relationship("Users", back_populates="roles")
    roles: Mapped["Roles"] = relationship("Roles", back_populates="users_roles")

    def model_dump(self):
        return {"user_id": self.user_id, "role_id": self.role_id}


# class SharedAccounts(Base):
#     __tablename__ = "shared_accounts"
#     account_id: Mapped[int] = mapped_column(
#         BigInteger, ForeignKey("accounts.id"), primary_key=True
#     )
#     user_id: Mapped[int] = mapped_column(
#         BigInteger, ForeignKey("pas_users.id"), primary_key=True
#     )
#     owner_id: Mapped[int] = mapped_column(
#         BigInteger, ForeignKey("pas_users.id"), nullable=False
#     )
#     can_edit: Mapped[bool] = mapped_column(default=False)
#     owner: Mapped["Users"] = relationship(
#         "Users", back_populates="shared", foreign_keys=[owner_id]
#     )
#     account: Mapped["Accounts"] = relationship("Accounts", back_populates="shared")
#     user: Mapped["Users"] = relationship(
#         "Users", back_populates="grantee", foreign_keys=[user_id]
#     )
