from App import views
from django.urls import path


urlpatterns = [
    path('', views.index, name="index"),
    path('minifig_page/<str:minifig_id>/', views.minifig_page, name="minifig_page"),
    path('trending/', views.trending, name="trending"),
]