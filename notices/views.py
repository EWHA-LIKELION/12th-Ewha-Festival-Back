from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import views
from rest_framework.status import *
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .models import *
from booths.models import * 
from manages.storages import FileUpload, s3_client
from .serializers import *
from rest_framework.pagination import PageNumberPagination
from .pagination import PaginationHandlerMixin
from .permissions import IsTFOrReadOnly

class TFPagination(PageNumberPagination):
    page_size = 5

class NoticeListView(views.APIView):
    serializer_class = NoticeSerializer
    pagination_class = TFPagination
    permission_classes = [IsTFOrReadOnly]

    def get(self, request):
        notices = Notice.objects.all().order_by('-created_at')
        paginator = self.pagination_class()
        notices_page = paginator.paginate_queryset(notices, request)
        serializer = self.serializer_class(notices_page, many=True)
        page_number = request.GET.get('page', 1)
        
        if notices.exists(): 
            total_items = Notice.objects.count()
            total_pages = paginator.page.paginator.num_pages
            view_count = len(serializer.data)

            return Response({'message': 'TF 공지 조회 성공','page': page_number,'total': total_items,'total_page': total_pages,'view': view_count,'data': serializer.data}, status=HTTP_200_OK)
        else: 
            return Response({'message': 'TF 공지 없음','page': page_number,'total': Notice.objects.count(),'total_page': paginator.page.paginator.num_pages,'view': 0,'data': serializer.data}, status=HTTP_200_OK)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save(user=request.user)
            return Response({'message': 'TF 공지 작성 성공', 'data': serializer.data}, status=HTTP_200_OK)
        else:
            return Response({'message': 'TF 공지 작성 실패', 'data': serializer.errors}, status=HTTP_400_BAD_REQUEST)


class NoticeDetailView(views.APIView):
    serializer_class = NoticeSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsTFOrReadOnly]


    def get_object(self, pk):
        notice = get_object_or_404(Notice, pk=pk)
        self.check_object_permissions(self.request, notice)

        return notice

    def get(self, request, pk):
        notice = self.get_object(pk=pk)
        serializer = self.serializer_class(notice)

        return Response({'message': 'TF 공지 상세 조회 성공', 'data': serializer.data})

    def put(self, request, pk):
        notice = self.get_object(pk=pk)
        serializer = self.serializer_class(data=request.data, instance=notice)

        if serializer.is_valid():
            serializer.save()
            return Response({'message' : 'TF 공지 수정 성공', 'data': serializer.data}, status = HTTP_200_OK)
        return Response({'message': 'TF 공지 수정 실패', 'data': serializer.errors}, status=HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        notice = self.get_object(pk=pk)
        notice.delete()

        return Response({'message': 'TF 공지 삭제 성공'}, status=HTTP_204_NO_CONTENT)


class EventListView(views.APIView):
    serializer_class = EventListSerializer
    permission_classes = [IsTFOrReadOnly]
    
    def get(self, request):
        day = request.query_params.get('day')
        if day:
            events = Event.objects.filter(days__day=day)
        else:
            events = Event.objects.all()

        serializer = self.serializer_class(events, many=True)

        return Response({'message': 'TF 이벤트 목록 조회 성공', 'data': serializer.data}, status=HTTP_200_OK)
    
class EventDetailView(views.APIView):
    serializer_class = EventDetailSerializer
    permission_classes = [IsTFOrReadOnly]
    def get_object(self, pk):
        event = get_object_or_404(Event, pk=pk)
        self.check_object_permissions(self.request, event)

        return event

    def get(self, request, pk):
        event = self.get_object(pk=pk)
        serializer = self.serializer_class(event)
        return Response({'message': 'TF 부스 상세 조회 성공', 'data': serializer.data})
    '''
    def patch(self, request, pk):
        event = self.get_object(pk)
        serializer = EventDetailSerializer(instance=event, data=request.data, partial=True)

        if 'thumnail' in request.data:
            file = request.FILES['thumnail']
            folder = f"{pk}_images"  
            file_url = FileUpload(s3_client).upload(file, folder)
            request.data['thumnail'] = file_url

        if serializer.is_valid():
            serializer.save()

            request_days = request.data.get('days', [])
            existing_days = event.days.all()

            for request_day in request_days:
                date = request_day.get('date')
                existing_day = existing_days.filter(date=date).first()

                if existing_day:
                    existing_day.start_time = request_day.get('start_time')
                    existing_day.end_time = request_day.get('end_time')
                    existing_day.save()
                else:
                    day_of_week = self.get_day_from_date(date) 
                    event.days.create(
                        date=date,
                        day=day_of_week,
                        start_time=request_day.get('start_time'),
                        end_time=request_day.get('end_time')
                    )

            return Response({'message': 'TF 부스 수정 성공', 'data': serializer.data}, status=HTTP_200_OK)
        else:
            return Response({'message': 'TF 부스 수정 실패', 'errors': serializer.errors}, status=HTTP_400_BAD_REQUEST)

    def get_day_from_date(self, date):
        date_day_mapping = {
            8: '수요일',
            9: '목요일',
            10: '금요일'
        }
        return date_day_mapping.get(date)

'''