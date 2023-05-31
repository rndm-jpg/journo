from django.http import JsonResponse
from rest_framework.views import APIView

from journo__globals.models import JournoFlowModel, JournoPageModel, JournoPlaceModel

class FlowListAPIView(APIView):
    def get(self, request):
        limit = int(request.GET.get("limit", "10"))
        page = int(request.GET.get("page", "1"))
        flows = JournoFlowModel.objects.filter().order_by("-createdAt")
        flows = flows[(page - 1) * limit:page * limit]

        data = []
        for flow in flows:
            data.append(
                {
                    "id": flow.id,
                    "source": flow.source.name,
                    "createdAt": flow.createdAt,
                    "pages": {
                        "success": JournoPageModel.objects.filter(flow=flow, ignoredAt__isnull=True).count(),
                        "ignored": JournoPageModel.objects.filter(flow=flow, ignoredAt__isnull=False).count()
                    },
                    "places": {
                        "success": JournoPlaceModel.objects.filter(page__flow=flow, ignoredAt__isnull=True).count(),
                        "ignored": JournoPlaceModel.objects.filter(page__flow=flow, ignoredAt__isnull=False).count()
                    }
                }
            )

        return JsonResponse({
            "page": page,
            "limit": limit,
            "data": data,
        }, safe=False)


class FlowRetrieveAPIView(APIView):
    def get(self, request, flow_id):
        flow = JournoFlowModel.objects.filter(
            id=flow_id
        ).get()

        data = []

        pages = JournoPageModel.objects.filter(
            flow=flow
        )

        for page in pages:
            page_data = {
                "url": page.url,
                "true_url": page.true_url,
                "title": page.title,
                "ignored_reason": page.ignored_reason
            }

            success_place_count = JournoPlaceModel.objects.filter(
                page=page,
                ignoredAt__isnull=True
            ).count()

            ignored_place_count = JournoPlaceModel.objects.filter(
                page=page,
                ignoredAt__isnull=False
            ).count()

            page_data['places'] = {
                "success": success_place_count,
                "ignored": ignored_place_count
            }

            data.append(page_data)

        return JsonResponse({
            "id": flow.id,
            "createdAt": flow.createdAt,
            "source": flow.source.name,
            "pages": data
        }, safe=False)


class ListPlacesByFlowId(APIView):
    def get(self, request, flow_id):
        limit = int(request.GET.get("limit", "10"))
        page = int(request.GET.get("page", "1"))
        places = JournoPlaceModel.objects.filter(
            page__flow_id=flow_id,
        )

        return JsonResponse({
            "page": page,
            "limit": limit,
            "data": [x.jsonified_full(with_gmap=True) for x in places[(page - 1) * limit:page * limit]]
        }, safe=False)


class PagesRetrieveAPIView(APIView):
    def get(self, request):
        url = request.GET.get('url', False)
        if not url:
            return JsonResponse({
                "message": "not found"
            })

        page = JournoPageModel.objects.filter(url=url).get()

        page_data = {
            "source": page.source.name,
            "url": page.url,
            "true_url": page.true_url,
            "createdAt": page.createdAt,
            "parsedAt": page.parsedAt,
            "ignoredAt": page.ignoredAt,
            "ignored_reason": page.ignored_reason,
            "flow": page.flow.id,
            "title": page.title,
            "description": page.description,
            "locations": page.locations,
            "externalAttribution": page.externalAttribution,
            "externalPublishedAt": page.externalPublishedAt,
            "excerpt": page.excerpt,
            "media": page.media,
            "page_data": page.page_data,
        }

        places = JournoPlaceModel.objects.filter(page=page)

        page_data['places'] = [place.jsonified_full(with_gmap=True) for place in places]

        return JsonResponse(page_data, safe=False)


class PlaceRetrieveAPIView(APIView):
    def get(self, request, place_id):
        place = JournoPlaceModel.objects.filter(id=place_id).get()

        return JsonResponse(place.jsonified_full(with_gmap=True), safe=False)
