import hashlib
import math
import secrets
from datetime import datetime, timedelta
from typing import List, Optional
from enum import Enum

from pydantic import EmailStr
from sqlalchemy.exc import IntegrityError
from sqlmodel import Field, Relationship, Session, SQLModel, create_engine, select

from broker import UserError
from env import EnvConfig
from email_facade import EmailFacade

# TABLE MODELS


class WatchPartyLink(SQLModel, table=True):
    party_id: Optional[int] = Field(
        default=None, primary_key=True, foreign_key="watchparty.id"
    )
    user_id: Optional[int] = Field(
        default=None, primary_key=True, foreign_key="user.id"
    )


class Movie(SQLModel, table=True):
    id: str = Field(primary_key=True)
    title: str = Field(index=False)
    description: str = Field(max_length=5000, index=False)
    year: int = Field(index=False)
    poster_url: str = Field(max_length=1000, index=False)
    runtime: int = Field(index=False)

    youtube_id: Optional[str] = Field(default=None, index=False)

    ratings: List["MovieRating"] = Relationship(back_populates="movie")
    watch_parties: List["WatchParty"] = Relationship(back_populates="movie")


class MovieRating(SQLModel, table=True):
    movie_id: Optional[str] = Field(
        default=None, foreign_key="movie.id", primary_key=True
    )
    user_id: Optional[int] = Field(
        default=None, foreign_key="user.id", primary_key=True
    )
    movie: Optional[Movie] = Relationship(back_populates="ratings")
    user: Optional["User"] = Relationship(back_populates="movie_ratings")
    stars: int = Field(ge=1, le=5, index=False)
    comment: str = Field(default="", max_length=350, index=False)


class FriendRequest(SQLModel, table=True):
    sender_id: Optional[int] = Field(
        default=None, primary_key=True, foreign_key="user.id"
    )
    recipient_id: Optional[int] = Field(
        default=None, primary_key=True, foreign_key="user.id"
    )


class FriendLink(SQLModel, table=True):
    user_id: Optional[int] = Field(
        default=None, primary_key=True, foreign_key="user.id"
    )
    friend_id: Optional[int] = Field(
        default=None, primary_key=True, foreign_key="user.id"
    )


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, sa_column_kwargs={"unique": True})
    display_name: str = Field(index=False)
    bio: str = Field(default="", index=False)

    movie_ratings: List[MovieRating] = Relationship(back_populates="user")
    friends: List["User"] = Relationship(
        link_model=FriendLink,
        sa_relationship_kwargs={
            "primaryjoin": "User.id==FriendLink.user_id",
            "secondaryjoin": "User.id==FriendLink.friend_id",
        },
    )
    friend_requests: List["User"] = Relationship(
        link_model=FriendRequest,
        sa_relationship_kwargs={
            "primaryjoin": "User.id==FriendRequest.recipient_id",
            "secondaryjoin": "User.id==FriendRequest.sender_id",
        },
    )
    watch_parties: List["WatchParty"] = Relationship(
        link_model=WatchPartyLink,
        sa_relationship_kwargs={
            "primaryjoin": "User.id==WatchPartyLink.user_id",
            "secondaryjoin": "WatchParty.id==WatchPartyLink.party_id",
        },
    )

    email: EmailStr = Field(sa_column_kwargs={"unique": True})
    password_hash: bytes = Field(index=False)
    password_salt: bytes = Field(index=False)
    tokens: List["AuthToken"] = Relationship(back_populates="user")

    def check_password(self, password: str):
        test_hash = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), self.password_salt, 100000
        )
        return test_hash == self.password_hash


def token_exp_factory():
    return datetime.utcnow() + timedelta(hours=12)


class AuthToken(SQLModel, table=True):
    token: str = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=False)
    user: User = Relationship(back_populates="tokens")
    expiration_date: datetime = Field(default_factory=token_exp_factory, index=False)


class WatchPartyStatus(str, Enum):
    PLAYING = "playing"
    PAUSED = "paused"


