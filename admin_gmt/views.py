from django.shortcuts import render

from rest_framework.decorators import api_view,permission_classes,parser_classes
from rest_framework.response import Response
from signup_gmt.models import StudentInformation, VendorData, TrainerData
from django.core.exceptions import ObjectDoesNotExist
import json
from django.forms.models import model_to_dict
from django.db.models import Q
# from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes


@api_view(['GET'])
def get_all_students(request):
    try:
        students = StudentInformation.objects.all().values('id', 'firstname', 'email', 'contact_number', 'skills')
        return Response({'status': 'success', 'data': list(students)})
    except Exception as e:
        return Response({'status': 'error', 'message': str(e)}, status=500)

@api_view(['GET'])
def get_all_vendors(request):
    try:
        vendors = VendorData.objects.all().values('id', 'firstname', 'business_name', 'contact_email', 'contact_phone', 'gst_number','status')
        return Response({'status': 'success', 'data': list(vendors)})
    except Exception as e:
        return Response({'status': 'error', 'message': str(e)}, status=500)

@api_view(['GET'])
def get_all_trainers(request):
    try:
        trainers = TrainerData.objects.all().values('id', 'first_name', 'email', 'phone_number', 'total_experience_years','status')
        return Response({'status': 'success', 'data': list(trainers)})
    except Exception as e:
        return Response({'status': 'error', 'message': str(e)}, status=500)


@api_view(['GET'])
def get_student_details(request):
    try:
        student = None
        if 'id' in request.GET:
            student = StudentInformation.objects.get(id=request.GET['id'])
        elif 'email' in request.GET:
            student = StudentInformation.objects.get(email=request.GET['email'])
        else:
            return Response({'status': 'error', 'message': 'Provide student ID or email'}, status=400)

        data = {
            "id": student.id,
            "firstname": student.firstname,
            "lastname": student.lastname,
            "email": student.email,
            "date_of_birth": student.date_of_birth,
            "gender": student.gender,
            "contact_number": student.contact_number,
            "alt_contact": student.alt_contact,
            "father_name": student.father_name,
            "mother_name": student.mother_name,

            "door_number": student.door_number,
            "street_name": student.street_name, 
            "landmark":  student.landmark,
            "country": student.country,
            "state": student.state,
            "city": student.city,

            "pincode": student.pincode,
            "description": student.description,
            "designation": student.designation,
            "skills": student.skills,

            "account_holder_name": student.account_holder_name,
            "account_number": student.account_number,
            "bank_name": student.bank_name,
            "bank_location": student.bank_location,
            "branch_name": student.branch_name,
            "ifsc_code": student.ifsc_code,

            "institution_name": student.institution_name,
            "location": student.location,
            "major_subject": student.major_subject,
            "qualification": student.qualification,
            "cgpa": student.cgpa,
            "passedout": student.passedout,
            "profile_picture": student.profile_picture.url if student.profile_picture else None,
        }

        return Response({'status': 'success', 'data': data})

    except ObjectDoesNotExist:
        return Response({'status': 'error', 'message': 'Student not found'}, status=404)
    except Exception as e:
        return Response({'status': 'error', 'message': str(e)}, status=500)

@api_view(['GET'])
def get_trainer_details(request):
    try:
        trainer = None
        if 'id' in request.GET:
            trainer = TrainerData.objects.get(id=request.GET['id'])
        elif 'email' in request.GET:
            trainer = TrainerData.objects.get(email=request.GET['email'])
        else:
            return Response({'status': 'error', 'message': 'Provide trainer ID or email'}, status=400)

        data = {
            "id": trainer.id,
            "email": trainer.email,
            "first_name": trainer.first_name,
            "last_name": trainer.last_name,
            "date_of_birth": trainer.date_of_birth,
            "gender": trainer.gender,
            "phone_number": trainer.phone_number,
            "pincode":trainer.pincode,
            "highest_qualification": trainer.highest_qualification,
            "specialization": trainer.specialization,

            "door_number": trainer.door_number,
            "street_Name": trainer.street_name, 
            "landmark": trainer.landmark,
            "country": trainer.country,
            "state": trainer.state,
            "city": trainer.city,

            "total_experience_years": trainer.total_experience_years,
            "current_organization": trainer.current_organization,
            "previous_teaching_experience": trainer.previous_teaching_experience,
            "certifications": trainer.certifications,

            "account_holder_name": trainer.account_holder_name,
            "account_number": trainer.account_number,
            "ifsc_code": trainer.ifsc_code,
            "bank_name": trainer.bank_name,
            "bank_location": trainer.bank_location,
            "branch_name": trainer.branch_name,

            "available_days": trainer.available_days,
            "available_mode": trainer.available_mode,
            "preferred_time_slots": trainer.preferred_time_slots,
            "resume": trainer.resume.url if trainer.resume else None,
            "id_proof": trainer.id_proof.url if trainer.id_proof else None,
            "educational_certificates": trainer.educational_certificates.url if trainer.educational_certificates else None,
            "profile_picture": trainer.profile_picture.url if trainer.profile_picture else None,
        }

        return Response({'status': 'success', 'data': data})
    except ObjectDoesNotExist:
        return Response({'status': 'error', 'message': 'Trainer not found'}, status=404)
    except Exception as e:
        return Response({'status': 'error', 'message': str(e)}, status=500)
    

