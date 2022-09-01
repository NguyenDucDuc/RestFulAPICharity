import hashlib

from django.db.models import Sum
from rest_framework import viewsets, generics, status, permissions, mixins
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from .models import *
from .serializers import *
from drf_yasg.utils import swagger_auto_schema
from .paginators import *
from .perms import *


class UserViewSet(viewsets.ViewSet, generics.CreateAPIView, generics.ListAPIView, generics.RetrieveAPIView):
    queryset = User.objects.filter(is_active=True).order_by("-id")
    serializer_class = UserSerializer
    parser_classes = [MultiPartParser, ]

    # def create(self, request):
    #     first_name = request.data.get('first_name')
    #     last_name = request.data.get('last_name')
    #     username = request.data.get('username')
    #     password = request.data.get('password')
    #     password_bam = hashlib.sha256(str(password).encode('utf-8')).hexdigest()
    #     email = request.data.get('email')
    #     avatar = request.data.get('avatar')
    #     us = User.objects.create(first_name=first_name, last_name=last_name, username=username, password=password_bam, email=email, avatar=avatar)
    #
    #     return Response(UserSerializer(us, context={'request': request}).data, status=status.HTTP_200_OK)


    def get_permissions(self):
        if self.action in ['current_user']:
            return [permissions.IsAuthenticated()]
        if self.action in ["send-like-notification"]:
            return [permissions.IsAuthenticated()]

        return [permissions.AllowAny()]

    @action(methods=['get'], url_path="current-user", detail=False)
    def current_user(self, request):
        return Response(self.serializer_class(request.user, context={'request': request}).data,
                        status=status.HTTP_200_OK)

    @action(methods=['post'], url_path="send-notification", detail=True)
    def send_notification(self, request, pk):
        post_id = request.data.get('post_id')
        p = Post.objects.get(id=post_id)
        receiver = self.get_object()
        cn, _ = CommentNotification.objects.get_or_create(post=p, receiver=receiver)
        cn.count = cn.count + 1
        try:
            cn.save()
        except:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(data=CommentNotificationSerializer(cn, context={'request': request}).data,
                        status=status.HTTP_200_OK)

    @action(methods=['get'], url_path="get-notification", detail=True)
    def get_notification(self, request, pk):
        receiver = self.get_object()
        comment_nc = CommentNotification.objects.filter(receiver=receiver)
        if comment_nc:
            return Response(CommentNotificationSerializer(comment_nc, many=True).data, status=status.HTTP_200_OK)

        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(methods=['post'], url_path="send-auction-winner", detail=True)
    def add_auction_winner(self, request, pk):
        post_id = request.data.get('post_id')
        post = Post.objects.get(id=post_id)
        winner = self.get_object()
        auction_winner, _ = AuctionWinner.objects.get_or_create(post=post, winner=winner)
        try:
            auction_winner.save()
        except:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(data=AuctionWinnerSerializer(auction_winner, context={'request': request}).data,
                        status=status.HTTP_200_OK)

    @action(methods=['get'], url_path="get-auction-winner", detail=True)
    def get_auction_winner(self, request, pk):
        winner = self.get_object()
        auction_winner = AuctionWinner.objects.filter(winner=winner)
        if auction_winner:
            return Response(AuctionWinnerSerializer(auction_winner,context={'request': request}, many=True).data, status=status.HTTP_200_OK)

        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(methods=['post'], url_path="add-auction-loser", detail=True)
    def add_auction_loser(self, request, pk):
        loser = self.get_object()
        post_id = request.data.get('post_id')
        post = Post.objects.get(id=post_id)
        auction_loser, _ = AuctionLoser.objects.get_or_create(post=post, loser=loser)
        try:
            auction_loser.save()
        except:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(data=AuctionLoserSerializer(auction_loser, context={'request': request}).data,
                        status=status.HTTP_200_OK)

    @action(methods=['get'], url_path="get-auction-loser", detail=True)
    def get_auction_loser(self, request, pk):
        loser = self.get_object()
        auction_loser = AuctionLoser.objects.filter(loser=loser)
        if auction_loser:
            return Response(AuctionLoserSerializer(auction_loser, context={'request': request}, many=True).data, status=status.HTTP_200_OK)

        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(methods=['post'], url_path="send-like-notification", detail=True)
    def send_like_notification(self, request, pk):
        receiver = self.get_object()
        post_id = request.data.get('post_id')
        post = Post.objects.get(id=post_id)
        l, _ = LikeNotification.objects.get_or_create(receiver=receiver, post=post)
        l.like_active = not l.like_active
        try:
            l.save()
        except:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(data=LikeNotificationSerializer(l, context={'request': request}).data,
                        status=status.HTTP_201_CREATED)

    @action(methods=['get'], url_path="get-like-notification", detail=True)
    def get_like_notification(self, request, pk):
        receiver = self.get_object()
        like_notification = LikeNotification.objects.filter(receiver=receiver, like_active=True).order_by("-id")
        if like_notification:
            return Response(data=LikeNotificationSerializer(like_notification, context={'request': request}, many=True).data,
                            status=status.HTTP_200_OK)

        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(methods=['get'], url_path="user-stats", detail=True)
    def get_stats_user(self, request, pk):
        user = self.get_object()
        count_like = LikeNotification.objects.filter(receiver=user, like_active=True).count()
        post = Post.objects.filter(user=user)
        count = 0
        for p in post:
            count = count + p.comments.all().count()

        count_post = Post.objects.filter(user=user).count()
        user_stats, _ = UserStats.objects.get_or_create(user=user, count_like=count_like, count_post=count_post, count_comment=count)
        try:
            user_stats.save()
        except:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(UserStatsSerializer(user_stats,context={'request': request}).data, status=status.HTTP_200_OK)




