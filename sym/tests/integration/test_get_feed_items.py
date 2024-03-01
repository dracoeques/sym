import unittest
from sym.modules.db.db import local_session
from sym.modules.discovery.core import get_feed_items
from sym.modules.db.models import MediaItem, Profile, MediaItemPersonalization

class TestGetFeedItems(unittest.TestCase):

    def setUp(self):
        engine,session_builder = local_session()
        self.engine = engine
        self.session = session_builder()
        self.addClassCleanup(self.session.close)
        self.addClassCleanup(self.engine.dispose)
        self.feed_id = 10 #set whatever feed id you want to use for testing

    def test_get_feed_items(self):
        items, error = get_feed_items(self.feed_id, session=self.session, query_builder=None)

        for item in items:
            media_item, personalization = item
            self.assertIsInstance(media_item, MediaItem)
            self.assertIsInstance(personalization, MediaItemPersonalization)
        self.assertIsNone(error)

    def test_get_feed_items_before(self):

        items, error = get_feed_items(self.feed_id, session=self.session, query_builder=None)

        for item in items:
            media_item, personalization = item
            self.assertIsInstance(media_item, MediaItem)
            self.assertIsInstance(personalization, MediaItemPersonalization)
        self.assertIsNone(error)

        #now get items before the third item
        third_media_item_personalization = items[2][1]
        before_items, error = get_feed_items(self.feed_id, session=self.session, query_builder=None, 
                                      before_id=third_media_item_personalization.id)
        
        for item in before_items:
            media_item, personalization = item
            self.assertIsInstance(media_item, MediaItem)
            self.assertIsInstance(personalization, MediaItemPersonalization)
            assert personalization.id < third_media_item_personalization.id, f"Media item: {personalization.id} should be before the third item: {third_media_item_personalization.id}"
        self.assertIsNone(error)

    def test_get_feed_items_after(self):

        items, error = get_feed_items(self.feed_id, session=self.session, query_builder=None)

        for item in items:
            media_item, personalization = item
            self.assertIsInstance(media_item, MediaItem)
            self.assertIsInstance(personalization, MediaItemPersonalization)
        self.assertIsNone(error)

        #now get items after the third item
        third_media_item_personalization = items[2][1]
        before_items, error = get_feed_items(self.feed_id, session=self.session, query_builder=None, 
                                      after_id=third_media_item_personalization.id)
        
        for item in before_items:
            media_item, personalization = item
            self.assertIsInstance(media_item, MediaItem)
            self.assertIsInstance(personalization, MediaItemPersonalization)
            assert personalization.id > third_media_item_personalization.id, f"Media item: {personalization.id} should be after the third item: {third_media_item_personalization.id}"
        self.assertIsNone(error)

if __name__ == '__main__':
    unittest.main()