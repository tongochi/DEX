from django.urls import include, path
from rest_framework import routers
from .views import *

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('', MethodsView.as_view()),
    path('pools/', PoolView.as_view()),
    path('stakers/', StakerView.as_view()),
    path('nft/content/', NftView.as_view()),
    path('dev-points/', DeveloperPointsView.as_view()),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]
