from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from core.views import custom_404, custom_500
from cms.views import admin_media_upload

urlpatterns = [
    #path('admin/cms/media/upload/', admin_media_upload, name='admin_media_upload'),
    path('admin/', admin.site.urls),
    path('', include('users.urls')),
    path('cms/', include('cms.urls')),
    path('appl/', include('applications.urls')),
    path('', include('core.urls')),
    path('pages/', include('pages.urls', namespace='pages')),
    path('ckeditor/', include('ckeditor_uploader.urls')), 
    path('password-change/', auth_views.PasswordChangeView.as_view(
        template_name='users/password_change.html',
        success_url='/users/profile/'
    ), name='password_change'),
    path('password-change/done/', auth_views.PasswordChangeDoneView.as_view(
        template_name='users/password_change_done.html'
    ), name='password_change_done'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = 'core.views.custom_404'
handler500 = 'core.views.custom_500'