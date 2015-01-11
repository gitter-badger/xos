from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework import serializers
from rest_framework import generics
from rest_framework.views import APIView
from core.models import *
from django.forms import widgets
from syndicate_storage.models import Volume

# This REST API endpoint contains a bunch of misc information that the
# tenant view needs to display

BLESSED_DEPLOYMENTS = ["ViCCI"] # ["US-MaxPlanck", "US-GeorgiaTech", "US-Princeton", "US-Washington", "US-Stanford"]


def getTenantViewDict():
    blessed_sites = []
    for site in Site.objects.all():
        good=False
        for deployment in site.deployments.all():
            if deployment.name in BLESSED_DEPLOYMENTS:
                good=True
        if good:
            blessed_sites.append(site)

    blessed_images=[]
    for image in Image.objects.all():
        good = False
        for deployment in image.deployments.all():
            if deployment.name in BLESSED_DEPLOYMENTS:
                 good=True
        if good:
            blessed_images.append(image)

    volumes=[]
    for volume in Volume.objects.all():
        if not volume.private:
            volumes.append(volume)

    return {"id": 0,
            "blessed_deployment_names": BLESSED_DEPLOYMENTS,
            "blessed_site_names": [site.name for site in blessed_sites],
            "blessed_sites": [site.id for site in blessed_sites],
            "blessed_image_names": [image.name for image in blessed_images],
            "blessed_images": [image.id for image in blessed_images],
            "public_volume_names": [volume.name for volume in volumes],
            "public_volumes": [volume.id for volume in volumes],
            }

class TenantList(APIView):
    method_kind = "list"
    method_name = "tenantview"

    def get(self, request, format=None):
        return Response( getTenantViewDict() )

class TenantDetail(APIView):
    method_kind = "detail"
    method_name = "tenantview"

    def get(self, request, format=None, pk=0):
        return Response( [getTenantViewDict()] )
