from App import views
from django.urls import path


urlpatterns = [
    path('', views.index, name="index"),
    path('item/<str:item_id>/', views.item, name="item"),
    path('trending/', views.trending, name="trending"),
    path('search/<path:theme_path>', views.search, name="search"),
    path('portfolio/', views.portfolio, name="portfolio"),
    path("portfolio_POST/<int:page>", views.portfolio_POST, name="portfolio_POST"),
    path("watchlist/", views.watchlist, name="watchlist"),
    path('login/', views.login, name="login"),
    path("logout/", views.logout, name="logout"),
    path('join/', views.join, name="join"),
]