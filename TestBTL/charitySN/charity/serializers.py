from rest_framework import serializers
from rest_framework.fields import SerializerMethodField
from rest_framework.serializers import ModelSerializer
from .models import *



class WritableSerializerMethodField(SerializerMethodField):
    def __init__(self, **kwargs):
        self.setter_method_name = kwargs.pop('setter_method_name', None)
        self.deserializer_field = kwargs.pop('deserializer_field')

        super().__init__(**kwargs)

        self.read_only = False

    def bind(self, field_name, parent):
        retval = super().bind(field_name, parent)
        if not self.setter_method_name:
            self.setter_method_name = f'set_{field_name}'

        return retval

    def get_default(self):
        default = super().get_default()

        return {
            self.field_name: default
        }

    def to_internal_value(self, data):
        value = self.deserializer_field.to_internal_value(data)
        method = getattr(self.parent, self.setter_method_name)
        return {self.field_name: self.deserializer_field.to_internal_value(method(value))}


class UserSerializer(serializers.ModelSerializer):
    avatar = WritableSerializerMethodField(source='avatar', deserializer_field=serializers.ImageField(use_url='users/%Y/%m'))

    # def get_avatar(self, obj):
    #     request = self.context.get('request')
    #     if obj.avatar and not obj.avatar.name.startswith("/static"):
    #         path = '/static/%s' % obj.avatar.name
    #
    #         return request.build_absolute_uri(path)

    def set_avatar(self, obj):
        return obj

    def get_avatar(self,obj):
        name = obj.avatar.name
        if name.startswith('static/'):
            path = '/%s' % name
        else:
            path = '/static/%s' % name

        return "http://127.0.0.1:8000" + path

    def create(self, validated_data):
        data = validated_data.copy()
        user = User(**data)
        user.set_password(user.password)
        user.save()

        return user

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name','username', 'password', 'email', 'avatar', 'is_superuser']
        extra_kwargs = {
            'password': {
                'write_only': True
            }
        }




class UserViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name',
                  'username', 'email',
                  'avatar']


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id','name']


class PostSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField(source='image')
    tags = TagSerializer(many=True)
    user = UserSerializer()

    def get_image(self, obj):
        request = self.context.get('request')
        if obj.image and not obj.image.name.startswith("/static"):
            path = '/static/%s' % obj.image.name

            return request.build_absolute_uri(path)

    class Meta:
        model = Post
        fields = ['id','content','image','user','tags']


class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Comment
        fields = ['id','content','user','post', 'created_date']


class CreateCommentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Comment
        fields = ['content','user','post']


class AuctionInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuctionInfo
        fields = ['price','user','post']


class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = ['reason','post','user']


class TestCommentSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    class Meta:
        model = Comment
        fields = ['id','content','user']


class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ['user','post','active_like']


class CommentNotificationSerializer(serializers.ModelSerializer):

    class Meta:
        model = CommentNotification
        fields = ['receiver','post', 'count']


class AuctionInfoSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    post = PostSerializer()

    class Meta:
        model = AuctionInfo
        fields = ['user', 'post', 'price']


class AuctionWinnerSerializer(serializers.ModelSerializer):
    winner = UserSerializer()
    post = PostSerializer()

    class Meta:
        model = AuctionWinner
        fields = ['winner', 'post']


class AuctionLoserSerializer(serializers.ModelSerializer):
    loser = UserSerializer()
    post = PostSerializer()

    class Meta:
        model = AuctionLoser
        fields = ['post', 'loser']


class LikeNotificationSerializer(serializers.ModelSerializer):
    post = PostSerializer()
    receiver = UserSerializer()

    class Meta:
        model = LikeNotification
        fields = ['post','receiver','like_active']


class CountPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = CountPost
        fields = ['count','count_comment','count_like']


class CountPostDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = CountPostDetail
        fields = ['post', 'count_comment', 'count_like']


class UserStatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserStats
        fields = ['count_like','count_comment','count_post', 'user']





