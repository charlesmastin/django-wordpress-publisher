from django.contrib import admin

from publisher.models import *

class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'remote_url', 'email', 'created_at', 'status']
    list_filter = ['status']

class AttachmentAdmin(admin.ModelAdmin):
    list_display = ['file', 'post', 'created_at', 'status']
    list_filter = ['status']

class AuthorizationAdmin(admin.ModelAdmin):
    list_display = ['post', 'code', 'status']
    list_filter = ['status']

admin.site.register(Post, PostAdmin)
admin.site.register(Attachment, AttachmentAdmin)
admin.site.register(Authorization, AuthorizationAdmin)