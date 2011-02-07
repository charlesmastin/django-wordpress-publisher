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
from PIL import Image

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
    
    publish = False
    try:
        if settings.WORDPRESS['AUTO_PUBLISH']:
            content['post_status'] = 'publish'
            publish = True
    except KeyError:
        pass
    
    body_top_extra = []
    body_bottom_extra = []
    
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
                
                attachment_html = ''
                
                try:
                    # we could implement some validation, thanks django source fields.py, but we'll skip for now. ah, the joy of too many options
                    attachment_image = Image.open(attachment.file.path)
                    attachment_html = '<a href="%s"><img class="%s size-full" title="%s" src="%s" alt="" width="%s" height="%s" /></a>' % ( 
                        attachment.remote_url, attachment.align, os.path.basename(attachment.file.name), attachment.remote_url, attachment_image.size[0], attachment_image.size[1]
                    )
                except ImportError:
                    raise
                except Exception:
                    # we're something else, like a pdf, just make a link
                    attachment_html = '<a href="%s">%s</a>' % (attachment.remote_url, os.path.basename(attachment.file.name))
                
                if attachment.position == 'top':
                    body_top_extra.append(attachment_html)
                
                if attachment.position == 'bottom':
                    body_bottom_extra.append(attachment_html)
                
                attachment.status = 'processed'
                attachment.save()
            except:
                attachment.status = 'error'
                attachment.save()
    
    try:
        if len(body_top_extra):
            content['description'] = '%s<br />%s' % ('<br />'.join(body_top_extra), content['description'])
        
        if len(body_bottom_extra):
            content['description'] = '%s<br />%s' % (content['description'], '<br />'.join(body_bottom_extra))
        new_post = blog.new_post(content, publish)
        post.status = 'processed'
        post.remote_url = '%s/wp-admin/post.php?post=%s&action=edit' % (settings.WORDPRESS['BASE_URL'], new_post)
        post.save()
    except:
        post.status = 'error'
        post.save()
        return False
    
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