from django.db import models


class Song(models.Model):
    title = models.CharField('Song Title', max_length=2048, null=False)

    status_choices = (
        ('new', 'New song'),
        ('down', 'Now downloading'),
        ('ready', 'Ready to Play'),
        ('error', 'Something are wrong'),
    )
    status = models.CharField('Status', max_length=6, choices=status_choices, default='down', db_index=True)
    logs = models.TextField('logs')

    filename = models.CharField('Filename', max_length=2048, null=False)
    url = models.CharField('Source URL', max_length=2048, null=False)
    duration = models.IntegerField('Duration(secs)', default=0, null=False)

    created_at = models.DateTimeField(auto_now_add=True, null=False)
    updated_at = models.DateTimeField(auto_now=True, null=False)


class Playlist(models.Model):
    song = models.ManyToManyField(Song, related_name='play_history')
    requester = models.CharField('Requester', max_length=1024)

    query = models.CharField('Request Query', max_length=2048)
    candidates = models.JSONField('Candidates')

    status_choices = (
        ('new', 'New in the list'),
        ('down', 'Now downloading'),
        ('ready', 'Ready to Play'),
        ('play', 'Now playing'),
        ('done', 'Played'),

        ('cancel', 'Requests canceled'),
        ('error', 'Something are wrong'),
    )
    status = models.CharField('Status', max_length=6, choices=status_choices, default='new', db_index=True)

    created_at = models.DateTimeField(auto_now_add=True, null=False)
    updated_at = models.DateTimeField(auto_now=True, null=False)
    played_at = models.DateTimeField(null=False)
