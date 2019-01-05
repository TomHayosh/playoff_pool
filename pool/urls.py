"""playoff_pool URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
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
from django.urls import path
from pool import views

urlpatterns = [
    path('new', views.new_picks, name='new_picks'),
    path('', views.view_picks, name='view_picks'),
    path('update_picks', views.update_picks, name='update_picks'),
    path('edit/', views.edit_picks, name='edit_picks'),
    path('results/', views.results, name='results'),
    path('alternate_view', views.alternate_view, name='alternate_view')
]
