from random import sample
from subprocess import TimeoutExpired, Popen

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db.transaction import atomic

from stage.models import Playlist


class DJ:
    def __init__(self, verbose_mode):
        self.idle_mode = True
        self.player = None
        self.available_songs = Playlist.objects.filter(status='ready')
        self.verbose_mode = verbose_mode

    def djing(self):
        while True:
            try:
                if self.player:
                    self.player.wait(1)

                self.play_next()

            except TimeoutExpired:
                if self.idle_mode and self.available_songs.exists():
                    self.play_next()

            finally:
                self.sync()

    def log(self, msg):
        if self.verbose_mode:
            print(msg)

    @atomic
    def play_next(self):
        if self.available_songs.exists():
            if self.idle_mode and self.player:
                self.log("Killing lounge music player")
                self.player.kill()
                self.player.join()
                self.player = None

            self.idle_mode = False
            song_id, song_info = self.available_songs.first().delete()

            self.log(f"Playing {song_info['title']} / {song_info['filename']}")
            filename = song_info['filename']

            self.play(filename)
            return

        self.idle_mode = True
        self.play_lounge_music()

    def play(self, filename):
        self.log(f"Playing {filename}")
        self.player = Popen([settings.PLAYER_BIN, '--play-and-exit', filename])

    def play_lounge_music(self):
        self.log(f"Playing the lounge music")
        self.player = Popen([settings.PLAYER_BIN, ] + sample(settings.LOUNGE_MUSICS, 1))

    def sync(self):
        pass


class Command(BaseCommand):
    help = 'DJ! play that music louder!'

    def add_arguments(self, parser):
        #parser.add_argument('-v', action='store_true', help='Verbose mode')
        pass

    def handle(self, *args, **options):
        verbose_mode = (options['verbosity'] >= 2)
        DJ(verbose_mode).djing()
