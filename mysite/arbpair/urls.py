from django.urls import path
from arbpair.views import *

urlpatterns =[
    path('analyze_stocks/', analyze_stocks, name='analyze_stocks'),
]