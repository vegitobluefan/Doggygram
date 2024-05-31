from django.contrib import admin  # type: ignore
from django.conf import settings  # type: ignore
from django.contrib.auth.forms import UserCreationForm  # type: ignore
from django.views.generic.edit import CreateView  # type: ignore
from django.conf.urls.static import static  # type: ignore
from django.urls import include, path, reverse_lazy  # type: ignore

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('blog.urls', namespace='blog')),
    path('posts/', include('blog.urls', namespace='blog')),
    path('category/', include('blog.urls', namespace='blog')),
    path('pages/', include('pages.urls', namespace='pages')),
    path('auth/', include('django.contrib.auth.urls')),
    path(
        'auth/registration/',
        CreateView.as_view(
            template_name='registration/registration_form.html',
            form_class=UserCreationForm,
            success_url=reverse_lazy('blog:index'),
        ),
        name='registration',
    ),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += (path('__debug__/', include(debug_toolbar.urls)),)

handler404 = 'pages.views.page_not_found'
handler500 = 'pages.views.server_error_500'
