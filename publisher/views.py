import re

from django.conf import settings
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe

from publisher.forms import PostForm
from publisher.models import Authorization, Attachment
from publisher.tasks import transfer_post, send_email

def post(request):
    form = PostForm(request.POST or None, request.FILES or None)
    
    if request.POST:
        if form.is_valid():
            # save into db, ehh
            post = form.save()
            
            # check for attachments?
            if request.FILES:
                for f in request.FILES.getlist('attachments'):
                    a = Attachment()
                    a.post = post
                    a.file.save(f.name, f)
                    a.save()
            
            # save an authorization
            auth = Authorization()
            auth.post = post
            auth.save()
            
            # send authorization email
            html_content = render_to_string('authorize_email.html', {
                'post': post,
                'site': request.get_host(),
                'MEDIA_URL': settings.MEDIA_URL,
                'code': auth.code,
            })
            
            send_email('Authorize Blog Post', html_content, [post.email])
            
            # at this point, we could also notify admin team, and they could authorize it, but it would still need to be sent over the WebBlog api
            
            # add message to the messages framework and redirect to prevent duplicate submission
            messages.success(request, 'To confirm your submission, please follow the instructions in your email (sent from %s).' % settings.WORDPRESS['FROM_EMAIL'])
            return HttpResponseRedirect(reverse('publisher_index'))
        else:
            # likely report errors
            pass
        
    return render_to_response('post.html', {
        'form': form,
    }, context_instance=RequestContext(request))

def index(request):
    return render_to_response('index.html', {
        
    }, context_instance=RequestContext(request))

def authorize(request, code):
    # look up authorization, check status
    try:
        auth = Authorization.objects.get(code=code, status='new')
        auth.status = 'pending'
        auth.save()
        if transfer_post(auth.post.id):
            auth.status = 'processed'
            auth.save()
            messages.success(request, 'Your blog post has been sent on to the editorial team.')
            return HttpResponseRedirect(reverse('publisher_index'))
        else:
            messages.error(request, mark_safe('There were problems submitting your post, please contact <a href="mailto:%s?subject=Blog Publisher Error-[id %s]">%s</a> for assistance' % ( settings.WORDPRESS['ADMIN_EMAIL'], post.id, settings.WORDPRESS['ADMIN_NAME'] )))
            auth.status = 'error'
            auth.save()
    except Authorization.DoesNotExist:
        messages.error(request, 'Authorization is invalid or the post has already been submitted.')
        return HttpResponseRedirect(reverse('publisher_index'))
    
    return render_to_response('authorize.html', {
    
    }, context_instance=RequestContext(request))

