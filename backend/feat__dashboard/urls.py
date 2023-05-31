from django.urls import path

from feat__dashboard.apis import FlowListAPIView, FlowRetrieveAPIView, PagesRetrieveAPIView, PlaceRetrieveAPIView, \
    ListPlacesByFlowId

urlpatterns = [
    path('flow/', FlowListAPIView.as_view()),
    path('flow/page', PagesRetrieveAPIView.as_view()),
    path('flow/place/<str:place_id>', PlaceRetrieveAPIView.as_view()),
    path('flow/<str:flow_id>', FlowRetrieveAPIView.as_view()),
    path('flow/<str:flow_id>/places', ListPlacesByFlowId.as_view()),
]
