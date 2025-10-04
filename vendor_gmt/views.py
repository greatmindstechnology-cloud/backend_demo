from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import VendorInternship, VendorData,CSREvent,VendorData, VendorEvent,BloodNeed
from django.utils import timezone
from django.db.models import Count
from .serializers import CSREventSerializer,BloodNeedSerializer
from django.http import JsonResponse
from django.shortcuts import get_object_or_404



@api_view(['POST'])
def create_vendor_internship(request):
    try:
        # Get vendor_id from query parameters
        vendor_id = request.query_params.get('vendor_id')
        if not vendor_id:
            return Response({"error": "Missing vendor_id in query parameters."},
                            status=status.HTTP_400_BAD_REQUEST)
        try:
            vendor = VendorData.objects.get(id=vendor_id)
        except VendorData.DoesNotExist:
            return Response({"error": "Vendor not found."}, status=status.HTTP_404_NOT_FOUND)

        data = request.data

        internship = VendorInternship.objects.create(
            vendor=vendor,
            title=data.get('title', ''),
            description=data.get('description', ''),
            location=data.get('location', ''),
            mode=data.get('mode', ''),
            duration=data.get('duration', ''),
            start_date=data.get('start_date'),
            stipend=data.get('stipend', ''),
            skills_required=data.get('skills_required', []),
            eligibility_criteria=data.get('eligibility_criteria', ''),
            application_deadline=data.get('application_deadline'),
            number_of_openings=data.get('number_of_openings', 0),
            contact_info=data.get('contact_info', ''),
            category=data.get('category', ''),
            application_process=data.get('application_process', '')
        )

        return Response({
            "message": "Internship created successfully",
            "internship_id": internship.id
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({
            "error": "Something went wrong",
            "details": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def create_vendor_event(request):
    try:
        vendor_id = request.query_params.get('vendor_id')
        if not vendor_id:
            return Response({"error": "Missing vendor_id in query parameters."},
                            status=status.HTTP_400_BAD_REQUEST)
        try:
            vendor = VendorData.objects.get(id=vendor_id)
        except VendorData.DoesNotExist:
            return Response({"error": "Vendor not found."}, status=status.HTTP_404_NOT_FOUND)
        data = request.data
        event = VendorEvent.objects.create(
            vendor=vendor, 
            event_title=data.get('event_title', ''),
            description=data.get('description', ''),
            location=data.get('location', ''),
            event_date_time=data.get('event_date_time'),
            duration=data.get('duration', ''),
            event_type=data.get('event_type', ''),
            target_audience=data.get('target_audience', ''),
            capacity=data.get('capacity', 0),
            registration_deadline=data.get('registration_deadline'),
            registration_fee=data.get('registration_fee', ''),
            contact_information=data.get('contact_information', ''),
            category=data.get('category', ''),
            event_link=data.get('event_link', None),
        )

        return Response({
            "message": "Event created successfully",
            "event_id": event.id
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({
            "error": "Something went wrong",
            "details": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_all_vendor_internships(request):
    try:
        internships = VendorInternship.objects.all().values()
        return Response({'internships': list(internships)}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_all_vendor_events(request):
    try:
        events = VendorEvent.objects.all().values()
        return Response({'events': list(events)}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['PUT'])
def update_internship_status(request):
    try:
        internship_id = request.data.get('internship_id')
        new_status = request.data.get('status')

        if not internship_id:
            return Response({'success': False, 'error': 'Internship ID is required.'}, status=status.HTTP_400_BAD_REQUEST)

        if not new_status:
            return Response({'success': False, 'error': 'Status field is required.'}, status=status.HTTP_400_BAD_REQUEST)

        if new_status not in ['waiting', 'approved', 'rejected']:
            return Response({'success': False, 'error': 'Invalid status value.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            internship = VendorInternship.objects.get(id=internship_id)
        except VendorInternship.DoesNotExist:
            return Response({'success': False, 'error': 'Internship not found.'}, status=status.HTTP_404_NOT_FOUND)

        internship.status = new_status
        internship.updated_at = timezone.now()
        internship.save()

        return Response({
            'success': True,
            'message': 'Status updated successfully.',
            'data': {
                'id': internship.id,
                'status': internship.status
            }
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['PUT'])
def update_event_status(request):
    try:
        event_id = request.data.get('event_id')
        new_status = request.data.get('status')

        if not event_id:
            return Response({'success': False, 'error': 'Event ID is required.'}, status=status.HTTP_400_BAD_REQUEST)

        if not new_status:
            return Response({'success': False, 'error': 'Status field is required.'}, status=status.HTTP_400_BAD_REQUEST)

        if new_status not in ['waiting', 'approved', 'rejected']:
            return Response({'success': False, 'error': 'Invalid status value.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            event = VendorEvent.objects.get(id=event_id)
        except VendorEvent.DoesNotExist:
            return Response({'success': False, 'error': 'Event not found.'}, status=status.HTTP_404_NOT_FOUND)

        event.status = new_status
        event.updated_at = timezone.now()
        event.save()

        return Response({
            'success': True,
            'message': 'Event status updated successfully.',
            'data': {
                'id': event.id,
                'status': event.status
            }
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['GET'])
def internship_status_counts(request):
    try:
        counts = VendorInternship.objects.values('status').annotate(total=Count('id'))
        result = {'waiting': 0, 'approved': 0, 'rejected': 0}
        for entry in counts:
            result[entry['status']] = entry['total']

        return Response({'success': True, 'data': result}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
from .models import VendorEvent

@api_view(['GET'])
def event_status_counts(request):
    try:
        counts = VendorEvent.objects.values('status').annotate(total=Count('id'))

        result = {'waiting': 0, 'approved': 0, 'rejected': 0}
        for entry in counts:
            result[entry['status']] = entry['total']

        return Response({'success': True, 'data': result}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

 # your model

def get_internship_by_id(request,id):
    if request.method == 'GET':
        internship = get_object_or_404(VendorInternship, id=id)
        data = {
            'id': internship.id,
            'vendor_id': internship.vendor.id,
            'title': internship.title,
            'description': internship.description,
            'location': internship.location,
            'mode': internship.mode,
            'duration': internship.duration,
            'start_date': internship.start_date,
            'stipend': internship.stipend,
            'skills_required': internship.skills_required,
            'eligibility_criteria': internship.eligibility_criteria,
            'application_deadline': internship.application_deadline,
            'number_of_openings': internship.number_of_openings,
            'contact_info': internship.contact_info,
            'category': internship.category,
            'application_process': internship.application_process,
            'status': internship.status,
            'created_at': internship.created_at,
            'updated_at': internship.updated_at,
        }
        return JsonResponse(data, safe=False)
    return JsonResponse({'error': 'Only GET method allowed'}, status=405)


@api_view(['POST'])
def create_csrevent(request):
    serializer = CSREventSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(
            {"message": "CSR Event created successfully", "data": serializer.data},
            status=status.HTTP_201_CREATED
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@api_view(["GET"])
def get_all_events(request):
    events = CSREvent.objects.all()
    serializer = CSREventSerializer(events, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)



@api_view(["POST"])
def create_blood_need(request):
    serializer = BloodNeedSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(
            {"message": "Blood request created successfully", "data": serializer.data},
            status=status.HTTP_201_CREATED,
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
def get_all_blood_needs(request):
    blood_needs = BloodNeed.objects.all().order_by("created_at") 
    serializer = BloodNeedSerializer(blood_needs, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)



@api_view(["PATCH"])
def update_request_status(request, pk):
    try:
        blood_need = BloodNeed.objects.get(pk=pk)
    except BloodNeed.DoesNotExist:
        return Response({"error": "BloodNeed not found"}, status=status.HTTP_404_NOT_FOUND)

    new_status = request.data.get("request_status")
    if not new_status:
        return Response({"error": "request_status field is required"}, status=status.HTTP_400_BAD_REQUEST)

    blood_need.request_status = new_status
    blood_need.save()

    serializer = BloodNeedSerializer(blood_need)
    return Response({"message": "Request status updated successfully", "data": serializer.data}, status=status.HTTP_200_OK)





