from django.urls import include, path

urlpatterns = [
    path("", include("subscriptions.urls")),
]
