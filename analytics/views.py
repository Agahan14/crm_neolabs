from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models.functions import ExtractYear
from django.db.models import Count, F
from applications.models import Application


class RejectionReasonAnalyticsView(APIView):
    def get(self, request, year):
        rejection_reason_analytics = (
            Application.objects.annotate(year=ExtractYear('created_at'))
            .values(
                'year',
                title=F('rejection_reason__title'),
                color=F('rejection_reason__color'),
            )
            .filter(year=year, transaction=False)
            .annotate(amount=Count('id'))
            .order_by('year', 'rejection_reason__title')
        )
        response_data = {'result': rejection_reason_analytics}

        response_data['total_amount'] = Application.objects\
            .filter(created_at__year=year, transaction=False).\
            aggregate(total=Count('id')).get('total')

        return Response(response_data)


class SourceAnalyticsView(APIView):
    def get(self, request, year):
        source_analytics = (
            Application.objects.annotate(year=ExtractYear('created_at'))
            .values(
                'year',
                source_title=F('source__name'),
                color=F('source__color'),
            )
            .filter(year=year, transaction=True)
            .annotate(amount=Count('id'))
            .order_by('year', 'source__name')
        )
        response_data = {'result': source_analytics}

        response_data['total_amount'] = Application.objects \
            .filter(created_at__year=year, transaction=True). \
            aggregate(total=Count('id')).get('total')

        return Response(response_data)


class GroupsAnalyticsView(APIView):
    def get(self, request, year):
        groups_analytics = (
            Application.objects.annotate(year=ExtractYear('created_at'))
            .values(
                'year',
                direction_name=F('groups__direction__name'),
                color=F('groups__direction__color'),
            )
            .filter(year=year, transaction=True)
            .annotate(amount=Count('id'))
            .order_by('year', 'groups__direction__name')
        )

        response_data = {'result': groups_analytics}

        response_data['total_amount'] = Application.objects \
            .filter(created_at__year=year, transaction=True). \
            aggregate(total=Count('id')).get('total')

        return Response(response_data)
