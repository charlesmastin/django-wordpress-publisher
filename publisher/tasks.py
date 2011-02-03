import ast
import base64
import mimetypes
import os
import re
import xmlrpclib

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

import pyblog

from publisher.models import Post, Attachment

def transfer_post(post_id, wordpress_user=None, wordpress_password=None):
    wp_user = settings.WORDPRESS['USER']
    if wordpress_user:
        wp_user = wordpress_user
    wp_pass = settings.WORDPRESS['PASSWORD']
    if wordpress_password:
        wp_pass = wordpress_password
    try:
        post = Post.objects.get(pk=post_id, status='new')
    except PostDoesNotExist:
        return False
    blog = pyblog.WordPress(settings.WORDPRESS['RPC_URL'], wp_user, wp_pass)
    
    content = {'title': post.title, 'description': post.body}
    categories = []
    try:
        categories.extend(ast.literal_eval(post.categories))
    except:
        pass
    if len(categories):
        content['categories'] = categories
    
    if len(post.tags):
        content['mt_keywords'] = ', '.join(ast.literal_eval(post.tags))
    
    if len(post.excerpt):
        content['mt_excerpt'] = post.excerpt
    
    try:
        new_post = blog.new_post(content, False)
        post.status = 'processed'
        post.remote_url = '%s/wp-admin/post.php?post=%s&action=edit' % (settings.WORDPRESS['BASE_URL'], new_post)
        post.save()
    except:
        post.status = 'error'
        post.save()
        return False
    
    if post.attachments:
        for attachment in post.attachments.all():
            mimetype = 'image/jpeg' #default
            try:
                m = mimetypes.guess_type(attachment.file.name)
                mimetype = m[0]
            except:
                pass
            
            try:
                remote_attachment = blog.upload_file(
                    {
                        'name': 'api-%s-%s' % (attachment.pk, os.path.basename(attachment.file.name)),
                        'type': mimetype,
                        'bits': xmlrpclib.Binary(attachment.file.read()),
                        'overwrite': 'false'
                    }
                )
                attachment.remote_url = remote_attachment['url']
                attachment.status = 'processed'
                attachment.save()
            except:
                attachment.status = 'error'
                attachment.save()
            
    
    # send an email to the admins
    html_content = render_to_string('team_email.html', {
        'post': post,
        'MEDIA_URL': settings.MEDIA_URL,
    })
    
    send_email('New Blog Post Submission', html_content, [settings.WORDPRESS['ADMIN_EMAIL']])
    
    return True

def send_email(header_subject, body, header_to, header_from=None):
    # we could throw this off into a thread, or use a queing system to improve performance
    if not header_from:
        header_from = settings.DEFAULT_FROM_EMAIL
    try:
        text_content = re.sub(r'<[^>]*?>', '', body)
        msg = EmailMultiAlternatives(header_subject, text_content, header_from, header_to)
        msg.attach_alternative(body, "text/html")
        msg.send()
    except:
        pass