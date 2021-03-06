import json
import os.path
from collections import Counter
from datetime import timedelta
from typing import TypedDict

import requests
# Scrapper
import youtube_dl

CONTENT_PREFIX = 'ytInitialData = '
SEARCH_ENDPOINT = "https://www.youtube.com/results"
PLAY_URL_FORMAT = "https://youtube.com/watch?v={}"

# Sorter
OWNER_WEIGHT = 5

POSITIVE_KEYWORDS = ['[MV]', 'M/V', 'Official', 'Music Video', 'VEVO']
NEGATIVE_KEYWORDS = [
    # Version issue
    'Acoustic', 'Karaoke', 'Ver.', 'Live', 'Inst.', 'Instrumental', '노래방',

    # 3rd party
    'Cover', '커버', 'Teaser',

    # recreated contents
    '근황', '팬', 'B-cut', '촬영', '댓글',
]

POSITIVE_OWNERS = [
    # Validated owners
    '1theK (원더케이)',
    'Music is my life',
    'MUSIC&NEW 뮤직앤뉴',
    'Sony Music Korea',

    # Positive keywords
    'MBC', 'KBS', 'kpop', 'song', 'music',
    'Entertainment', '뮤직', 'BGM'
]

NEGATIVE_OWNERS = [
    # Validated negative owners
    '백종원', '주부', '요리', 'TJ KARAOKE TJ 노래방 공식 유튜브채널', 'MBCNEWS', 'YTN', '고용노동부',

    # Negative keywords
    'NEWS', '뉴스', '지식']

SongInfo = TypedDict('SongInfo', {
    'title': str,
    'id': int,
    'url': str,
    'thumbnail': str,
    'playtime': timedelta,
    'view': int,
    'owner': str,
    'owner_badge': list[str],
    'penalty': int
})


def _query_youtube(query_string: str) -> list[SongInfo]:
    res = requests.get(SEARCH_ENDPOINT, {"search_query": query_string})
    if res.status_code != 200:
        return []

    raw_contents = ""
    for idx, script in enumerate(res.text.split('</script>')):
        pos = script.find(CONTENT_PREFIX)
        if pos != -1:
            starts_at = pos + len(CONTENT_PREFIX)
            raw_contents = script[starts_at:-1]
            break

    contents = json.loads(raw_contents)
    contents = contents['contents']['twoColumnSearchResultsRenderer']['primaryContents']
    contents = contents['sectionListRenderer']['contents'][0]['itemSectionRenderer']['contents']
    contents = [c['videoRenderer'] for c in contents if 'videoRenderer' in c]

    def parse_playtime(playtime):
        slices = [int(i) for i in playtime.split(':')]
        slices_count = len(slices)

        if slices_count == 3:
            hours, minutes, seconds = slices
            return timedelta(hours=hours, minutes=minutes, seconds=seconds)

        elif slices_count == 2:
            minutes, seconds = slices
            return timedelta(minutes=minutes, seconds=seconds)

        else:
            raise Exception(playtime)

    return [SongInfo(
        title=c['title']['runs'][0]['text'],
        id=c['videoId'],
        url=PLAY_URL_FORMAT.format(c['videoId']),
        thumbnail=c['thumbnail']['thumbnails'][0]['url'],
        playtime=parse_playtime(c['lengthText']['simpleText']),
        view=int(''.join(filter(str.isdigit, c['viewCountText']['simpleText']))),
        owner=c['ownerText']['runs'][0]['text'],
        owner_badge=[b['metadataBadgeRenderer']['style'] for b in c.get('ownerBadges', [])],
        penalty=idx
    ) for idx, c in enumerate(contents)]


def _prioritize_links(songs: list[SongInfo], positive_keywords) -> list[SongInfo]:
    def keyword_count(title, keywords):
        checking = [title.lower().find(keyword.lower()) != -1 for keyword in keywords]
        return Counter(checking).get(True, 0)

    for song in songs:
        # title penalty
        song['penalty'] -= keyword_count(song['title'], POSITIVE_KEYWORDS + positive_keywords)
        song['penalty'] += keyword_count(song['title'], NEGATIVE_KEYWORDS)

        # owner penalty
        song['penalty'] -= keyword_count(song['owner'], POSITIVE_OWNERS + positive_keywords) * OWNER_WEIGHT
        song['penalty'] += keyword_count(song['owner'], NEGATIVE_OWNERS) * OWNER_WEIGHT

        # owner badge penalty
        if 'BADGE_STYLE_TYPE_VERIFIED' in song['owner_badge']:
            song['penalty'] -= 10

        # playtime penalty
        if not timedelta(seconds=15) < song['playtime'] < timedelta(minutes=15):
            song['penalty'] += 10

    return sorted(songs, key=lambda x: x['penalty'])


# response format:
#
# [{
#  'title': 'Norazo - Mackerel, 노라조 - 고등어, Music Core 20090711',
#  'id': 'SwFF_HSfmXE',
#  'url': 'https://youtube.com/watch?v=SwFF_HSfmXE',
#  'thumbnail': 'https://i.ytimg.com/vi/SwFF_HSfmXE/hq720.jpg?sqp=-oay ... Qj0AgKJDeAE=&rs=AOn4CLCQObT ... 5W2_ebA',
#  'playtime': datetime.timedelta(seconds=196),
#  'view': 124543,
#  'owner': 'MBCkpop',
#  'penalty': -5
#  }, ...]

def query(query_string: str) -> list[SongInfo]:
    links = _query_youtube(query_string)
    return _prioritize_links(links, [k.strip() for k in query_string.split('-')])


def download(song_info, target_folder='downloads'):
    os.makedirs(target_folder, exist_ok=True)

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': f"{target_folder}/%(display_id)s.%(ext)s",
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'aac',
        }]
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([song_info['url']])
