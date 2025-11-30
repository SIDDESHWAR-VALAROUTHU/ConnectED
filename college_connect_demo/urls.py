from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.conf import settings
from django.conf.urls.static import static


def redirect_to_login(request):
    # Use the namespace to avoid "NoReverseMatch"
    return redirect('accounts:login')


urlpatterns = [
    path('admin/', admin.site.urls),
    
    path('', redirect_to_login, name='redirect_to_login'),
    path('accounts/', include(('accounts.urls', 'accounts'), namespace='accounts')),
    path('chat/', include('chat.urls', namespace='chat')),
    path('network/', include(('network.urls', 'network'), namespace='network')),
    path('jobs/', include(('jobs.urls', 'jobs'), namespace='jobs')),
    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