@api_view(['GET'])
def get_vendor_details(request):
    try:
        vendor = None
        if 'id' in request.GET:
            vendor = VendorData.objects.get(id=request.GET['id'])
        elif 'email' in request.GET:
            vendor = VendorData.objects.get(contact_email=request.GET['email'])
        else:
            return Response({'status': 'error', 'message': 'Provide vendor ID or email'}, status=400)

        data = {
            "id": vendor.id,
            "firstname":vendor.firstname,
            "lastname":vendor.lastname,
            "business_name": vendor.business_name,
            "business_type": vendor.business_type,
            "gst_number": vendor.gst_number,
            "registration_number": vendor.registration_number,
            "year_of_establishment": vendor.year_of_establishment,
            "contact_email": vendor.contact_email,
            "contact_phone": vendor.contact_phone,
            "alternate_contact": vendor.alternate_contact,

            "door_number": vendor.door_number,
            "street_Name": vendor.street_name, 
            "landmark": vendor.landmark,
            "country": vendor.country,
            "state": vendor.state,
            "city": vendor.city,
            "pincode":vendor.pincode,

            "account_holder_name": vendor.account_holder_name,
            "account_number": vendor.account_number,
            "ifsc_code": vendor.ifsc_code,
            "bank_name": vendor.bank_name,
            "bank_location": vendor.bank_location,
            "branch_name": vendor.branch_name,

            "events_type": vendor.events_type,
            "event_history": vendor.event_history,
            "gst_certificate": vendor.gst_certificate.url if vendor.gst_certificate else None,
            "business_license": vendor.business_license.url if vendor.business_license else None,
            "pan_card": vendor.pan_card.url if vendor.pan_card else None,
            "profile_picture": vendor.profile_picture.url if vendor.profile_picture else None,
        }

        return Response({'status': 'success', 'data': data})
    except ObjectDoesNotExist:
        return Response({'status': 'error', 'message': 'Vendor not found'}, status=404)
    except Exception as e:
        return Response({'status': 'error', 'message': str(e)}, status=500)

@api_view(['PUT'])
@parser_classes([MultiPartParser, FormParser])
def update_student(request):
    try:
        data = request.data
        query_params = request.query_params
        student = None
        student_id = data.get('id') or query_params.get('id')
        student_email = data.get('email') or query_params.get('email')

        if student_id:
            student = StudentInformation.objects.get(id=student_id)
        elif student_email:
            student = StudentInformation.objects.get(email=student_email.strip())
        else:
            return Response({'status': 'error', 'message': 'Provide student ID or email'}, status=400)

        updatable_fields = [
             'date_of_birth', 'address', 'firstname', 'lastname', 'email', 'contact_number',
            'alt_contact', 'father_name', 'mother_name', 'pincode', 'description', 'designation',
            'gender', 'skills', 'account_holder_name', 'account_number', 'bank_location', 'bank_name',
            'branch_name', 'ifsc_code', 'institution_name', 'location', 'major_subject',
            'qualification', 'total_score', 'passedout',"door_number","street_name", "landmark","country",
            "state","city"
        ]

        for field in updatable_fields:
            if field in data:
                setattr(student, field, data.get(field))

        if 'profile_picture' in request.FILES:
            student.profile_picture = request.FILES['profile_picture']

        student.save()

        return Response({'status': 'success', 'message': 'Student updated successfully'})

    except StudentInformation.DoesNotExist:
        return Response({'status': 'error', 'message': 'Student not found'}, status=404)
    except Exception as e:
        return Response({'status': 'error', 'message': str(e)}, status=500)


