from django.urls import path, include
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register(prefix='users', viewset=views.UserViewSet, basename='user')
router.register(prefix='posts', viewset=views.PostViewSet, basename='post')
router.register(prefix='comments', viewset=views.CommentViewSet, basename='comment')
router.register(prefix='auctions', viewset=views.AuctionInfoViewSet, basename='auction')
router.register(prefix='comment_notifications', viewset=views.CommentNotificationViewSet, basename='comment_notification')
router.register(prefix='tags', viewset=views.TagViewSet, basename='tag')

urlpatterns = [
    path('', include(router.urls)),

]