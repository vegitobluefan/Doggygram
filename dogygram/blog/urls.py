from django.urls import path

from blog import views

app_name = 'blog'

urlpatterns = [
    path(
        '',
        views.PostListView.as_view(),
        name='index'
    ),
    path(
        '<slug:category_slug>/',
        views.CategoryPostsView.as_view(),
        name='category_posts'
    ),
    path(
        'profile/edit',
        views.ProfieEditView.as_view(),
        name='edit_profile'
    ),
    path(
        'profile/<str:username>/',
        views.Profile.as_view(),
        name='profile'
    ),
    path(
        'posts/<int:post_id>/comment/',
        views.CommentCreateView.as_view(),
        name='add_comment'
    ),
    path(
        'posts/<int:post_id>/edit_comment/<int:comment_id>/',
        views.CommentEditView.as_view(),
        name='edit_comment'
    ),
    path(
        'posts/<int:post_id>/delete_comment/<int:comment_id>/',
        views.CommentDeleteView.as_view(),
        name='delete_comment'
    ),
    path(
        'posts/create/',
        views.PostCreateView.as_view(),
        name='create_post'
    ),
    path(
        'posts/<int:post_id>/edit/',
        views.PostEditView.as_view(),
        name='edit_post'
    ),
    path(
        'posts/<int:post_id>/delete/',
        views.PostDeleteView.as_view(),
        name='delete_post'
    ),
    path(
        'posts/<int:post_id>/',
        views.PostDetailView.as_view(),
        name='post_detail'
    ),
]