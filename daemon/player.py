from multiprocessing import Process, Queue
from subprocess import Popen, TimeoutExpired
from random import sample

from django.conf import settings


class DJ(Process):

    def __init__(self):
        super().__init__()
        self.on_stage = False
        self.queue = Queue()

        self.player = None
        self.mode = 'idle'

    def start_djing(self):
        self.on_stage = True
        self.start()
        print("DJ on the Stage! yey!")

    def stop_djing(self):
        self.on_stage = False
        self.join()

    def run(self):
        while self.on_stage:
            try:
                if self.player:
                    self.player.wait(1)
            except TimeoutExpired:
                continue

            self.play_next()

    def play_next(self):
        filename = self.queue.get_nowait()

        if not filename:
            self.play_lounge_music()
        else:
            self.play(filename)

    def play(self, filename):
        self.player = Popen([settings.PLAYER_BIN, filename])

    def play_lounge_music(self):
        self.player = Popen([settings.CVLC_BIN, ] + sample(settings.LOUNGE_MUSICS, 1))

    def add(self, filename):
        self.queue.put(filename)

        if self.mode == 'idle' and self.player:
            self.player.kill()