@api_view(['PUT'])
@parser_classes([MultiPartParser, FormParser])
def update_vendor(request):
    try:
        data = request.data
        query_params = request.query_params
        vendor = None

        vendor_id = data.get('id') or query_params.get('id')
        vendor_email = data.get('email') or query_params.get('email')

        if vendor_id:
            vendor = VendorData.objects.get(id=vendor_id)
        elif vendor_email:
            vendor = VendorData.objects.get(email=vendor_email.strip())
        else:
            return Response({'status': 'error', 'message': 'Provide vendor ID or email'}, status=400)

        updatable_fields = [
            "firstname","lastname","business_name", "business_type", "gst_number", "registration_number",
            "year_of_establishment", "contact_email", "contact_phone", "alternate_contact",
            "address","pincode","country", "account_holder_name","bank_name_branch","account_number","ifsc_code",
            "events_type","event_history","door_number","street_name", "landmark","country",
            "state","city"
        ]

        for field in updatable_fields:
            if field in data:
                setattr(vendor, field, data.get(field))

        # Handle file upload if present
        if 'gst_certificate' in request.FILES:
            vendor.gst_certificate = request.FILES['gst_certificate']
        if 'business_license' in request.FILES:
            vendor.business_license = request.FILES['business_license']
        if 'pan_card' in request.FILES:
            vendor.pan_card = request.FILES['pan_card']
        if 'profile_picture' in request.FILES:
            vendor.profile_picture = request.FILES['profile_picture']

        vendor.save()

        return Response({'status': 'success', 'message': 'Vendor updated successfully'})

    except VendorData.DoesNotExist:
        return Response({'status': 'error', 'message': 'Vendor not found'}, status=404)
    except Exception as e:
        return Response({'status': 'error', 'message': str(e)}, status=500)


@api_view(['PUT'])
@parser_classes([MultiPartParser, FormParser])
def update_trainer(request):
    try:
        data = request.data
        trainer = None
        query_params = request.query_params

        # Identify trainer
        trainer_id = data.get('id') or query_params.get('id')
        trainer_email = data.get('email') or query_params.get('email')

        if trainer_id:
            trainer = TrainerData.objects.get(id=trainer_id)
        elif trainer_email:
            trainer = TrainerData.objects.get(email=trainer_email.strip())
        else:
            return Response({'status': 'error', 'message': 'Provide trainer ID or email'}, status=400)

        # List of updatable fields (you can add/remove based on your model)
        updatable_fields = [
            "first_name", "last_name","date_of_birth", "gender",
            "phone_number", "highest_qualification", "specialization","address","pincode"
            "total_experience_years", "current_organization", "previous_teaching_experience",
            "certifications", "account_holder_name", "bank_name_branch", "account_number",
            "ifsc_code", "available_days", "available_mode", "preferred_time_slots","door_number","street_name", "landmark","country",
            "state","city"
        ]

        # Update non-file fields
        for field in updatable_fields:
            if field in data:
                setattr(trainer, field, data.get(field))

        # Handle file fields
        if 'resume' in request.FILES:
            trainer.resume = request.FILES['resume']
        if 'id_proof' in request.FILES:
            trainer.id_proof = request.FILES['id_proof']
        if 'educational_certificates' in request.FILES:
            trainer.educational_certificates = request.FILES['educational_certificates']
        if 'profile_picture' in request.FILES:
            trainer.profile_picture = request.FILES['profile_picture']

        trainer.save()

        return Response({'status': 'success', 'message': 'Trainer updated successfully'})
    
    except TrainerData.DoesNotExist:
        return Response({'status': 'error', 'message': 'Trainer not found'}, status=404)
    
    except Exception as e:
        return Response({'status': 'error', 'message': str(e)}, status=500)

@api_view(['PUT'])
def update_trainer_status(request):
    try:
        data = request.data
        record_id = data.get('id')
        email = data.get('email')
        new_status = data.get('status')

        if not new_status:
            return Response({"error": "Status is required."}, status=status.HTTP_400_BAD_REQUEST)

        if not record_id and not email:
            return Response({"error": "Either 'id' or 'email' is required."}, status=status.HTTP_400_BAD_REQUEST)

        trainer = None
        if record_id:
            trainer = TrainerData.objects.filter(id=record_id).first()
        else:
            trainer = TrainerData.objects.filter(login__email=email).first()

        if not trainer:
            return Response({"error": "Trainer not found."}, status=status.HTTP_404_NOT_FOUND)

        trainer.status = new_status
        trainer.save()
        return Response({"message": f"Trainer status updated to '{new_status}'."}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['PUT'])
