from datetime import datetime

import pytz
from django.db import models
from django.dispatch import receiver

from utils.pretty_printer import print_danger, print_success


class SourceModel(models.Model):
    name = models.CharField(max_length=255, primary_key=True)
    score_threshold = models.FloatField(default=0.5)

    class Meta:
        db_table = 'journo__source'

    def __str__(self):
        return self.name


class SourcePostcardMapperModel(models.Model):
    source = models.OneToOneField(to=SourceModel, on_delete=models.CASCADE, primary_key=True)
    production_user_id = models.CharField(max_length=255)
    development_user_id = models.CharField(max_length=255)

    class Meta:
        db_table = 'journo__source_to_postcard'

    def __str__(self):
        return f"{self.source} - {self.development_user_id} (dev) / {self.production_user_id} (dev)"


class JournoFlowModel(models.Model):
    source = models.ForeignKey(to=SourceModel, on_delete=models.CASCADE)
    createdAt = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'journo__flow'


class JournoPageModel(models.Model):
    source = models.ForeignKey(to=SourceModel, on_delete=models.CASCADE)
    url = models.CharField(unique=True, primary_key=True, max_length=255)
    true_url = models.CharField(null=True, default=None, max_length=255)

    createdAt = models.DateTimeField(auto_now_add=True)
    parsedAt = models.DateTimeField(null=True, default=None)

    ignoredAt = models.DateTimeField(null=True, default=None)
    ignored_reason = models.TextField(null=True, default=None)

    flow = models.ForeignKey(to=JournoFlowModel, on_delete=models.CASCADE, null=True, default=None)

    title = models.TextField(null=True, default=None)
    description = models.TextField(null=True, default=None)
    locations = models.JSONField(null=True, default=None)
    externalAttribution = models.CharField(null=True, default=None, max_length=255)
    externalPublishedAt = models.DateTimeField(null=True, default=None)
    excerpt = models.TextField(null=True, default=None)
    media = models.JSONField(null=True, default=None)

    page_data = models.JSONField(null=True, default=None)

    class Meta:
        db_table = 'journo__page'

    def set_true_url(self, true_url):
        self.true_url = true_url
        self.save()

    def set_parsed(self, new_data=None):
        self.parsedAt = datetime.utcnow().replace(tzinfo=pytz.utc)
        self.page_data = new_data
        self.save()

    def set_ignored(self, reasoning):
        print_danger("Ignored", f"{reasoning}, {self.url}")
        self.ignoredAt = datetime.utcnow().replace(tzinfo=pytz.utc)
        self.ignored_reason = reasoning
        self.save()

class JournoPlaceModel(models.Model):
    page = models.ForeignKey(to=JournoPageModel, on_delete=models.CASCADE)

    placeId = models.TextField(null=True, default=None)
    name = models.TextField()
    description = models.TextField(null=True, default=None)
    excerpt = models.TextField(null=True, default=None)
    media = models.JSONField(null=True, default=None)
    externalAttribution = models.TextField(null=True, default=None)
    externalPublishedAt = models.DateTimeField(null=True, default=None)
    urlTitle = models.TextField(null=True, default=None)
    url = models.URLField(null=True, default=None)

    lat = models.FloatField(null=True, default=None)
    long = models.FloatField(null=True, default=None)

    _extraData = models.JSONField(null=True, default=None)

    createdAt = models.DateTimeField(auto_now_add=True)

    matchedAt = models.DateTimeField(null=True, default=None)
    serp_query = models.TextField(null=True, default=None)

    ignoredAt = models.DateTimeField(null=True, default=None)
    ignoredReason = models.TextField(null=True, default=None)

    uploadedAt = models.DateTimeField(null=True, default=None)
    pc_upload_result = models.JSONField(null=True, default=None)
    mediaIds = models.JSONField(null=True, default=None)

    class Meta:
        db_table = 'journo__place'

    def set_ignored(self, reason):
        print_danger("Ignored", f"{reason}, {self.name}")
        self.ignoredAt = datetime.utcnow().replace(tzinfo=pytz.utc)
        self.ignoredReason = reason
        self.save()

    def set_matched(self):
        self.matchedAt = datetime.utcnow().replace(tzinfo=pytz.utc)
        self.save()

    def set_uploaded(self, new_data=None):
        self.uploadedAt = datetime.utcnow().replace(tzinfo=pytz.utc)
        self.pc_upload_result = new_data
        self.save()

    def get_extra(self):
        return self._extraData

    def set_extra(self, new_extra):
        self._extraData = new_extra

    def jsonified(self):
        return {
            "placeId": self.placeId,
            "name": self.name,
            "description": self.description,
            "excerpt": self.excerpt,
            "media": self.media,
            "mediaIds": self.mediaIds,
            "externalAttribution": self.externalAttribution,
            "externalPublishedAt": self.externalPublishedAt.isoformat() if self.externalPublishedAt is not None else None,
            "urlTitle": self.urlTitle,
            "url": self.url,
            "_extraData": self._extraData
        }

    def jsonified_full(self, with_gmap=False):
        data = {
            "id": self.id,
            "page_url": self.page.url,
            "placeId": self.placeId,
            "name": self.name,
            "description": self.description,
            "excerpt": self.excerpt,
            "media": self.media,
            "externalAttribution": self.externalAttribution,
            "externalPublishedAt": self.externalPublishedAt,
            "urlTitle": self.urlTitle,
            "url": self.url,
            "lat": self.lat,
            "long": self.long,
            "_extraData": self.get_extra(),
            "createdAt": self.createdAt,
            "matchedAt": self.matchedAt,
            "serp_query": self.serp_query,
            "ignoredAt": self.ignoredAt,
            "ignoredReason": self.ignoredReason,
            "uploadedAt": self.uploadedAt,
            "pc_upload_result": self.pc_upload_result,
            "mediaIds": self.mediaIds,
        }

        if not with_gmap:
            return data

        best_match = JournoSerpPlaceMatchModel.objects.filter(place=self)
        if not best_match:
            return data

        best_match = best_match.get()
        data_id = best_match.data_id
        rest_of_data = f"!4m5!3m4!1s{data_id}!8m2!3d{self.lat}!4d{self.long}"
        map_url = f"https://www.google.com/maps/place/{self.name}/@{self.lat},{self.long},18z/data={rest_of_data}"
        map_url = map_url.replace(" ", "+")
        data['gmaps'] = map_url

        return data


class JournoSerpPlaceMatchModel(models.Model):
    place = models.OneToOneField(to=JournoPlaceModel, on_delete=models.CASCADE)
    data_id = models.CharField(null=True, default=None, max_length=255)
    best_match = models.JSONField()
    score = models.FloatField()
    createdAt = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'journo__serp_place_match'


class SerpResultModel(models.Model):
    query_key = models.TextField(default=None, null=True)
    result_path = models.TextField(default=None, null=True)
    isWOF = models.BooleanField(default=False)
    wof_gids = models.JSONField(default=None, null=True)
    createdAt = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'journo__serp_result'


@receiver(models.signals.post_save, sender=JournoPageModel)
def execute_after_save(sender, instance, created, *args, **kwargs):
    if created:
        print_success("JournoPage Created", f"{instance.source} - {instance.url}")


@receiver(models.signals.post_save, sender=JournoPlaceModel)
def execute_after_save_pcplace(sender, instance, created, *args, **kwargs):
    if created:
        print_success("JournoPlace Created", f"{instance.page_id} - {instance.name}")
