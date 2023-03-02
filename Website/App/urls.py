from App import views
from django.urls import path


urlpatterns = [
    path('', views.index, name="index"),
    path('search_item/<path:current_view>/', views.search_item, name="search_item"),
    path('item/<str:item_id>/', views.item, name="item"),
    path('trending/', views.trending, name="trending"),
    path('search/', views.search, name="search"),
    path('search/<path:theme_path>/', views.search, name="search"),
    path('portfolio/', views.portfolio, name="portfolio"),
    path('view_POST/<str:view>', views.view_POST, name="view_POST"),
    path("watchlist/", views.watchlist, name="watchlist"),
    path("add_to_user_items/<str:item_id>", views.add_to_user_items, name="add_to_user_items"),
    path('login/', views.login, name="login"),
    path("logout/", views.logout, name="logout"),
    path('join/', views.join, name="join"),
    path('profile/', views.profile, name="profile"),
]