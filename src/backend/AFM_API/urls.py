"""
URL configuration for AFM_API project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from django.contrib import admin
from django.urls import path
from .views import WaterLevelView, AccountView, ValidateEmailView, ValidateUserView

urlpatterns = [
    path('admin/', admin.site.urls),                            # Admin URL
    path('api/water-level/', WaterLevelView.as_view(), name='water-level'),  # Water level API endpoint
    path('api/accounts/', AccountView.as_view(), name='accounts'),
    path('api/accounts/validate-email/', ValidateEmailView.as_view(), name='validate-email'),
    path('api/accounts/validate-user/', ValidateUserView.as_view(), name='validate-user'),
]
