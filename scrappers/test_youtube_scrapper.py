import os
import shutil

from django.conf import settings
from django.test import TestCase

from scrappers import youtube

QUERIES = (
    ('Se so neon - midnight train plz', 'MgyhJ-F-IpM'),
    ('kenny loggins - footloose ㅋㅋㅋㅋㅋㅋ', 'ltrMfT4Qz5Y'),
    ('카레', 'ao58vQDMVlQ'),
    ('stay - Alessia Cara', 'h--P8HzYZ74'),
    ('가을 아침 - IU', 'ZDoH5dQ58ps')
)


class YoutubeScrapperCase(TestCase):

    def setUpClass(self) -> None:
        if os.path.exists(settings.DOWNLOADS_PATH):
            shutil.rmtree(settings.DOWNLOADS_PATH)

    def tearDownClass(self) -> None:
        if os.path.exists(settings.DOWNLOADS_PATH):
            shutil.rmtree(settings.DOWNLOADS_PATH)

    def test_query(self):
        for query, id in QUERIES:
            songs = youtube.query(query)
            self.assertEqual(songs[0]['id'], id, f"checking for '{query}' => {songs}")

    def test_download(self):
        songs = youtube.query('고등어')
        youtube.download(songs[0], settings.DOWNLOADS_PATH)

        expected_filename = os.path.join(settings.DOWNLOADS_PATH, f"{songs[0]['id']}.aac")
        self.assertTrue(os.path.isfile(expected_filename))
        self.assertGreater(0, os.path.getsize(expected_filename))
