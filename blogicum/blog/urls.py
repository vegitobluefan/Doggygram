from django.urls import path

from blog import views

app_name = 'blog'

urlpatterns = [
    path('', views.PostListView.as_view(), name='index'),
    path('<int:post_id>/', views.PostDetailView.as_view(), name='post_detail'),
    path(
        '<slug:category_slug>/', views.CategoryPostsView.as_view(),
        name='category_posts'
    ),
    path('profile/<str:username>/', views.Profile.as_view(), name='profile'),
    path(
        'posts/<int:post_id>/comment/',
        views.CommentCreateView.as_view(),
        name='comment'
    ),
    path(
        'posts/<int:post_id>/edit_comment/<int:comment_id>/',
        views.CommentEditView.as_view(),
        name='comment_edit'
    ),
    path(
        'posts/create/', views.PostCreateView.as_view(),
        name='create_post'
    ),
]
