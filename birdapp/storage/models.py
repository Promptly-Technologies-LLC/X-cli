from typing import Any, Optional

from sqlalchemy import Column, Index, JSON, UniqueConstraint
from sqlmodel import Field, Relationship, SQLModel


class UploadOptions(SQLModel, table=True):
    __tablename__ = "upload_options"
    __table_args__ = (UniqueConstraint("account_id", name="uq_upload_options_account_id"),)

    id: Optional[int] = Field(default=None, primary_key=True)
    account_id: str = Field(foreign_key="account.account_id", index=True)
    keep_private: bool
    upload_likes: bool
    start_date: str
    end_date: str


class Account(SQLModel, table=True):
    __tablename__ = "account"

    account_id: str = Field(primary_key=True, index=True)
    username: str
    account_display_name: str
    created_at: str
    created_via: str

    profile: Optional["Profile"] = Relationship(back_populates="account")


class Profile(SQLModel, table=True):
    __tablename__ = "profile"

    account_id: str = Field(primary_key=True, foreign_key="account.account_id")
    bio: str
    website: str
    location: str
    avatar_media_url: str
    header_media_url: str

    account: Optional[Account] = Relationship(back_populates="profile")


class Tweet(SQLModel, table=True):
    __tablename__ = "tweet"
    __table_args__ = (
        Index("ix_tweet_account_id_created_at", "account_id", "created_at"),
    )

    tweet_id: str = Field(primary_key=True, index=True)
    account_id: str = Field(foreign_key="account.account_id", index=True)
    tweet_id_str: Optional[str] = Field(default=None, index=True)
    tweet_kind: str = Field(default="tweet", index=True)
    created_at: str
    full_text: str
    lang: str
    source: str
    retweeted: bool
    favorited: bool
    truncated: bool
    favorite_count: Optional[int] = None
    retweet_count: Optional[int] = None
    display_text_range: Optional[list[int]] = Field(
        default=None, sa_column=Column(JSON)
    )
    in_reply_to_status_id: Optional[str] = None
    in_reply_to_status_id_str: Optional[str] = None
    in_reply_to_user_id: Optional[str] = None
    in_reply_to_user_id_str: Optional[str] = None
    in_reply_to_screen_name: Optional[str] = None
    possibly_sensitive: Optional[bool] = None
    edit_info: Optional[dict[str, Any]] = Field(
        default=None, sa_column=Column(JSON)
    )
    community_id: Optional[str] = None
    community_id_str: Optional[str] = None
    scopes: Optional[dict[str, Any]] = Field(default=None, sa_column=Column(JSON))

    hashtags: list["TweetHashtag"] = Relationship(back_populates="tweet")
    symbols: list["TweetSymbol"] = Relationship(back_populates="tweet")
    user_mentions: list["TweetUserMention"] = Relationship(back_populates="tweet")
    urls: list["TweetUrl"] = Relationship(back_populates="tweet")
    media: list["TweetMedia"] = Relationship(back_populates="tweet")


class TweetHashtag(SQLModel, table=True):
    __tablename__ = "tweet_hashtag"

    id: Optional[int] = Field(default=None, primary_key=True)
    tweet_id: str = Field(foreign_key="tweet.tweet_id", index=True)
    text: str
    start_index: Optional[int] = None
    end_index: Optional[int] = None

    tweet: Optional[Tweet] = Relationship(back_populates="hashtags")


class TweetSymbol(SQLModel, table=True):
    __tablename__ = "tweet_symbol"

    id: Optional[int] = Field(default=None, primary_key=True)
    tweet_id: str = Field(foreign_key="tweet.tweet_id", index=True)
    text: str
    start_index: Optional[int] = None
    end_index: Optional[int] = None

    tweet: Optional[Tweet] = Relationship(back_populates="symbols")


class TweetUserMention(SQLModel, table=True):
    __tablename__ = "tweet_user_mention"

    id: Optional[int] = Field(default=None, primary_key=True)
    tweet_id: str = Field(foreign_key="tweet.tweet_id", index=True)
    user_id: Optional[str] = Field(default=None, index=True)
    user_id_str: Optional[str] = Field(default=None, index=True)
    name: str
    screen_name: str
    start_index: Optional[int] = None
    end_index: Optional[int] = None

    tweet: Optional[Tweet] = Relationship(back_populates="user_mentions")


class TweetUrl(SQLModel, table=True):
    __tablename__ = "tweet_url"

    id: Optional[int] = Field(default=None, primary_key=True)
    tweet_id: str = Field(foreign_key="tweet.tweet_id", index=True)
    url: str
    expanded_url: str
    display_url: str
    start_index: Optional[int] = None
    end_index: Optional[int] = None

    tweet: Optional[Tweet] = Relationship(back_populates="urls")


class TweetMedia(SQLModel, table=True):
    __tablename__ = "tweet_media"

    id: Optional[int] = Field(default=None, primary_key=True)
    tweet_id: str = Field(foreign_key="tweet.tweet_id", index=True)
    entity_type: str = Field(default="entities", index=True)
    media_id: Optional[str] = Field(default=None, index=True)
    media_id_str: Optional[str] = Field(default=None, index=True)
    media_type: str
    url: str
    expanded_url: str
    display_url: str
    media_url: str
    media_url_https: str
    sizes: Optional[dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
    video_info: Optional[dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
    additional_media_info: Optional[dict[str, Any]] = Field(
        default=None, sa_column=Column(JSON)
    )
    source_status_id: Optional[str] = None
    source_status_id_str: Optional[str] = None
    source_user_id: Optional[str] = None
    source_user_id_str: Optional[str] = None

    tweet: Optional[Tweet] = Relationship(back_populates="media")


class NoteTweet(SQLModel, table=True):
    __tablename__ = "note_tweet"

    note_tweet_id: str = Field(primary_key=True, index=True)
    account_id: str = Field(foreign_key="account.account_id", index=True)
    created_at: str
    updated_at: str
    lifecycle: dict[str, Any] = Field(sa_column=Column(JSON))
    core: dict[str, Any] = Field(sa_column=Column(JSON))


class Like(SQLModel, table=True):
    __tablename__ = "like"
    __table_args__ = (
        UniqueConstraint("account_id", "tweet_id", name="uq_like_account_id_tweet_id"),
        Index("ix_like_account_id_tweet_id", "account_id", "tweet_id"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    account_id: str = Field(foreign_key="account.account_id", index=True)
    tweet_id: str = Field(index=True)
    full_text: Optional[str] = None
    expanded_url: Optional[str] = None


class Follower(SQLModel, table=True):
    __tablename__ = "follower"
    __table_args__ = (
        UniqueConstraint(
            "account_id",
            "follower_account_id",
            name="uq_follower_account_id_follower_account_id",
        ),
        Index(
            "ix_follower_account_id_follower_account_id",
            "account_id",
            "follower_account_id",
        ),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    account_id: str = Field(foreign_key="account.account_id", index=True)
    follower_account_id: str = Field(index=True)
    user_link: str


class Following(SQLModel, table=True):
    __tablename__ = "following"
    __table_args__ = (
        UniqueConstraint(
            "account_id",
            "followed_account_id",
            name="uq_following_account_id_followed_account_id",
        ),
        Index(
            "ix_following_account_id_followed_account_id",
            "account_id",
            "followed_account_id",
        ),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    account_id: str = Field(foreign_key="account.account_id", index=True)
    followed_account_id: str = Field(index=True)
    user_link: str
