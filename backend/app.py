import warnings

from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.exc import SAWarning
from backend.broker import UserError

from broker import run_rabbit_app
from db import DatabaseFacade
from email_facade import EmailFacade
from env import EnvConfig

db: DatabaseFacade
email: EmailFacade

# constants

USERNAME_FIELD = Field(regex=r"^[\w\-]{3,}$")
DISPLAY_NAME_FIELD = Field(regex=r"^[\w\-' ]{3,}$")
BIO_FIELD = Field(max_length=500)
PASSWORD_REGEX = Field(regex=r"^[\w\-&^/\\$#@!%*().,\"';:[\]{}]{5,30}$")


# shared models


class TokenRequest(BaseModel):
    token: str


# token.create


class TokenGenRequest(BaseModel):
    username: str = USERNAME_FIELD
    password: str = PASSWORD_REGEX


def handle_token_gen(req_body: dict):
    rq = TokenGenRequest(**req_body)
    token = db.generate_token(rq.username, rq.password)
    return {"token": token}


# token.get-user


def handle_token_get_user(req_body: dict):
    rq = TokenRequest(**req_body)
    user = db.get_token_user(rq.token)
    return user.dict(include={"username": ..., "display_name": ...})


# token.delete


def handle_token_delete(req_body: dict):
    rq = TokenRequest(**req_body)
    db.delete_token(rq.token)


# user.create


class UserCreateRequest(BaseModel):
    username: str = USERNAME_FIELD
    display_name: str = DISPLAY_NAME_FIELD
    email: EmailStr
    password: str = PASSWORD_REGEX


def handle_user_create(req_body: dict):
    rq = UserCreateRequest(**req_body)
    db.create_user(rq.email, rq.username, rq.display_name, rq.password)
    token = db.generate_token(rq.username, rq.password)
    return {"token": token}


# user.get


class UserGetPublicRequest(BaseModel):
    username: str = USERNAME_FIELD


def handle_user_get_public(req_body: dict):
    rq = UserGetPublicRequest(**req_body)
    user = db.get_user(rq.username)
    reply = user.dict(include={"username": ..., "display_name": ..., "bio": ...})
    reply["movie_ratings"] = db.get_user_ratings(user)
    reply["friends"] = db.get_user_friends(user)
    return reply


def handle_user_get_private(req_body: dict):
    rq = TokenRequest(**req_body)
    user = db.get_token_user(rq.token)
    reply = user.dict(exclude={"password_hash": ..., "password_salt": ...})
    reply["movie_ratings"] = db.get_user_ratings(user)
    reply["friends"] = db.get_user_friends(user)
    reply["friend_requests"] = db.get_user_friend_requests(user)
    reply["watch_parties"] = db.get_user_watch_parties(user)
    return reply


# user.update


class UserUpdateRequest(BaseModel):
    token: str
    display_name: str = DISPLAY_NAME_FIELD
    bio: str = BIO_FIELD


def handle_user_update(req_body: dict):
    rq = UserUpdateRequest(**req_body)
    user = db.get_token_user(rq.token)
    user.display_name = rq.display_name
    user.bio = rq.bio
    db.update_user(user)


# friend routes


class SendFriendRequest(BaseModel):
    token: str
    recipient_username: str


def handle_friend_request_send(req_body: dict):
    rq = SendFriendRequest(**req_body)
    sender = db.get_token_user(rq.token)
    recipient = db.get_user(rq.recipient_username)
    db.send_friend_request(sender, recipient)


class ModifyFriendRequest(BaseModel):
    token: str
    sender_username: str


def handle_friend_request_accept(req_body: dict):
    rq = ModifyFriendRequest(**req_body)
    recipient = db.get_token_user(rq.token)
    sender = db.get_user(rq.sender_username)
    db.accept_friend_request(sender, recipient)


def handle_friend_request_decline(req_body: dict):
    rq = ModifyFriendRequest(**req_body)
    recipient = db.get_token_user(rq.token)
    sender = db.get_user(rq.sender_username)
    db.accept_friend_request(sender, recipient)


# review routes


class ReviewSubmitRequest(BaseModel):
    token: str
    movie_id: str
    stars: int = Field(ge=1, le=5)
    comment: str = Field(default="", max_length=350)


def handle_review_submit(req_body: dict):
    rq = ReviewSubmitRequest(**req_body)
    user = db.get_token_user(rq.token)
    movie = db.get_movie(rq.movie_id)
    db.submit_movie_review(movie, user, rq.stars, rq.comment)


