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
    # path('', views.view_picks3, name='view_picks3'),
    # path('week1/', views.view_picks, name='view_picks'),
    # path('week2/', views.view_picks2, name='view_picks2'),
    # path('sb_pick/', views.view_picks3, name='view_picks3'),
    path('update_picks', views.update_picks, name='update_picks'),
    # path('update_picks2', views.update_picks2, name='update_picks2'),
    # path('update_picks3', views.update_picks3, name='update_picks3'),
    path('edit/', views.edit_picks, name='edit_picks'),
    path('results/', views.results, name='results'),
    # path('results_week1/', views.results, name='results'),
    # path('results_week2/', views.results_week2, name='results_week2'),
    # path('results/', views.results_sb, name='results_sb'),
    path('alternate_view', views.alternate_view, name='alternate_view'),
    path('round2test1/', views.round2test1, name='round2test1'),
    path('round2test2/', views.round2test2, name='round2test2'),
    path('sbtest/', views.sbtest, name='sbtest'),
    path('nfl/', views.nfl, name='nfl'),
    path('bjcp/', views.bjcp, name='bjcp'),
]
