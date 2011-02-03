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
        self.fields['body'].widget.attrs['rows'] = 16
        self.fields['excerpt'].widget.attrs['rows'] = 4
        self.fields['categories'] = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, choices=[], required=False)
        self.fields['tags'] = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, choices=[], required=False)
        
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
    
    class Meta:
        model = Post
        exclude = ['status', 'attachments']
    
    def clean_email(self):
        data = self.cleaned_data['email']
        tA = data.split('@')
        if tA[1] not in settings.WORDPRESS['AUTH']['default']['VALID_DOMAINS']:
            raise forms.ValidationError('You must use a valid email address')
        return data
    

    