# movie routes


class MovieAddRequest(BaseModel):
    id: str
    title: str
    description: str = Field(max_length=5000)
    # genre_ids: list[int]
    year: int
    poster_url: str = Field(max_length=1000)


def handle_movie_add(req_body: dict):
    rq = MovieAddRequest(**req_body)
    db.add_movie(**rq.dict())


class MovieGetRequest(BaseModel):
    movie_id: str


def handle_movie_get(req_body: dict):
    rq = MovieGetRequest(**req_body)
    movie = db.get_movie(rq.movie_id)
    movie_dict = movie.dict()
    movie_dict["ratings"] = db.get_movie_ratings(movie)
    return movie_dict


# watch-party


class WatchPartyGetReq(BaseModel):
    token: str
    watch_party_id: int


def handle_watch_party_get(req_body: dict):
    req = WatchPartyGetReq(**req_body)
    user = db.get_token_user(req.token)
    watch_party = db.get_watch_party(user, req.watch_party_id)
    return db.get_watch_party_data(watch_party)


class WatchPartyScheduleReq(BaseModel):
    token: str
    movie_id: str
    movie_length: int
    youtube_id: str
    participants: list[str]


def handle_watch_party_schedule(req_body: dict):
    req = WatchPartyScheduleReq(**req_body)
    scheduler = db.get_token_user(req.token)
    friend_usernames: list[str] = [
        friend["username"] for friend in db.get_user_friends(scheduler)
    ]
    for username in req.participants:
        if username not in friend_usernames:
            raise UserError(f"User not in friends list: {username}")
    full_participants = set(req.participants + [scheduler.username])
    movie = db.get_movie(req.movie_id)
    watch_party = db.schedule_watch_party(
        movie=movie,
        youtube_id=req.youtube_id,
        movie_length=req.movie_length,
        participants=[db.get_user(username) for username in full_participants],
    )
    return db.get_watch_party_data(watch_party)


class WatchPartyLeaveReq(BaseModel):
    token: str
    watch_party_id: int


def handle_watch_party_leave(req_body: dict):
    req = WatchPartyLeaveReq(**req_body)
    user = db.get_token_user(req.token)
    watch_party = db.get_watch_party(user, req.watch_party_id)
    db.leave_watch_party(watch_party, user)


class WatchPartyPlayPauseReq(BaseModel):
    token: str
    watch_party_id: int


def handle_watch_party_play(req_body: dict):
    req = WatchPartyPlayPauseReq(**req_body)
    user = db.get_token_user(req.token)
    watch_party = db.get_watch_party(user, req.watch_party_id)
    db.play_watch_party(watch_party)


def handle_watch_party_pause(req_body: dict):
    req = WatchPartyPlayPauseReq(**req_body)
    user = db.get_token_user(req.token)
    watch_party = db.get_watch_party(user, req.watch_party_id)
    db.pause_watch_party(watch_party)


# run app


def main():
    warnings.simplefilter("ignore", category=SAWarning)

    route_handlers = {
        "db.token.generate": handle_token_gen,
        "db.token.get-user": handle_token_get_user,
        "db.token.delete": handle_token_delete,
        "db.user.create": handle_user_create,
        "db.user.get.public": handle_user_get_public,
        "db.user.get.private": handle_user_get_private,
        "db.user.update": handle_user_update,
        "db.friend-request.send": handle_friend_request_send,
        "db.friend-request.accept": handle_friend_request_accept,
        "db.friend-request.decline": handle_friend_request_decline,
        "db.review.submit": handle_review_submit,
        "db.movie.add": handle_movie_add,
        "db.movie.get": handle_movie_get,
        "db.watch-party.get": handle_watch_party_get,
        "db.watch-party.schedule": handle_watch_party_schedule,
        "db.watch-party.leave": handle_watch_party_leave,
        "db.watch-party.play": handle_watch_party_play,
        "db.watch-party.pause": handle_watch_party_pause,
    }

    cfg = EnvConfig()

    global db
    db = DatabaseFacade(cfg)

    global email
    email = EmailFacade(cfg.email_addr)

    run_rabbit_app(
        "backend-db",
        cfg.broker_host,
        cfg.broker_port,
        cfg.broker_user,
        cfg.broker_password,
        route_handlers,
    )


if __name__ == "__main__":
    main()
