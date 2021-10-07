import unittest
from pprint import pprint

import youtube


class YoutubeCase(unittest.TestCase):
    def test_query(self):
        songs = youtube.query('kenny loggins - footloose ㅋㅋㅋㅋㅋㅋ')
        pprint(songs)

    def test_download(self):
        songs = youtube.query('고등어')
        youtube.download(songs[0])


if __name__ == '__main__':
    unittest.main()
