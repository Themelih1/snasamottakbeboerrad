from django import forms
from .models import Comment, BlogPost, TeamMember
from tinymce.widgets import TinyMCE
from django.contrib.flatpages.models import FlatPage
from captcha.fields import CaptchaField
from django.utils.translation import gettext_lazy as _

class CommentForm(forms.ModelForm):
    subscribe_newsletter = forms.BooleanField(
        required=False,
        initial=False,
        label=_('Subscribe to newsletter'),
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    captcha = CaptchaField()

    class Meta:
        model = Comment
        fields = ['name', 'email', 'content']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': _('Your name')}),
            'email': forms.EmailInput(attrs={'placeholder': _('Your email')}),
            'content': forms.Textarea(attrs={'rows': 5, 'placeholder': _('Your comment')}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['captcha'].label = _('Security Code')
        


class BlogPostForm(forms.ModelForm):
    slug = forms.SlugField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Otomatik oluşturulacak',
            'readonly': 'readonly'
        })
    )
    
    class Meta:
        model = BlogPost
        fields = '__all__'
        widgets = {
            'content': TinyMCE(attrs={
                'cols': 80,
                'rows': 30,
                'plugins': 'link image code',
                'toolbar': 'undo redo | styleselect | bold italic | alignleft aligncenter alignright | link image | code',
            }),
            'summary': forms.Textarea(attrs={'rows': 3}),
        }     
class FlatPageForm(forms.ModelForm):
    class Meta:
        model = FlatPage
        fields = ['title', 'content', 'url']

class TeamMemberForm(forms.ModelForm):
    class Meta:
        model = TeamMember
        fields = '__all__'  # Tüm alanları dahil ediyoruz
        widgets = {
            'expertise_list': forms.Textarea(attrs={
                'rows': 3, 
                'placeholder': 'Uzmanlık alanlarını virgülle ayırarak girin'
            }),
            'slug': forms.TextInput(attrs={
                'readonly': 'readonly',
                'placeholder': 'Otomatik oluşturulacak'
            }),
        }
