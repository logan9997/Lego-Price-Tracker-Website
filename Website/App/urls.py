from App import views
from django.urls import path


urlpatterns = [
    path('', views.index, name="index"),
    path('item/<str:item_id>/', views.item, name="item"),
    path('trending/', views.trending, name="trending"),
]