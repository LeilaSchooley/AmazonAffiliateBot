import unittest
from unittest.mock import MagicMock
from your_script import upload_to_youtube  # Adjust the import according to your script's name

class TestUploadToYoutube(unittest.TestCase):

    def setUp(self):
        # Create a mock page object
        self.mock_page = MagicMock()
        # Setup the mock to return a specific title when TinyTag.get(video).title is called
        self.mock_page.set_input_files = MagicMock()
        self.mock_page.click = MagicMock()
        self.mock_page.fill = MagicMock()
        self.mock_page.content = MagicMock(return_value="Upload complete")

    def test_upload_message(self):
        # Call the function with the mock
        upload_to_youtube(self.mock_page)

        # Check if the success message was printed
        self.mock_page.content.assert_called_with()
        self.assertIn("Upload complete", self.mock_page.content())

if __name__ == '__main__':
    unittest.main()