class WatchParty(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    movie_id: str = Field(foreign_key="movie.id", index=False)
    youtube_id: str
    movie_length: int = Field(index=False)

    status: WatchPartyStatus = Field(default=WatchPartyStatus.PAUSED, index=False)
    last_play: datetime = Field(default_factory=datetime.utcnow)
    pause_time: int = Field(default=0, ge=0, le=45000, index=False)

    movie: Optional[Movie] = Relationship(back_populates="watch_parties")
    participants: List[User] = Relationship(
        link_model=WatchPartyLink,
        sa_relationship_kwargs={
            "primaryjoin": "WatchParty.id==WatchPartyLink.party_id",
            "secondaryjoin": "User.id==WatchPartyLink.user_id",
        },
    )

    def get_current_time(self):
        if self.status == WatchPartyStatus.PAUSED:
            return self.pause_time
        time_passed = datetime.utcnow() - self.last_play
        seconds_passed = self.pause_time + math.trunc(time_passed.total_seconds())
        return seconds_passed if seconds_passed < self.movie_length else 0


# FACADE CLASS


class DatabaseFacade:
    def __init__(self, cfg: EnvConfig) -> None:
        self._engine = create_engine(
            f"mysql+pymysql://{cfg.mysql_user}:{cfg.mysql_password}@{cfg.mysql_host}:{cfg.mysql_port}/appdb",
            echo=False,
        )
        SQLModel.metadata.create_all(self._engine)

    def generate_token(self, username: str, password: str):
        with Session(self._engine) as session:
            statement = select(User).where(User.username == username)
            results = session.exec(statement)
            target_user = results.first()
            if target_user is None:
                raise UserError("Username does not exist")
            if target_user.check_password(password) is False:
                raise UserError("Incorrect password")
            token_str = secrets.token_urlsafe(32)
            if not isinstance(target_user.id, int):
                raise RuntimeError("User was never assigned ID")
            new_token = AuthToken(token=token_str, user_id=target_user.id)
            session.add(new_token)
            session.commit()
        return token_str

    def get_token_user(self, token_str: str):
        with Session(self._engine) as session:
            statement = select(AuthToken).where(AuthToken.token == token_str)
            token = session.exec(statement).first()
            if token is None:
                raise UserError("Invalid token")
            if datetime.utcnow() > token.expiration_date:
                session.delete(token)
                session.commit()
                raise UserError("Invalid token")
            return token.user

    def delete_token(self, token_str: str):
        with Session(self._engine) as session:
            statement = select(AuthToken).where(AuthToken.token == token_str)
            token = session.exec(statement).first()
            if token is None:
                return
            session.delete(token)
            session.commit()

    def create_user(
        self, email: EmailStr, username: str, display_name: str, password: str
    ):
        pass_salt = secrets.token_bytes(32)
        pass_hash = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), pass_salt, 100000
        )
        new_user = User(
            username=username,
            email=email,
            display_name=display_name,
            password_hash=pass_hash,
            password_salt=pass_salt,
        )
        with Session(self._engine) as session:
            session.add(new_user)
            try:
                session.commit()
            except IntegrityError as err:
                if err.orig.args[0] == 1062:
                    raise UserError("Username or email already in use")

    def get_user(self, username: str):
        with Session(self._engine) as session:
            statement = select(User).where(User.username == username)
            user = session.exec(statement).first()
            if user is None:
                raise UserError(f"Username {username} does not exist")
            return user

    def update_user(self, user: User):
        with Session(self._engine) as session:
            session.add(user)
            session.commit()
            session.refresh(user)

    def get_user_ratings(self, user: User):
        with Session(self._engine) as session:
            session.add(user)
            ratings = []
            for rating in user.movie_ratings:
                rating_expanded = rating.dict()
                if rating.movie is not None:
                    rating_expanded["movie"] = rating.movie.dict()
                ratings.append(rating_expanded)
            return ratings

    def get_user_friends(self, user: User):
        with Session(self._engine) as session:
            session.add(user)
            return [
                friend.dict(include={"username": ..., "display_name": ...})
                for friend in user.friends
            ]

    def get_user_friend_requests(self, user: User):
        with Session(self._engine) as session:
            session.add(user)
            return [
                friend.dict(include={"username": ..., "display_name": ...})
                for friend in user.friend_requests
            ]

    def get_user_watch_parties(self, user: User):
        with Session(self._engine) as session:
            session.add(user)
            return [self._dict_watch_party(wp) for wp in user.watch_parties]

    def send_friend_request(self, sender: User, recipient: User):
        with Session(self._engine) as session:
            session.add(sender)
            for friend in sender.friends:
                if friend.id == recipient.id:
                    raise UserError("You are already friends with this user")
            friend_request = FriendRequest(
                sender_id=sender.id, recipient_id=recipient.id
            )
            session.add(friend_request)
            try:
                session.commit()
            except IntegrityError as err:
                if err.orig.args[0] == 1062:
                    raise UserError("Friend request already sent")

    def _modify_friend_request(self, sender: User, recipient: User, accept: bool):
        with Session(self._engine) as session:
            session.add_all((sender, recipient))
            statement = select(FriendRequest).where(
                FriendRequest.sender_id == sender.id
                and FriendRequest.recipient_id == recipient.id
            )
            friend_request = session.exec(statement).first()
            if friend_request is None:
                raise UserError("Friend request does not exist")
            if accept:
                sender.friends.append(recipient)
                recipient.friends.append(sender)
            session.delete(friend_request)
            session.commit()
            session.refresh(recipient)
            session.refresh(sender)

    def accept_friend_request(self, sender: User, recipient: User):
        self._modify_friend_request(sender, recipient, True)

    def decline_friend_request(self, sender: User, recipient: User):
        self._modify_friend_request(sender, recipient, False)

    def submit_movie_review(self, movie: Movie, user: User, stars: int, comment: str):
        with Session(self._engine) as session:
            new_rating = MovieRating(
                movie_id=movie.id, user_id=user.id, stars=stars, comment=comment
            )
            session.add(new_rating)
            try:
                session.commit()
            except IntegrityError as err:
                if err.orig.args[0] == 1062:
                    pass
            session.refresh(movie)
            session.refresh(user)

    def add_movie(self, **kwargs):
        with Session(self._engine) as session:
            new_movie = Movie(**kwargs)
            session.add(new_movie)
            try:
                session.commit()
            except IntegrityError as err:
                if err.orig.args[0] == 1062:
                    raise RuntimeError("Movie already added")

    def get_movie_ratings(self, movie: Movie):
        with Session(self._engine) as session:
            session.add(movie)
            ratings: list[dict] = []
            for rating in movie.ratings:
                rd = rating.dict()
                if rating.user is not None:
                    rd["user"] = rating.user.dict(
                        include={"username": ..., "display_name": ...}
                    )
                ratings.append(rd)
            return ratings

    def get_movie(self, movie_id: str):
        with Session(self._engine) as session:
            statement = select(Movie).where(Movie.id == movie_id)
            movie = session.exec(statement).first()
            if movie is None:
                raise UserError("Movie must be added to database")
            return movie

    def get_watch_party(self, user: User, watch_party_id: int):
        with Session(self._engine) as session:
            session.add(user)
            for wp in user.watch_parties:
                if wp.id == watch_party_id:
                    return wp
            raise UserError("Watch party does not exist")

    def send_watch_party_emails(self, watch_party: WatchParty, email: EmailFacade):
        with Session(self._engine) as session:
            session.add(watch_party)
            if watch_party.movie is None:
                raise RuntimeError("Watch parties must have a movie")
            emails = [str(user.email) for user in watch_party.participants]
            email.send(
                emails,
                f"Watch Party Invite: {watch_party.movie.title}",
                "\n".join(
                    [
                        "Hello there!",
                        "",
                        f"You've been invited to watch {watch_party.movie.title}!",
                        "",
                        "Description:",
                        watch_party.movie.description,
                    ]
                ),
            )

    def get_watch_party_data(self, watch_party: WatchParty):
        with Session(self._engine) as session:
            session.add(watch_party)
            return self._dict_watch_party(watch_party)

    def schedule_watch_party(
        self,
        movie: Movie,
        youtube_id: str,
        participants: list[User],
    ):
        with Session(self._engine) as session:
            new_wp = WatchParty(
                movie_id=movie.id, movie_length=movie.runtime, youtube_id=youtube_id
            )
            session.add(new_wp)
            for participant in participants:
                new_wp.participants.append(participant)
            session.commit()
            if movie.youtube_id is None:
                session.add(movie)
                movie.youtube_id = youtube_id
                session.commit()
            session.refresh(new_wp)
            return new_wp

    def pause_watch_party(self, watch_party: WatchParty):
        with Session(self._engine) as session:
            session.add(watch_party)
            session.refresh(watch_party)
            if watch_party.status == WatchPartyStatus.PAUSED:
                raise UserError("Movie is already paused")
            watch_party.status = WatchPartyStatus.PAUSED
            watch_party.pause_time = watch_party.get_current_time()
            session.commit()

    def play_watch_party(self, watch_party: WatchParty):
        with Session(self._engine) as session:
            session.add(watch_party)
            session.refresh(watch_party)
            if watch_party.status == WatchPartyStatus.PLAYING:
                raise UserError("Movie is already playing")
            watch_party.status = WatchPartyStatus.PLAYING
            watch_party.last_play = datetime.utcnow()
            session.commit()

    def leave_watch_party(self, watch_party: WatchParty, user: User):
        with Session(self._engine) as session:
            session.add(watch_party)
            watch_party.participants.remove(user)
            session.commit()
            session.refresh(watch_party)
            if len(watch_party.participants) == 0:
                session.delete(watch_party)
                session.commit()

    def _dict_watch_party(self, watch_party: WatchParty):
        data = watch_party.dict(
            exclude={"movie_id": ..., "pause_time": ..., "last_play": ...}
        )
        if watch_party.movie is not None:
            data["movie"] = watch_party.movie.dict()
        data["participants"] = [
            {
                "username": participant.username,
                "display_name": participant.display_name,
            }
            for participant in watch_party.participants
            if participant is not None
        ]
        data["current_time"] = watch_party.get_current_time()
        return data
