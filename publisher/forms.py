import datetime
import json

from django import forms
from django.conf import settings

import pyblog

from publisher.models import Post, KeyStore

class PostForm(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        super(PostForm, self).__init__(*args, **kwargs)
        self.fields['title'].widget.attrs['title'] = 'A catchy title'
        self.fields['body'].widget.attrs['title'] = 'Pulitzer award winning text goes here, don\'t be shy'
        self.fields['excerpt'].widget.attrs['title'] = 'Optionally, provide an excerpt'
        self.fields['email'].widget.attrs['title'] = 'Lastly, we need your email for verification'
        self.fields['wordpress_username'].widget.attrs['title'] = 'Your wordpress username'
        self.fields['body'].widget.attrs['rows'] = 16
        self.fields['excerpt'].widget.attrs['rows'] = 4
        self.fields['categories'] = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, choices=[], required=False)
        self.fields['tags'] = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, choices=[], required=False)
        
        try:
            settings.WORDPRESS['AUTH']['email']
        except KeyError:
            del(self.fields['email'])
        
        try:
            settings.WORDPRESS['AUTH']['wordpress']
            self.fields['wordpress_password'] = forms.RegexField(
                regex=r'^\w+$',
                min_length=5,
                max_length=50,
                widget=forms.PasswordInput(render_value=False),
                label="Wordpress Password",
                error_messages={'invalid': 'This is an invalid wordpress password'},
                required=False
            )
            
            try:
                self.fields['email'].widget.attrs['title'] = 'Optionally, verify with your email if you don\'t have a wordpress account'
            except KeyError:
                pass
            
        except KeyError:
            pass
        
        categories = []
                
        try:
            value = KeyStore.objects.get(key='blog_categories', updated_at__gte=datetime.datetime.now() - datetime.timedelta(hours=1))
            categories = json.loads(value.value)
        except KeyStore.DoesNotExist:
            blog = pyblog.WordPress(settings.WORDPRESS['RPC_URL'], settings.WORDPRESS['USER'], settings.WORDPRESS['PASSWORD'])
            categories = blog.get_categories()
            value = json.dumps(categories)
            
            try:
                key = KeyStore.objects.get(key='blog_categories')
                key.value = value
                key.save()
            except KeyStore.DoesNotExist:
                key = KeyStore(key='blog_categories', value=value)
                key.save()
        
        for category in categories:
            self.fields['categories'].choices.append((category['categoryName'], category['categoryName']))
        
        tags = []
                
        try:
            value = KeyStore.objects.get(key='blog_tags', updated_at__gte=datetime.datetime.now() - datetime.timedelta(hours=1))
            tags = json.loads(value.value)
        except KeyStore.DoesNotExist:
            blog = pyblog.WordPress(settings.WORDPRESS['RPC_URL'], settings.WORDPRESS['USER'], settings.WORDPRESS['PASSWORD'])
            tags = blog.get_tags()
            value = json.dumps(tags)
            
            try:
                key = KeyStore.objects.get(key='blog_tags')
                key.value = value
                key.save()
            except KeyStore.DoesNotExist:
                key = KeyStore(key='blog_tags', value=value)
                key.save()
        
        for tag in tags:
            self.fields['tags'].choices.append((tag['name'], tag['name']))
    
    class Meta:
        model = Post
        exclude = ['status', 'attachments']
    
    def clean_email(self):
        data = self.cleaned_data['email']
        # whitelisting, we could blacklist too
        if len(data):
            try:
                settings.WORDPRESS['AUTH']['email']['VALID_DOMAINS']
                tA = data.split('@')
                if tA[1] not in settings.WORDPRESS['AUTH']['email']['VALID_DOMAINS']:
                    raise forms.ValidationError('You must use a valid email address')
            except KeyError:
                pass
        return data
    

    