import threading

from django.http import JsonResponse
from rest_framework.views import APIView

from journo__globals.function_mapper import do_crawl, do_parse, do_match, do_flow, do_upload
from journo__globals.models import SourceModel, JournoFlowModel, SourcePostcardMapperModel

crawl_tasker = {}
parse_tasker = {}
match_tasker = {}
upload_tasker = {}
flow_tasker = {}

def _is_source_exists(source) -> bool:
    instance = SourceModel.objects.filter(name=source)
    return instance.exists()

class GlobalCrawlAPI(APIView):
    def get(self, request, source):
        global crawl_tasker
        if source in crawl_tasker and crawl_tasker[source].is_alive():
            return JsonResponse("Already Running", safe=False)

        if not _is_source_exists(source):
            return JsonResponse("Source is not found", safe=False)

        crawl_tasker[source] = threading.Thread(
            target=lambda: do_crawl(
                source=source,
            )
        )
        crawl_tasker[source].start()
        return JsonResponse("Started", safe=False)


class GlobalParseAPI(APIView):
    def get(self, request, source):
        global parse_tasker
        if source in parse_tasker and parse_tasker[source].is_alive():
            return JsonResponse("Already Running", safe=False)

        if not _is_source_exists(source):
            return JsonResponse("Source is not found", safe=False)

        parse_tasker[source] = threading.Thread(
            target=lambda: do_parse(
                source=source,
            )
        )
        parse_tasker[source].start()
        return JsonResponse("Started", safe=False)


class GlobalMatchAPI(APIView):
    def get(self, request, source):
        global match_tasker
        if source in match_tasker and match_tasker[source].is_alive():
            return JsonResponse("Already Running", safe=False)

        if not _is_source_exists(source):
            return JsonResponse("Source is not found", safe=False)

        instance = SourceModel.objects.filter(name=source).get()

        match_tasker[source] = threading.Thread(
            target=lambda: do_match(
                source=source,
                score_threshold=instance.score_threshold
            )
        )
        match_tasker[source].start()
        return JsonResponse("Started", safe=False)


class GlobalUploadAPI(APIView):
    def get(self, request, source):
        global upload_tasker
        if source in upload_tasker and upload_tasker[source].is_alive():
            return JsonResponse("Already Running", safe=False)

        if not _is_source_exists(source):
            return JsonResponse("Source is not found", safe=False)

        instance = SourceModel.objects.filter(name=source).get()
        pcuser = SourcePostcardMapperModel.objects.filter(source=instance).get()

        upload_tasker[source] = threading.Thread(
            target=lambda: do_upload(
                source=source,
                pcuser_id=pcuser.production_user_id
            )
        )

        upload_tasker[source].start()
        return JsonResponse("Started", safe=False)


class GlobalFlowAPI(APIView):
    def get(self, request, source):
        if not _is_source_exists(source):
            return JsonResponse("Source is not found", safe=False)

        instance = SourceModel.objects.filter(name=source).get()

        global crawl_tasker, parse_tasker, match_tasker, flow_tasker
        if source in flow_tasker and flow_tasker[source].is_alive():
            return JsonResponse("Flow tasker is running, please wait for it to complete", safe=False)
        if source in crawl_tasker and crawl_tasker[source].is_alive():
            return JsonResponse("Crawl tasker is running, please wait for it to complete", safe=False)
        if source in parse_tasker and parse_tasker[source].is_alive():
            return JsonResponse("Parse tasker is running, please wait for it to complete", safe=False)
        if source in match_tasker and match_tasker[source].is_alive():
            return JsonResponse("Match tasker is running, please wait for it to complete", safe=False)

        flow = JournoFlowModel.objects.create(
            source=instance
        )

        flow_tasker[source] = threading.Thread(
            target=lambda: do_flow(flow, instance)
        )
        flow_tasker[source].start()
        return JsonResponse("Started", safe=False)