def update_vendor_status(request):
    try:
        data = request.data
        record_id = data.get('id')
        email = data.get('email')
        new_status = data.get('status')

        if not new_status:
            return Response({"error": "Status is required."}, status=status.HTTP_400_BAD_REQUEST)

        if not record_id and not email:
            return Response({"error": "Either 'id' or 'email' is required."}, status=status.HTTP_400_BAD_REQUEST)

        vendor = None
        if record_id:
            vendor = VendorData.objects.filter(id=record_id).first()
        else:
            vendor = VendorData.objects.filter(login__email=email).first()

        if not vendor:
            return Response({"error": "Vendor not found."}, status=status.HTTP_404_NOT_FOUND)

        vendor.status = new_status
        vendor.save()
        return Response({"message": f"Vendor status updated to '{new_status}'."}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_user_category_counts(request):
    try:
        total_students = StudentInformation.objects.count()
        total_approved_trainers = TrainerData.objects.filter(status='approved').count()
        total_approved_vendors = VendorData.objects.filter(status='approved').count()

        data = {
            'total_students': total_students,
            'total_approved_trainers': total_approved_trainers,
            'total_approved_vendors': total_approved_vendors
        }

        return Response(data, status=200)
    except Exception as e:
        return Response({'error': str(e)}, status=500)
    
@api_view(['GET'])
def get_trainer_status_counts(request):
    try:
        approved = TrainerData.objects.filter(status='approved').count()
        waiting = TrainerData.objects.filter(status='waiting').count()
        rejected = TrainerData.objects.filter(status='rejected').count()

        data = {
            'approved_trainers': approved,
            'waiting_trainers': waiting,
            'rejected_trainers': rejected
        }

        return Response(data, status=200)
    except Exception as e:
        return Response({'error': str(e)}, status=500)

@api_view(['GET'])
def get_vendor_status_counts(request):
    try:
        approved = VendorData.objects.filter(status='approved').count() 
        waiting = VendorData.objects.filter(status='waiting').count()
        rejected = VendorData.objects.filter(status='rejected').count()

        data = {
            'approved_vendors': approved,
            'waiting_vendors': waiting,
            'rejected_vendors': rejected
        }

        return Response(data, status=200)
    except Exception as e:
        return Response({'error': str(e)}, status=500)
    
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import InstitutionData
from .serializers import InstitutionDataSerializer

# Create and List all institutions
@api_view(['GET', 'POST'])
# @permission_classes([permissions.IsAuthenticated])
def institution_list_create(request):
    if request.method == 'GET':
        institutions = InstitutionData.objects.all()
        serializer = InstitutionDataSerializer(institutions, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = InstitutionDataSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Read (GET) single institution by ID
@api_view(['GET'])
# @permission_classes([permissions.IsAuthenticated])
def get_institution(request, pk):
    try:
        institution = InstitutionData.objects.get(pk=pk)
    except InstitutionData.DoesNotExist:
        return Response({'error': 'Not Found'}, status=status.HTTP_404_NOT_FOUND)

    serializer = InstitutionDataSerializer(institution)
    return Response(serializer.data)


# Update (PUT) single institution by ID
@api_view(['PATCH'])  # ← Allow PATCH instead of PUT
# @permission_classes([permissions.IsAuthenticated])
def update_institution(request, pk):
    try:
        institution = InstitutionData.objects.get(pk=pk)
    except InstitutionData.DoesNotExist:
        return Response({'error': 'Not Found'}, status=status.HTTP_404_NOT_FOUND)

    serializer = InstitutionDataSerializer(institution, data=request.data, partial=True)  # ← partial=True
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



# Delete (DELETE) single institution by ID
@api_view(['DELETE'])
# @permission_classes([permissions.IsAuthenticated])
def delete_institution(request, pk):
    try:
        institution = InstitutionData.objects.get(pk=pk)
    except InstitutionData.DoesNotExist:
        return Response({'error': 'Not Found'}, status=status.HTTP_404_NOT_FOUND)

    institution.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)
