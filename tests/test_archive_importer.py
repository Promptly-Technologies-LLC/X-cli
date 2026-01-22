import unittest
from copy import deepcopy

from sqlmodel import Session, select

from x_cli.storage.db import get_engine, init_db
from x_cli.storage.importer import build_archive_url, import_archive_data
from x_cli.storage.models import (
    Like,
    NoteTweet,
    Tweet,
    TweetHashtag,
    TweetMedia,
)


class TestArchiveImporter(unittest.TestCase):
    def test_build_archive_url(self) -> None:
        url = build_archive_url("ExampleUser")
        self.assertEqual(
            url,
            "https://fabxmporizzqflnftavs.supabase.co/storage/v1/object/public/"
            "archives/ExampleUser/archive.json",
        )

    def test_import_archive_data_inserts_and_parses(self) -> None:
        data = {
            "upload-options": {
                "keepPrivate": False,
                "uploadLikes": True,
                "startDate": "2023-01-01T00:00:00.000Z",
                "endDate": "2024-01-01T00:00:00.000Z",
            },
            "account": [
                {
                    "account": {
                        "createdVia": "oauth:123",
                        "username": "example",
                        "accountId": "42",
                        "createdAt": "2023-01-01T00:00:00.000Z",
                        "accountDisplayName": "Example",
                    }
                }
            ],
            "profile": [
                {
                    "profile": {
                        "description": {
                            "bio": "bio",
                            "website": "https://example.com",
                            "location": "Nowhere",
                        },
                        "avatarMediaUrl": "https://example.com/avatar.png",
                        "headerMediaUrl": "https://example.com/header.png",
                    }
                }
            ],
            "tweets": [
                {
                    "tweet": {
                        "created_at": "2023-05-01T00:00:00.000Z",
                        "display_text_range": ["0", "10"],
                        "edit_info": {
                            "initial": {
                                "editTweetIds": ["111"],
                                "editableUntil": "2023-05-02T00:00:00.000Z",
                                "editsRemaining": "5",
                                "isEditEligible": False,
                            }
                        },
                        "entities": {
                            "hashtags": [{"text": "Tag", "indices": ["0", "4"]}],
                            "symbols": [],
                            "user_mentions": [],
                            "urls": [],
                            "media": [
                                {
                                    "expanded_url": "https://example.com/media",
                                    "indices": ["0", "5"],
                                    "url": "https://t.co/abc",
                                    "media_url": "https://example.com/media.jpg",
                                    "id_str": "999",
                                    "id": "999",
                                    "media_url_https": "https://example.com/media.jpg",
                                    "sizes": {"small": {"w": "1", "h": "2", "resize": "fit"}},
                                    "type": "photo",
                                    "display_url": "pic.twitter.com/abc",
                                }
                            ],
                        },
                        "favorite_count": "5",
                        "in_reply_to_status_id_str": None,
                        "id_str": "111",
                        "in_reply_to_user_id": None,
                        "truncated": False,
                        "retweet_count": "2",
                        "id": "111",
                        "in_reply_to_status_id": None,
                        "created_at": "2023-05-01T00:00:00.000Z",
                        "favorited": False,
                        "full_text": "hello",
                        "lang": "en",
                        "in_reply_to_screen_name": None,
                        "in_reply_to_user_id_str": None,
                        "source": "web",
                        "retweeted": False,
                        "extended_entities": {
                            "media": [
                                {
                                    "expanded_url": "https://example.com/video",
                                    "indices": ["0", "5"],
                                    "url": "https://t.co/vid",
                                    "media_url": "https://example.com/video.jpg",
                                    "id_str": "1000",
                                    "id": "1000",
                                    "media_url_https": "https://example.com/video.jpg",
                                    "sizes": {"small": {"w": "1", "h": "2", "resize": "fit"}},
                                    "type": "video",
                                    "display_url": "pic.twitter.com/vid",
                                    "video_info": {
                                        "aspect_ratio": ["16", "9"],
                                        "variants": [
                                            {
                                                "bitrate": "128000",
                                                "content_type": "video/mp4",
                                                "url": "https://example.com/video.mp4",
                                            }
                                        ],
                                    },
                                    "additional_media_info": {"monetizable": False},
                                }
                            ]
                        },
                    }
                }
            ],
            "community-tweet": [
                {
                    "tweet": {
                        "created_at": "2023-06-01T00:00:00.000Z",
                        "display_text_range": ["0", "8"],
                        "entities": {"hashtags": [], "symbols": [], "user_mentions": [], "urls": []},
                        "favorite_count": "1",
                        "id_str": "222",
                        "truncated": False,
                        "retweet_count": "0",
                        "id": "222",
                        "favorited": False,
                        "full_text": "community",
                        "lang": "en",
                        "source": "web",
                        "retweeted": False,
                        "community_id": "99",
                        "community_id_str": "99",
                        "scopes": {"followers": True},
                    }
                }
            ],
            "note-tweet": [
                {
                    "noteTweet": {
                        "noteTweetId": "nt1",
                        "updatedAt": "2023-01-01T00:00:00.000Z",
                        "createdAt": "2023-01-01T00:00:00.000Z",
                        "lifecycle": {
                            "value": "ok",
                            "name": "ok",
                            "originalName": "ok",
                            "annotations": {},
                        },
                        "core": {
                            "styletags": [],
                            "urls": [],
                            "text": "note",
                            "mentions": [],
                            "cashtags": [],
                            "hashtags": [],
                        },
                    }
                }
            ],
            "like": [
                {"like": {"tweetId": "333", "fullText": "liked", "expandedUrl": "https://x.com"}}
            ],
            "follower": [{"follower": {"accountId": "11", "userLink": "https://x.com/11"}}],
            "following": [{"following": {"accountId": "12", "userLink": "https://x.com/12"}}],
        }

        engine = get_engine("sqlite:///:memory:")
        init_db(engine)
        with Session(engine) as session:
            counts = import_archive_data(data, session)

            self.assertEqual(counts["tweet"], 1)
            self.assertEqual(counts["community_tweet"], 1)
            self.assertEqual(counts["note_tweet"], 1)
            self.assertEqual(counts["like"], 1)
            self.assertEqual(counts["tweet_media"], 2)

            tweet = session.get(Tweet, "111")
            self.assertIsNotNone(tweet)
            self.assertEqual(tweet.favorite_count, 5)
            self.assertEqual(tweet.retweet_count, 2)
            self.assertEqual(tweet.display_text_range, [0, 10])

            hashtags = session.exec(select(TweetHashtag)).all()
            self.assertEqual(len(hashtags), 1)
            self.assertEqual(hashtags[0].start_index, 0)
            self.assertEqual(hashtags[0].end_index, 4)

            media_items = session.exec(select(TweetMedia)).all()
            self.assertEqual(len(media_items), 2)

            note = session.get(NoteTweet, "nt1")
            self.assertIsNotNone(note)

            likes = session.exec(select(Like)).all()
            self.assertEqual(len(likes), 1)

    def test_import_archive_data_incremental_update(self) -> None:
        base_data = {
            "upload-options": {
                "keepPrivate": False,
                "uploadLikes": True,
                "startDate": "2023-01-01T00:00:00.000Z",
                "endDate": "2024-01-01T00:00:00.000Z",
            },
            "account": [
                {
                    "account": {
                        "createdVia": "oauth:123",
                        "username": "example",
                        "accountId": "42",
                        "createdAt": "2023-01-01T00:00:00.000Z",
                        "accountDisplayName": "Example",
                    }
                }
            ],
            "profile": [
                {
                    "profile": {
                        "description": {
                            "bio": "bio",
                            "website": "https://example.com",
                            "location": "Nowhere",
                        },
                        "avatarMediaUrl": "https://example.com/avatar.png",
                        "headerMediaUrl": "https://example.com/header.png",
                    }
                }
            ],
            "tweets": [
                {
                    "tweet": {
                        "created_at": "2023-05-01T00:00:00.000Z",
                        "display_text_range": ["0", "10"],
                        "edit_info": {
                            "initial": {
                                "editTweetIds": ["111"],
                                "editableUntil": "2023-05-02T00:00:00.000Z",
                                "editsRemaining": "5",
                                "isEditEligible": False,
                            }
                        },
                        "entities": {
                            "hashtags": [{"text": "Tag", "indices": ["0", "4"]}],
                            "symbols": [{"text": "SYM", "indices": ["0", "3"]}],
                            "user_mentions": [
                                {
                                    "name": "Example",
                                    "screen_name": "example",
                                    "indices": ["0", "7"],
                                    "id_str": "9",
                                    "id": "9",
                                }
                            ],
                            "urls": [
                                {
                                    "url": "https://t.co/abc",
                                    "expanded_url": "https://example.com",
                                    "display_url": "example.com",
                                    "indices": ["0", "10"],
                                }
                            ],
                            "media": [
                                {
                                    "expanded_url": "https://example.com/media",
                                    "indices": ["0", "5"],
                                    "url": "https://t.co/abc",
                                    "media_url": "https://example.com/media.jpg",
                                    "id_str": "999",
                                    "id": "999",
                                    "media_url_https": "https://example.com/media.jpg",
                                    "sizes": {"small": {"w": "1", "h": "2", "resize": "fit"}},
                                    "type": "photo",
                                    "display_url": "pic.twitter.com/abc",
                                }
                            ],
                        },
                        "favorite_count": "5",
                        "id_str": "111",
                        "truncated": False,
                        "retweet_count": "2",
                        "id": "111",
                        "favorited": False,
                        "full_text": "hello",
                        "lang": "en",
                        "source": "web",
                        "retweeted": False,
                    }
                }
            ],
            "community-tweet": [
                {
                    "tweet": {
                        "created_at": "2023-06-01T00:00:00.000Z",
                        "display_text_range": ["0", "8"],
                        "entities": {"hashtags": [], "symbols": [], "user_mentions": [], "urls": []},
                        "favorite_count": "1",
                        "id_str": "222",
                        "truncated": False,
                        "retweet_count": "0",
                        "id": "222",
                        "favorited": False,
                        "full_text": "community",
                        "lang": "en",
                        "source": "web",
                        "retweeted": False,
                        "community_id": "99",
                        "community_id_str": "99",
                        "scopes": {"followers": True},
                    }
                }
            ],
            "note-tweet": [
                {
                    "noteTweet": {
                        "noteTweetId": "nt1",
                        "updatedAt": "2023-01-01T00:00:00.000Z",
                        "createdAt": "2023-01-01T00:00:00.000Z",
                        "lifecycle": {
                            "value": "ok",
                            "name": "ok",
                            "originalName": "ok",
                            "annotations": {},
                        },
                        "core": {
                            "styletags": [],
                            "urls": [],
                            "text": "note",
                            "mentions": [],
                            "cashtags": [],
                            "hashtags": [],
                        },
                    }
                }
            ],
            "like": [
                {"like": {"tweetId": "333", "fullText": "liked", "expandedUrl": "https://x.com"}}
            ],
            "follower": [{"follower": {"accountId": "11", "userLink": "https://x.com/11"}}],
            "following": [{"following": {"accountId": "12", "userLink": "https://x.com/12"}}],
        }

        second_data = deepcopy(base_data)
        second_data["tweets"].append(
            {
                "tweet": {
                    "created_at": "2023-07-01T00:00:00.000Z",
                    "display_text_range": ["0", "5"],
                    "entities": {"hashtags": [], "symbols": [], "user_mentions": [], "urls": []},
                    "favorite_count": "0",
                    "id_str": "112",
                    "truncated": False,
                    "retweet_count": "0",
                    "id": "112",
                    "favorited": False,
                    "full_text": "new",
                    "lang": "en",
                    "source": "web",
                    "retweeted": False,
                }
            }
        )
        second_data["community-tweet"].append(
            {
                "tweet": {
                    "created_at": "2023-07-02T00:00:00.000Z",
                    "display_text_range": ["0", "8"],
                    "entities": {"hashtags": [], "symbols": [], "user_mentions": [], "urls": []},
                    "favorite_count": "1",
                    "id_str": "223",
                    "truncated": False,
                    "retweet_count": "0",
                    "id": "223",
                    "favorited": False,
                    "full_text": "community2",
                    "lang": "en",
                    "source": "web",
                    "retweeted": False,
                    "community_id": "99",
                    "community_id_str": "99",
                    "scopes": {"followers": True},
                }
            }
        )
        second_data["note-tweet"].append(
            {
                "noteTweet": {
                    "noteTweetId": "nt2",
                    "updatedAt": "2023-02-01T00:00:00.000Z",
                    "createdAt": "2023-02-01T00:00:00.000Z",
                    "lifecycle": {
                        "value": "ok",
                        "name": "ok",
                        "originalName": "ok",
                        "annotations": {},
                    },
                    "core": {
                        "styletags": [],
                        "urls": [],
                        "text": "note2",
                        "mentions": [],
                        "cashtags": [],
                        "hashtags": [],
                    },
                }
            }
        )
        second_data["like"].append(
            {"like": {"tweetId": "334", "fullText": "liked2", "expandedUrl": "https://x.com/2"}}
        )
        second_data["follower"].append(
            {"follower": {"accountId": "11", "userLink": "https://x.com/13"}}
        )
        second_data["following"].append(
            {"following": {"accountId": "12", "userLink": "https://x.com/14"}}
        )

        engine = get_engine("sqlite:///:memory:")
        init_db(engine)
        with Session(engine) as session:
            import_archive_data(base_data, session)
            import_archive_data(second_data, session)

            self.assertEqual(len(session.exec(select(Tweet)).all()), 4)
            self.assertEqual(len(session.exec(select(TweetHashtag)).all()), 1)
            self.assertEqual(len(session.exec(select(TweetMedia)).all()), 1)
            self.assertEqual(len(session.exec(select(NoteTweet)).all()), 2)
            self.assertEqual(len(session.exec(select(Like)).all()), 2)
