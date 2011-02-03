import hashlib
import datetime

from django.db import models
from django_extensions.db.fields import CreationDateTimeField
from django_extensions.db.fields import ModificationDateTimeField
from django.conf import settings

STATUSES = (
    ('new', 'new'),
    ('pending', 'pending'),
    ('processed', 'processed'),
    ('invalid', 'invalid'),
    ('error', 'error')
)

class KeyStore(models.Model):
    created_at = CreationDateTimeField()
    updated_at = ModificationDateTimeField()
    key = models.CharField(max_length=255)
    value = models.TextField()
    
    def __unicode__(self):
        return self.value

class Post(models.Model):
    created_at = CreationDateTimeField()
    status = models.CharField(max_length=40, choices=STATUSES, default='new')
    title = models.CharField(max_length=255)
    body = models.TextField()
    excerpt = models.TextField(blank=True)
    email = models.EmailField()
    categories = models.TextField(blank=True)
    tags = models.TextField(blank=True)
    remote_url = models.CharField(max_length=255, blank=True, null=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __unicode__(self):
        return self.title

class Attachment(models.Model):
    created_at = CreationDateTimeField()
    status = models.CharField(max_length=40, choices=STATUSES, default='new')
    file = models.FileField(upload_to='uploads/attachments/')
    post = models.ForeignKey('publisher.Post', related_name='attachments')
    remote_url = models.CharField(max_length=255, blank=True, null=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __unicode__(self):
        return '%s' % self.file

# used when settings.WORDPRESS['AUTH']['default']['METHOD'] == 'EMAIL'
class Authorization(models.Model):
    created_at = CreationDateTimeField()
    status = models.CharField(max_length=40, choices=STATUSES, default='new')
    post = models.ForeignKey('publisher.Post')
    code = models.CharField(max_length=255)
    
    class Meta:
        ordering = ['created_at']
    
    def __unicode__(self):
        return '%s->%s' % (self.post.email, self.post.title)
    
    def save(self, *args, **kwargs):
        h = hashlib.sha1()
        h.update('%s' % datetime.datetime.now())
        h.update(settings.SECRET_KEY)
        h.update(self.post.email)
        self.code = h.hexdigest()
        super(Authorization, self).save(*args, **kwargs)

