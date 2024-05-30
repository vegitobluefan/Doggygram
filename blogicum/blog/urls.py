from django.urls import path

from blog import views

app_name = 'blog'

urlpatterns = [
    path('', views.PostListView.as_view(), name='index'),
    path('<int:post_id>/', views.post_detail, name='post_detail'),
    path('profile/<str:username>/', views.Profile.as_view(), name='profile'),
    path(
        '<slug:category_slug>/', views.CategoryPostsView.as_view(),
        name='category_posts'
    ),
]
