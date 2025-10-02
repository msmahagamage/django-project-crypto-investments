from django.urls import path
from . import views


urlpatterns = [
    path("", views.list_investments, name="list"),
    path("create/", views.create_investment, name="create"),
    path("<int:pk>/", views.investment_detail, name="detail"),
    path("<int:pk>/edit/", views.edit_investment, name="edit"),
    path("<int:pk>/delete/", views.delete_investment, name="delete"),
]
