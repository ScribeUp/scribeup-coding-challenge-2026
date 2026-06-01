from django.urls import path

from . import views

urlpatterns = [
    path("users/", views.list_users),
    path("users/<int:user_id>/transactions/", views.list_user_transactions),
    # TODO (candidate): add the subscription detection endpoint here.
]
