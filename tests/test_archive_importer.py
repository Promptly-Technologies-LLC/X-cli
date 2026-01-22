import unittest

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
