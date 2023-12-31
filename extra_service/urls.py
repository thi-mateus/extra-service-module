"""
URL configuration for extra_service project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
import debug_toolbar
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.defaults import permission_denied

from extra_service import views

urlpatterns = [

    # URLs de aplicativos
    path('', include('service_app.urls')),
    path('profile/', include('profile_app.urls')),
    path('request/', include('request_app.urls')),
    path('ocorrencia/', include('ocorrencia.urls')),
    path('admin/', admin.site.urls),

    # TODO: Remover debug toolbar
    path('__debug__', include(debug_toolbar.urls)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler403 = permission_denied
handler404 = views.pagina_erro_404

urlpatterns += [
    path('<path:path>', views.pagina_erro_404, name='pagina_erro_404'),
]
