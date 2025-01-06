from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('otpVerify/', views.otpVerify, name='otpVerify'),
    path('oauth_Verification/', views.oauth_Verification, name='oauth_Verification'),
    path('createPassword/', views.createPassword, name='createPassword'),
    # path('home/', views.home, name='home'),
    path('login/', views.login, name='login'),
    path('addpost/', views.add_post, name='addpost'),
    path('like_post/<int:post_id>/', views.like_post, name='like_post'),
    path('dislike_post/<int:post_id>/', views.dislike_post, name='dislike_post'),
    path('post_detail/<int:post_id>/', views.post_detail, name='post_detail'),
    path('logout/', auth_views.LogoutView.as_view(next_page='index'), name='logout'),
    path('search_suggestions/', views.search_suggestions, name='search'),
    path('trending/', views.trending, name='trending'),
    path('add_comment/<int:post_id>/', views.add_comment, name='comments'),
    path('agree_comment/<int:comment_id>/', views.agree_comment, name='agree'),
    path('disagree_comment/<int:comment_id>/', views.disagree_comment, name='disagree'),
    path('bookmarks_post/<int:post_id>/', views.bookmark_post, name='bookmarks'),
    path('view_bookmarks/', views.view_bookmarks, name='view_bookmarks'),
    path('remove_bookmark/<int:bookmark_id>/', views.remove_bookmark, name='remove_bookmark'),
    # path('user_profile/<int:user_id>/', views.user_profile, name='user_profile'),
    path('user_profile/', views.user_profile, name='user_profile'),

]