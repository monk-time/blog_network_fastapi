from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.sql import expression, func


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'user'
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(30), unique=True)
    email: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]
    is_active: Mapped[bool] = mapped_column(server_default=expression.true())

    posts: Mapped[list['Post']] = relationship(back_populates='author')
    comments: Mapped[list['Comment']] = relationship(back_populates='author')
    follower: Mapped[list['Follow']] = relationship(
        foreign_keys='Follow.user_id', back_populates='user'
    )
    following: Mapped[list['Follow']] = relationship(
        foreign_keys='Follow.following_id', back_populates='following'
    )

    def __repr__(self) -> str:
        return (
            f'User(id={self.id!r}, username={self.username!r}, '
            f'email={self.email!r})'
        )


class Group(Base):
    __tablename__ = 'group'
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    slug: Mapped[str] = mapped_column(String(50), unique=True)
    description: Mapped[str]

    posts: Mapped[list['Post']] = relationship(back_populates='group')

    def __repr__(self) -> str:
        return (
            f'Group(id={self.id!r}, title={self.title!r}, '
            f'slug={self.slug!r}, description={self.description!r})'
        )


class Post(Base):
    __tablename__ = 'post'
    id: Mapped[int] = mapped_column(primary_key=True)
    text: Mapped[str]
    pub_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    author_id: Mapped[int] = mapped_column(
        ForeignKey('user.id', ondelete='CASCADE')
    )
    group_id: Mapped[int | None] = mapped_column(
        ForeignKey('group.id', ondelete='SET NULL')
    )
    image: Mapped[str | None] = mapped_column(String(100))

    author: Mapped['User'] = relationship(back_populates='posts')
    group: Mapped['Group'] = relationship(back_populates='posts')
    comments: Mapped[list['Comment']] = relationship(back_populates='post')

    def __repr__(self) -> str:
        return (
            f'Post(id={self.id!r}, text={self.text!r}, '
            f'pub_date={self.pub_date!r}, author_id={self.author_id!r}, '
            f'group_id={self.group_id!r}, image={self.image!r})'
        )


class Comment(Base):
    __tablename__ = 'comment'
    id: Mapped[int] = mapped_column(primary_key=True)
    author_id: Mapped[int] = mapped_column(
        ForeignKey('user.id', ondelete='CASCADE')
    )
    post_id: Mapped[int] = mapped_column(
        ForeignKey('post.id', ondelete='CASCADE')
    )
    text: Mapped[str]
    created: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    author: Mapped['User'] = relationship(back_populates='comments')
    post: Mapped['Post'] = relationship(back_populates='comments')

    def __repr__(self) -> str:
        return (
            f'Comment(id={self.id!r}, author_id={self.author_id!r}, '
            f'post_id={self.post_id!r}, text={self.text!r}, '
            f'created={self.created!r})'
        )


class Follow(Base):
    __tablename__ = 'follow'
    user_id: Mapped[int] = mapped_column(
        ForeignKey('user.id', ondelete='CASCADE'),
        primary_key=True,
    )
    following_id: Mapped[int] = mapped_column(
        ForeignKey('user.id', ondelete='CASCADE'),
        primary_key=True,
    )

    user: Mapped['User'] = relationship(
        foreign_keys=[user_id],
        back_populates='follower',
    )
    following: Mapped['User'] = relationship(
        foreign_keys=[following_id],
        back_populates='following',
    )

    def __repr__(self) -> str:
        return (
            f'Follow(user_id={self.user_id!r}, '
            f'following_id={self.following_id!r})'
        )
