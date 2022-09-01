from django.contrib import admin
from django.db.models import Count
from django.template.response import TemplateResponse
from .models import *
from django.utils.html import mark_safe
from django import forms
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from django.urls import path

# Register your models here.

class PostForm(forms.ModelForm):
    content = forms.CharField(widget=CKEditorUploadingWidget)

    class Meta:
        model = Post
        fields = '__all__'


class PostAdmin(admin.ModelAdmin):
    form = PostForm
    list_display = ['content','image','user']

class TagAdmin(admin.ModelAdmin):
    class Meta:
        model = Tag
        fields = '__all__'

    list_display = ['id','name']


class CommentAdmin(admin.ModelAdmin):
    class Meta:
        model = Comment
        fields = '__all__'

    list_display = ['content','user_id','post_id']


class LikeAdmin(admin.ModelAdmin):
    class Meta:
        model = Tag
        fields = '__all__'

    list_display = ['id','user_id', 'post_id', 'active_like']


admin.site.register(Post, PostAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(User)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Like, LikeAdmin)
