from django_simple_slack_app import slack_events, slack_commands


@slack_events.on("message")
def message_channels(event_data):
    msg = event_data["event"]["text"]
    print(f"New message: {msg}")


@slack_commands.on("/dj.drop")
def my_command(event_data):
    print(f"Command {event_data['command']} has received")


@slack_commands.on("/dj.next")
def my_command(event_data):
    print(f"Command {event_data['command']} has received")
