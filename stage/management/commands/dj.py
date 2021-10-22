from random import sample
from subprocess import TimeoutExpired, Popen

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db.transaction import atomic

from stage.models import Playlist


class DJ:
    def __init__(self):
        self.idle_mode = True
        self.player = None
        self.available_songs = Playlist.objects.filter(status='ready')

    def djing(self):
        while True:
            if self.idle_mode:
                try:
                    if self.player:
                        self.player.wait(1)

                    self.play_next()

                except TimeoutExpired:
                    if self.available_songs.exists():
                        self.play_next()

            else:
                try:
                    if self.player:
                        self.player.wait(1)

                    self.play_next()

                except TimeoutExpired:
                    pass

    @atomic
    def play_next(self):
        if self.available_songs.exists():
            if self.idle_mode and self.player:
                print("Killing lounge music player")
                self.player.kill()
                self.player.join()
                self.player = None

            self.idle_mode = False
            song_id, song_info = self.available_songs.first().delete()

            print(f"Playing {song_info['title']} / {song_info['filename']}")
            filename = song_info['filename']

            self.play(filename)
            return

        self.idle_mode = True
        self.play_lounge_music()

    def play(self, filename):
        print(f"Playing {filename}")
        self.player = Popen([settings.PLAYER_BIN, '--play-and-exit', filename])

    def play_lounge_music(self):
        print(f"Playing the lounge music")
        self.player = Popen([settings.CVLC_BIN, ] + sample(settings.LOUNGE_MUSICS, 1))


class Command(BaseCommand):
    help = 'DJ! play that music louder!'

    # def add_arguments(self, parser):
    #     parser.add_argument('poll_ids', nargs='+', type=int)

    def handle(self, *args, **options):
        DJ().djing()
