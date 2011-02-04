# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'Attachment.position'
        db.add_column('publisher_attachment', 'position', self.gf('django.db.models.fields.CharField')(default='', max_length=255, blank=True), keep_default=False)

        # Adding field 'Attachment.align'
        db.add_column('publisher_attachment', 'align', self.gf('django.db.models.fields.CharField')(default='', max_length=255, blank=True), keep_default=False)

        # Changing field 'Attachment.remote_url'
        db.alter_column('publisher_attachment', 'remote_url', self.gf('django.db.models.fields.CharField')(max_length=255))


    def backwards(self, orm):
        
        # Deleting field 'Attachment.position'
        db.delete_column('publisher_attachment', 'position')

        # Deleting field 'Attachment.align'
        db.delete_column('publisher_attachment', 'align')

        # Changing field 'Attachment.remote_url'
        db.alter_column('publisher_attachment', 'remote_url', self.gf('django.db.models.fields.CharField')(max_length=255, null=True))


    models = {
        'publisher.attachment': {
            'Meta': {'ordering': "['created_at']", 'object_name': 'Attachment'},
            'align': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'blank': 'True'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'position': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'blank': 'True'}),
            'post': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'attachments'", 'to': "orm['publisher.Post']"}),
            'remote_url': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'new'", 'max_length': '40'})
        },
        'publisher.authorization': {
            'Meta': {'ordering': "['created_at']", 'object_name': 'Authorization'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'post': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['publisher.Post']"}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'new'", 'max_length': '40'})
        },
        'publisher.keystore': {
            'Meta': {'object_name': 'KeyStore'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'value': ('django.db.models.fields.TextField', [], {})
        },
        'publisher.post': {
            'Meta': {'ordering': "['created_at']", 'object_name': 'Post'},
            'body': ('django.db.models.fields.TextField', [], {}),
            'categories': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'default': "''", 'max_length': '75', 'blank': 'True'}),
            'excerpt': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'remote_url': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'new'", 'max_length': '40'}),
            'tags': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'wordpress_username': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'blank': 'True'})
        }
    }

    complete_apps = ['publisher']
