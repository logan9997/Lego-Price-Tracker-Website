from App import views
from django.urls import path


urlpatterns = [
    path('', views.index, name="index"),
    path('item/<str:item_id>/', views.item, name="item"),
    path('trending/', views.trending, name="trending"),
    path('search/', views.search, name="search"),
    path('portfolio/<str:view>', views.portfolio, name="portfolio"),
    path('theme/<path:theme_path>', views.theme, name="theme"),
    path('login/', views.login, name="login"),
    path("logout/", views.logout, name="logout"),
    path('join/', views.join, name="join"),
]