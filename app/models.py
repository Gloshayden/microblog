from datetime import datetime, timezone  # Importing date and time handling utilities
from typing import Optional  # Importing type hint for optional values
from werkzeug.security import generate_password_hash, check_password_hash  # For password hashing
from flask_login import UserMixin  # type: ignore (Adding user session management for Flask)
import sqlalchemy as sa  # type: ignore (Importing SQLAlchemy library for database ORM)
import sqlalchemy.orm as so  # type: ignore (Importing ORM tools from SQLAlchemy)
from app import db, login, app  # Importing app's database instance and login manager
from hashlib import md5  # For generating unique user avatars
from time import time
import jwt

# Creates a followers table with two coloums which are both primary keys to create a compound key
followers = sa.Table(
    'followers',
    db.metadata,
    sa.Column('follower_id', sa.Integer, sa.ForeignKey('user.id'),
              primary_key=True),
    sa.Column('followed_id', sa.Integer, sa.ForeignKey('user.id'),
              primary_key=True)
)

# Define the User class with database columns and methods for user management
class User(UserMixin, db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)  # Unique user ID
    username: so.Mapped[str] = so.mapped_column(sa.String(64), index=True, unique=True)  # Username, must be unique
    email: so.Mapped[str] = so.mapped_column(sa.String(120), index=True, unique=True)  # User email, also unique
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))  # Stores hashed password

    # Relationship to link user to posts, allows accessing posts authored by the user
    posts: so.WriteOnlyMapped['Post'] = so.relationship(
        back_populates='author')
    
    about_me: so.Mapped[Optional[str]] = so.mapped_column(sa.String(140))  # Short bio about the user
    last_seen: so.Mapped[Optional[datetime]] = so.mapped_column(
        default=lambda: datetime.now(timezone.utc))  # Last login time
    
    # Creates relationship links between user table and followers table
    following: so.WriteOnlyMapped['User'] = so.relationship(
        secondary=followers, primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        back_populates='followers')
    followers: so.WriteOnlyMapped['User'] = so.relationship(
        secondary=followers, primaryjoin=(followers.c.followed_id == id),
        secondaryjoin=(followers.c.follower_id == id),
        back_populates='following')

    # Sets hashed password for the user
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    # Checks if the password matches the hashed password
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    # Defines how user object is represented, helpful for debugging
    def __repr__(self):
        return '<User {}>'.format(self.username)
    
    # Generates a URL for the user's avatar based on email hash
    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return f'https://www.gravatar.com/avatar/{digest}?d=identicon&s={size}'
    
    # Defines follow and if they are not already following it then follows them
    def follow(self, user):
        if not self.is_following(user):
            self.following.add(user)

    # Defines unfollow and if they are following it unfolows them
    def unfollow(self, user):
        if self.is_following(user):
            self.following.remove(user)

    # Script to check if the curent user is folowing the target user 
    def is_following(self, user):
        query = self.following.select().where(User.id == user.id)
        return db.session.scalar(query) is not None
    
    # Script to show folowers
    def followers_count(self):
        query = sa.select(sa.func.count()).select_from(self.followers.select().subquery())
        return db.session.scalar(query)
    
    # Script to show folowing people
    def following_count(self):
        query = sa.select(sa.func.count()).select_from(self.following.select().subquery())
        return db.session.scalar(query)
    
    # Defines folowing posts so you can get updated on that post
    def following_posts(self):
        Author = so.aliased(User)
        Follower = so.aliased(User)
        return (
            sa.select(Post)
            .join(Post.author.of_type(Author))
            .join(Author.followers.of_type(Follower), isouter=True)
            .where(sa.or_(
                Follower.id == self.id,
                Author.id == self.id,
            ))
            .group_by(Post)
            .order_by(Post.timestamp.desc())
        )
    def get_reset_password_token(self, expires_in=600):
        return jwt.encode({'reset_password': self.id, 'exp': time() + expires_in}, app.config['SECRET_KEY'], algorithm='HS256')
    
    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])['reset_password']
        except:
            return
        return db.session.get(User, id)
    
# Define the Post class to represent blog posts linked to users
class Post(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)  # Unique post ID
    body: so.Mapped[str] = so.mapped_column(sa.String(140))  # Post content
    timestamp: so.Mapped[datetime] = so.mapped_column(
        index=True, default=lambda: datetime.now(timezone.utc))  # Time of post creation
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(User.id),
                                               index=True)  # Foreign key linking post to user

    # Relationship linking post to its author (user)
    author: so.Mapped[User] = so.relationship(back_populates='posts')

    # Adds the messages language into the database
    language: so.Mapped[Optional[str]] = so.mapped_column(sa.String(5))

    # Defines how post object is represented, helpful for debugging
    def __repr__(self):
        return '<Post {}>'.format(self.body)

# User loader function required by Flask-Login to manage user sessions
@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))