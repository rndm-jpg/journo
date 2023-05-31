from django.urls import path

from journo__globals.apis import GlobalCrawlAPI, GlobalParseAPI, GlobalMatchAPI, GlobalFlowAPI, GlobalUploadAPI

urlpatterns = [
    path('crawl/<str:source>/', GlobalCrawlAPI.as_view()),
    path('parse/<str:source>/', GlobalParseAPI.as_view()),
    path('match/<str:source>/', GlobalMatchAPI.as_view()),
    path('upload/<str:source>/', GlobalUploadAPI.as_view()),
    path('flow/<str:source>/', GlobalFlowAPI.as_view()),
]
