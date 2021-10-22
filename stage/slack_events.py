from django_simple_slack_app import slack_events, slack_commands
from scrappers import youtube
from stage.models import Playlist


@slack_events.on("message")
def message_channels(event_data):
    msg = event_data["event"]["text"]
    user = event_data["event"]["user"]

    print(f"New message: {msg} from {user}")
    songs = youtube.query(msg)

    # youtube.download(songs[0])
    Playlist.create_from(songs, user, msg)


@slack_commands.on("/dj.drop")
def my_command(event_data):
    print(f"Command {event_data['command']} has received")


@slack_commands.on("/dj.next")
def my_command(event_data):
    print(f"Command {event_data['command']} has received")


@slack_commands.on("/dj.on")
def my_command(event_data):
    event_data['client'].post_message(":loud_sound: DJ:head_phones: on the Stage!! :mega: :loud_sound:")
    print(f"Command {event_data['command']} has received")


@slack_commands.on("/dj.off")
def my_command(event_data):
    event_data['client'].post_message(":mute: the Party is over~ go home :house:")
    print(f"Command {event_data['command']} has received")
