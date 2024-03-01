import unittest
from datetime import timezone, datetime
from unittest.mock import MagicMock, patch
from datetime import datetime
from sym.modules.discovery.core import get_feed_items
from sym.modules.db.models import MediaItem, Profile, MediaItemPersonalization

class TestGetFeedItems(unittest.TestCase):
    
    @patch('sym.modules.discovery.core.local_session')
    def test_get_feed_items(self, mock_local_session):
        # Mock the session and the query objects
        mock_session = MagicMock()
        
        
        mock_feed_items_query_builder = MagicMock()
        mock_feed_items_query = MagicMock()
        mock_feed_items_query_builder.return_value = mock_feed_items_query

        media_items = [
            (MediaItem(id=1, title="Item 1", created_on=datetime.utcnow()), MediaItemPersonalization(text="Personalized Summary 1")),
            (MediaItem(id=1, title="Item 2", created_on=datetime.utcnow()), MediaItemPersonalization(text="Personalized Summary 2")),
            (MediaItem(id=1, title="Item 3", created_on=datetime.utcnow()), MediaItemPersonalization(text="Personalized Summary 3"))
            
        ]
        mock_feed_items_query.all.return_value = media_items

        # Call the function with the mocked session
        items, error = get_feed_items(1, session=mock_session, query_builder=mock_feed_items_query_builder)

        # Assert that the function returned the expected result
        self.assertEqual(items, media_items)
        self.assertIsNone(error)

    def test_media_item_to_dict(self):
        # Create a mock MediaItem object
        media_item = MagicMock(spec=MediaItem)

        # Set the attributes of the mock object
        media_item.id = 1
        media_item.id_source = "source1"
        media_item.kind = "article"
        media_item.source_url = "https://example.com/article1"
        media_item.title = "Article 1"
        media_item.summary = "This is the summary of Article 1."
        media_item.image = "https://example.com/images/article1.jpg"
        media_item.payload = { "key":"This is the payload of Article 1."}
        media_item.created_on = datetime(2021, 1, 1, 0, 0, 0, 0, timezone.utc)
        media_item.updated_on = datetime(2021, 1, 1, 0, 0, 0, 0, timezone.utc)

        # Call the to_dict method
        result = MediaItem.to_dict(media_item)

        # Assert that the method returned the expected result
        self.assertEqual(result, {
            "id": 1,
            "id_source": "source1",
            "kind": "article",
            "source_url": "https://example.com/article1",
            "title": "Article 1",
            "summary": "This is the summary of Article 1.",
            "image": "https://example.com/images/article1.jpg",
            "payload": { "key":"This is the payload of Article 1."},
            "created_on": datetime(2021, 1, 1, 0, 0, 0, 0, timezone.utc).isoformat(),
            "updated_on": datetime(2021, 1, 1, 0, 0, 0, 0, timezone.utc).isoformat()
        })

    

if __name__ == '__main__':
    unittest.main()