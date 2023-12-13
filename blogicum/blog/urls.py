from django.urls import path

from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.index, name='index'),
    path('posts/<int:post_id>/', views.post_detail, name='post_detail'),
    path('category/<slug:category_slug>/', views.category_posts,
         name='category_posts'),
    path('posts/create/', views.todo_create, name='create_post'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/<slug:username>', views.ProfileListView.as_view(), name='profile'),
]
