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
from publisher.models import Authorization, Attachment, ALIGNMENTS, POSITIONS
from publisher.tasks import transfer_post, send_email

def post(request):
    form = PostForm(request.POST or None, request.FILES or None)
    
    if request.POST:
        if form.is_valid():
            post = form.save()
            
            if request.FILES:
                positions = request.POST.getlist('positions')
                alignments = request.POST.getlist('alignments')
                for i, f in enumerate(request.FILES.getlist('attachments')):
                    a = Attachment()
                    a.post = post
                    a.file.save(f.name, f)
                    a.position = positions[i]
                    a.alignment = alignments[i]
                    a.save()
            
            # wordpress auth
            try:
                settings.WORDPRESS['AUTH']['wordpress']
                if form.cleaned_data['wordpress_username'] and form.cleaned_data['wordpress_password']:
                    # process and return now
                    if transfer_post(post.id, form.cleaned_data['wordpress_username'], form.cleaned_data['wordpress_password']):
                        messages.success(request, 'Your blog post has been sent on to the editorial team.')
                    else:
                        messages.error(request, mark_safe('There were problems submitting your post, please contact <a href="mailto:%s?subject=Blog Publisher Error-[id %s]">%s</a> for assistance' % ( settings.WORDPRESS['ADMIN_EMAIL'], post.id, settings.WORDPRESS['ADMIN_NAME'] )))
                    return HttpResponseRedirect(reverse('publisher_index'))
            except KeyError:
                pass
            
            # email auth
            try:
                settings.WORDPRESS['AUTH']['email']
                if form.cleaned_data['email']:
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
            except KeyError:
                pass
            # anonymous auth
            
            
        else:
            messages.error(request, 'There were errors processing your submission')
            return HttpResponseRedirect(reverse('publisher_index'))
    
    return render_to_response('post.html', {
        'ALIGNMENTS': ALIGNMENTS,
        'POSITIONS': POSITIONS,
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