class PostViewSet(viewsets.ViewSet, generics.ListAPIView, generics.CreateAPIView, generics.UpdateAPIView, generics.DestroyAPIView, generics.RetrieveAPIView):
    queryset = Post.objects.filter(active=True)
    pagination_class = PostPaginator
    serializer_class = PostSerializer

    def get_queryset(self):
        q = self.queryset
        kw = self.request.query_params.get('kw')
        if kw:
            q = q.filter(content__icontains=kw)

        return q

    def get_permissions(self):
        if self.action in ["add_comment","like", "create", "add_auction_info","report"]:
            return [permissions.IsAuthenticated()]
        if self.action in ['destroy','update','update_post']:
            return [PostOwnerPerms()]

        return [permissions.AllowAny()]

    @action(methods=['post'], url_path='add-post', detail=False)
    def add_post(self, request):
        content = request.data.get('content')
        user = request.user
        image = request.data.get('image')
        tag_arr = request.data.get('tag_arr')

        if content:
            p = Post.objects.create(content=content, user=user, image=image)
        if tag_arr:
            tag_arr = tag_arr.split(",")
            for tag in tag_arr:
                t, _ = Tag.objects.get_or_create(name=tag)
                p.tags.add(t)
        return Response(PostSerializer(p, context={'request': request}).data, status=status.HTTP_200_OK)

        #return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['patch'], url_path='update-post', detail=True)
    def update_post(self, request, pk):
        post = self.get_object()
        content = request.data.get('content')
        image = request.data.get('image')
        tags = request.data.get('tags')

        #p = post.objects.update(content=content, image=image)
        if content:
            post.content = content
        if image not in ['undefined']:
            post.image = image
        if tags:
            tags = tags.split(",")
            post.tags.all().delete()
            for tag in tags:
                t, _ = Tag.objects.get_or_create(name=tag)
                post.tags.add(t)
        try:
            post.save()
        except:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(PostSerializer(post,context={'request': request}).data, status=status.HTTP_200_OK)

    @action(methods=['get'], url_path='comments', detail=True)
    def get_comments(self, request, pk):
        post = self.get_object()
        comments = post.comments.select_related('user').filter(active=True)

        return Response(CommentSerializer(comments,context={'request': request}, many=True).data,
                        status=status.HTTP_200_OK)

    @action(methods=['post'], url_path='like', detail=True)
    def like(self, request, pk):
        post = self.get_object()
        user = request.user
        p, _ = Like.objects.get_or_create(post=post, user=user)
        p.active_like = not p.active_like
        try:
            p.save()
        except:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(data=LikeSerializer(p, context={'request': request}).data,
                        status=status.HTTP_200_OK)

    @action(methods=['post'], url_path='report', detail=True)
    def report(self, request, pk):
        post = self.get_object()
        user = request.user
        reason = request.data.get('reason')
        if reason:
            rp, _ = Report.objects.get_or_create(user=user, post=post, reason=reason)
        try:
            rp.save()
        except:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(data=ReportSerializer(rp, context={'request': request}).data,
                        status=status.HTTP_200_OK)

    @action(methods=['post'], url_path='add-comment', detail=True)
    def add_comment(self, request, pk):
        content = request.data.get('content')
        if content:
            c = Comment.objects.create(content=content, post=self.get_object(), user=request.user)
            return Response(CreateCommentSerializer(c, context={'request': request}).data, status=status.HTTP_201_CREATED)

        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['post'], url_path='add-auction', detail=True)
    def add_auction_info(self, request, pk):
        user = request.user
        post = self.get_object()
        price = float(request.data.get('price'))
        auction_info = AuctionInfo.objects.create(user=user, post=post, price=price)
        try:
            auction_info.save()
        except:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(AuctionInfoSerializer(auction_info, context={'request': request}).data, status=status.HTTP_201_CREATED)

    @action(methods=['get'], url_path='get-auction-info', detail=True)
    def get_auction_info(self, request, pk):
        try:
            post = self.get_object()
            auction_info = post.auction_info.filter(active=True)
        except:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(AuctionInfoSerializer(auction_info, context={'request': request}, many=True).data, status=status.HTTP_200_OK)

    @action(methods=['get'], url_path='stats', detail=False)
    def get_all_post(self, request):
        count = Post.objects.filter(active=True).count()
        count_comment = Comment.objects.filter(active=True).count()
        count_like = Like.objects.filter(active_like=True).count()
        cp, _ = CountPost.objects.get_or_create(count=count, count_comment=count_comment, count_like=count_like)
        try:
            cp.save()
        except:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(CountPostSerializer(cp).data, status=status.HTTP_200_OK)

    @action(methods=['get'], url_path='detail-stats', detail=True)
    def get_post_stats(self, request,pk):
        post = self.get_object()
        count_like = post.like.filter(active_like=True).count()
        count_comment = post.comments.filter(active=True).count()
        cpd, _ = CountPostDetail.objects.get_or_create(post=post, count_comment=count_comment, count_like=count_like)
        try:
            cpd.save()
        except:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(CountPostDetailSerializer(cpd).data, status=status.HTTP_200_OK)


class CommentViewSet(viewsets.ViewSet, generics.CreateAPIView):
    queryset = Comment.objects.filter(active=True).order_by("-id")
    serializer_class = CreateCommentSerializer


class AuctionInfoViewSet(viewsets.ViewSet, generics.CreateAPIView):
    queryset = AuctionInfo.objects.filter(active=True)
    serializer_class = AuctionInfoSerializer


class CommentNotificationViewSet(viewsets.ViewSet, generics.ListAPIView):
    queryset = CommentNotification.objects.filter(active=True)
    serializer_class = CommentNotificationSerializer


class TagViewSet(viewsets.ViewSet, generics.ListAPIView):
    queryset = Tag.objects.filter(active=True)
    serializer_class = TagSerializer



