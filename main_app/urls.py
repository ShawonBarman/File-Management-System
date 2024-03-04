from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('create_folder/', views.create_folder, name='create_folder'),
    path('upload_file/', views.upload_file, name='upload_file'),
    path('<str:folder_name>/<int:folder_id>/', views.open_folder, name='open_folder'),
    path('rename/', views.rename_item, name='rename_item'),
    path('delete/', views.delete_item, name='delete_item'),
    path('share_item/', views.share_item, name='share_item'),
    path('share_with_me/', views.share_with_me, name='share_with_me'),
    path('download/<str:item_type>/<int:item_id>/', views.download_item, name='download_item'),
    path('search_items/', views.search_items, name='search_items'),
]
