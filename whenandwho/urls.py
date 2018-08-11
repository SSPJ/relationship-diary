# Relationship Diary, Seamus Johnston, 2018, GPLv3
from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.RecordListView.as_view(), name="index"),
    path('category/<category>/', views.RecordListView.as_view(), name="index"),
    path('detail/<int:pk>', views.RecordDetailView.as_view(), name="detail"),
    path('edit/<int:pk>', views.record_edit_view, name="edit"),
    path('create/', views.record_create_view, name="create"),
    path('delete/<int:pk>', views.RecordDeleteView.as_view(), name="delete"),
    path('download', views.download, name="download"),
    path('api/v1/water/<int:pk>', views.water, name="water"),
    path('api/v1/note/create/<int:pk>', views.create_note, name="create_note"),
    path('api/v1/quick_add', views.quick_add, name="quick_add"),
    path('api/v1/populate', views.populate, name="populate"),
    path('admin/', admin.site.urls),
    # path('',include('api.urls')),
]
