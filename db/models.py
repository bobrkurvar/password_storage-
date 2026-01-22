from sqlalchemy import ForeignKey
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.types import BigInteger, String


class Base(AsyncAttrs, DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str] = mapped_column(String(256))
    salt: Mapped[str] = mapped_column(nullable=False)
    accounts: Mapped[list["Account"]] = relationship("Account", back_populates="user")
    # actions: Mapped[list["UsersActions"]] = relationship(
    #     "UsersActions", back_populates="user"
    # )
    roles: Mapped[list["UserRole"]] = relationship(
        "UserRole", back_populates="user"
    )

    def __repr__(self):
        text = f"id: {self.id}, username: {self.username}"
        return text

    def model_dump(self):
        return {
            "id": self.id,
            "username": self.username,
            "salt": self.salt,
            "password": self.password,
        }


class Account(Base):
    __tablename__ = "accounts"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    password: Mapped[str] = mapped_column(nullable=False)
    name: Mapped[str] = mapped_column(nullable=False)
    user: Mapped["User"] = relationship("User", back_populates="accounts")
    params: Mapped[list["Param"]] = relationship(
        "Param",
        back_populates="account",
        cascade="all, delete, delete-orphan",
        passive_deletes=True,
    )

    def __repr__(self):
        text = f"id: {self.id}, {self.user_id}"
        return text

    def model_dump(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "name": self.name,
            "password": self.password,
        }


class Param(Base):
    __tablename__ = "params"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    account_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("accounts.id", ondelete="CASCADE"), index=True
    )
    account: Mapped["Account"] = relationship("Account", back_populates="params")
    name: Mapped[str] = mapped_column(nullable=False)
    secret: Mapped[bool] = mapped_column(default=False)
    content: Mapped[str] = mapped_column(nullable=False)


    def __repr__(self):
        text = f"id: {self.id}, name: {self.name}, content: {self.content}"
        return text

    def model_dump(self):
        return {
            "id": self.id,
            "account_id": self.account_id,
            "secret": self.secret,
            "name": self.name,
            "content": self.content,
        }


# class Actions(Base):
#     __tablename__ = "actions"
#     action_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
#     action_name: Mapped[str] = mapped_column(nullable=False, unique=True)
#     action_description: Mapped[str] = mapped_column(nullable=True)
#     user_action: Mapped[list["UsersActions"]] = relationship(
#         "UsersActions", back_populates="action"
#     )
#     action_to_roles: Mapped[list["RolesPermissions"]] = relationship(
#         "RolesPermissions", back_populates="actions"
#     )

#
# class UsersActions(Base):
#     __tablename__ = "users_actions"
#     user_id: Mapped[int] = mapped_column(
#         BigInteger, ForeignKey("pas_users.id"), primary_key=True
#     )
#     action_id: Mapped[int] = mapped_column(
#         ForeignKey("actions.action_id"), primary_key=True
#     )
#     action: Mapped["Actions"] = relationship("Actions", back_populates="user_action")
#     user: Mapped["Users"] = relationship("Users", back_populates="actions")


class Role(Base):
    __tablename__ = "roles"
    role_name: Mapped[str] = mapped_column(primary_key=True)
    # role_permissions: Mapped[list["RolesPermissions"]] = relationship(
    #     "RolesPermissions", back_populates="roles"
    # )
    users: Mapped[list["UserRole"]] = relationship(
        "UserRole", back_populates="role"
    )

    def model_dump(self):
        return {"role_name": self.role_name}


# class RolesPermissions(Base):
#     __tablename__ = "roles_permissions"
#     role_id: Mapped[int] = mapped_column(ForeignKey("roles.role_id"), primary_key=True)
#     action_id: Mapped[int] = mapped_column(
#         ForeignKey("actions.action_id"), primary_key=True
#     )
#     roles: Mapped["Roles"] = relationship("Roles", back_populates="role_permissions")
#     actions: Mapped["Actions"] = relationship(
#         "Actions", back_populates="action_to_roles"
#     )


class UserRole(Base):
    __tablename__ = "users_roles"
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    role_name: Mapped[int] = mapped_column(ForeignKey("roles.role_name"), primary_key=True)
    user: Mapped["User"] = relationship("User", back_populates="roles")
    role: Mapped["Role"] = relationship("Role", back_populates="users")

    def model_dump(self):
        return {"user_id": self.user_id, "role_name": self.role_name}


class Admin(Base):
    __tablename__ = "admins"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)

    def model_dump(self):
        return {"id": self.id}

