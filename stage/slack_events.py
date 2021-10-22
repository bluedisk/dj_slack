from dj_slack.urls import dj
from django_simple_slack_app import slack_events, slack_commands
from scrappers import youtube
from stage.models import Playlist


@slack_events.on("message")
def message_channels(event_data):
    msg = event_data["event"]["text"]
    print(f"New message: {msg}")
    songs = youtube.query(msg)

    # youtube.download(songs[0])
    Playlist(songs[0])


@slack_commands.on("/dj.drop")
def my_command(event_data):
    print(f"Command {event_data['command']} has received")


@slack_commands.on("/dj.next")
def my_command(event_data):
    print(f"Command {event_data['command']} has received")


@slack_commands.on("/dj.on")
def my_command(event_data):
    dj.start_djing()
    event_data['client'].post_message(":loud_sound: DJ:head_phones: on the Stage!! :mega: :loud_sound:")
    print(f"Command {event_data['command']} has received")


@slack_commands.on("/dj.off")
def my_command(event_data):
    dj.stop_djing()
    event_data['client'].post_message(":mute: the Party is over~ go home :house:")
    print(f"Command {event_data['command']} has received")
