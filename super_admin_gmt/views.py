from django.shortcuts import render
from rest_framework.decorators import api_view,parser_classes
from rest_framework.response import Response
from signup_gmt.models import LoginDetails, Role, StudentInformation, VendorData, TrainerData
from django.db import transaction
from rest_framework.parsers import MultiPartParser, FormParser
import requests
from django.conf import settings
import random
from django.utils.dateparse import parse_date
from django.db.models import Q
from rest_framework import status
from .models import AdminData
import traceback

@api_view(['POST'])
def superadmin_add_student(request):
    try:
        with transaction.atomic():
            role = Role.objects.get(role_name='student')

            login = LoginDetails.objects.create(
                username=request.data.get('username'),
                email=request.data.get('email'),
                password=request.data.get('password'),
                role=role
            )

            StudentInformation.objects.create(
                login=login,
                date_of_birth=parse_date(request.data.get('date_of_birth')),

                door_number=request.data.get('door_number',''),
                street_Name=request.data.get('street_Name',''),
                landmark=request.data.get('landmark',''),
                country=request.data.get('country',''),
                state=request.data.get('state',''),
                city=request.data.get('city',''),

                firstname=request.data.get('firstname', ''),
                lastname=request.data.get('lastname', ''),
                email=request.data.get('email', ''),
                contact_number=request.data.get('contact_number', ''),
                alt_contact=request.data.get('alt_contact', ''),
                father_name=request.data.get('father_name', ''),
                mother_name=request.data.get('mother_name', ''),
                pincode=request.data.get('pincode', ''),
                description=request.data.get('description', ''),
                designation=request.data.get('designation', ''),
                gender=request.data.get('gender', ''),
                skills=request.data.get('skills', []),
                account_holder_name=request.data.get('account_holder_name', ''),
                account_number=request.data.get('account_number', ''),
                bank_location=request.data.get('bank_location', ''),
                bank_name=request.data.get('bank_name', ''),
                branch_name=request.data.get('branch_name', ''),
                ifsc_code=request.data.get('ifsc_code', ''),
                institution_name=request.data.get('institution_name', ''),
                location=request.data.get('location', ''),
                major_subject=request.data.get('major_subject', ''),
                qualification=request.data.get('qualification', ''),
                cgpa=float(request.data.get('cgpa')) if request.data.get('cgpa') else None,
                passedout=int(request.data.get('passedout')) if request.data.get('passedout') else None,
                profile_picture=request.FILES.get('profile_picture')
            )

            return Response({'message': 'Student registered successfully'}, status=201)
    except Exception as e:
        return Response({'error': str(e)}, status=400)

@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def superadmin_add_vendor(request):
    try:
        with transaction.atomic():
            role = Role.objects.get(role_name='vendor')

            login = LoginDetails.objects.create(
                username=request.data['username'],
                email=request.data['email'],
                password=request.data['password'],
                role=role
            )

            vendor = VendorData.objects.create(
                login=login,
                status='approved',
                role='vendor',
                firstname=request.data.get('firstname', ''),
                lastname=request.data.get('lastname', ''),
                business_name=request.data.get('business_name', ''),
                business_type=request.data.get('business_type', ''),
                gst_number=request.data.get('gst_number', ''),
                registration_number=request.data.get('registration_number', ''),
                year_of_establishment=request.data.get('year_of_establishment'),
                contact_email=request.data.get('contact_email', ''),
                contact_phone=request.data.get('contact_phone', ''),
                alternate_contact=request.data.get('alternate_contact', ''),
                
                door_number=request.data.get('door_number',''),
                street_Name=request.data.get('street_Name',''),
                landmark=request.data.get('landmark',''),
                country=request.data.get('country',''),
                state=request.data.get('state',''),
                city=request.data.get('city',''),

                pincode=request.data.get('pincode', ''),
                account_holder_name=request.data.get('account_holder_name', ''),
                bank_name_branch=request.data.get('bank_name_branch', ''),
                account_number=request.data.get('account_number', ''),
                ifsc_code=request.data.get('ifsc_code', ''),
                gst_certificate=request.FILES.get('gst_certificate', None),
                business_license=request.FILES.get('business_license', None),
                pan_card=request.FILES.get('pan_card', None),
                profile_picture=request.FILES.get('profile_picture', None),
                events_type=request.data.get('events_type', ''),
                event_history=request.data.get('event_history', '')
            )

            return Response({'message': 'Vendor created and approved successfully', 'vendor_id': vendor.id}, status=status.HTTP_201_CREATED)

    except Role.DoesNotExist:
        return Response({'error': 'Vendor role not found.'}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'error': 'Something went wrong', 'details': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def superadmin_add_trainer(request):
    try:
        with transaction.atomic():
            role = Role.objects.get(role_name='trainer')

            login = LoginDetails.objects.create(
                username=request.data['username'],
                email=request.data['email'],
                password=request.data['password'],
                role=role
            )

            TrainerData.objects.create(
                login=login,
                status='approved',
                first_name=request.data.get('first_name', ''),
                last_name=request.data.get('last_name', ''),
                date_of_birth=request.data.get('date_of_birth', None),
                gender=request.data.get('gender', ''),
                email=request.data.get('email', ''),
                phone_number=request.data.get('phone_number', ''),

                door_number=request.data.get('door_number',''),
                street_Name=request.data.get('street_Name',''),
                landmark=request.data.get('landmark',''),
                country=request.data.get('country',''),
                state=request.data.get('state',''),
                city=request.data.get('city',''),

                highest_qualification=request.data.get('highest_qualification', ''),
                specialization=request.data.get('specialization', ''),
                total_experience_years=request.data.get('total_experience_years', None),
                current_organization=request.data.get('current_organization', ''),
                previous_teaching_experience=request.data.get('previous_teaching_experience', ''),
                certifications=request.data.get('certifications', ''),
                account_holder_name=request.data.get('account_holder_name', ''),
                bank_name_branch=request.data.get('bank_name_branch', ''),
                account_number=request.data.get('account_number', ''),
                ifsc_code=request.data.get('ifsc_code', ''),
                resume=request.FILES.get('resume', None),
                id_proof=request.FILES.get('id_proof', None),
                educational_certificates=request.FILES.get('educational_certificates', None),
                profile_picture=request.FILES.get('profile_picture', None),
                available_days=request.data.get('available_days', []),
                available_mode=request.data.get('available_mode', ''),
                preferred_time_slots=request.data.get('preferred_time_slots', '')
            )

            return Response({'message': 'Trainer created and approved successfully'}, status=status.HTTP_201_CREATED)

    except Role.DoesNotExist:
        return Response({'error': 'Trainer role not found.'}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        print(traceback.format_exc())
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def superadmin_add_admin(request):
    try:
        with transaction.atomic():
            role = Role.objects.get(role_name='admin')

            login = LoginDetails.objects.create(
                username=request.data.get('username'),
                email=request.data.get('email'),
                password=request.data.get('password'),
                role=role
            )
            AdminData.objects.create(
                login=login,
                first_name=request.data.get('first_name', ''),
                last_name=request.data.get('last_name', ''),
                email=request.data.get('email', ''),
                phone_number=request.data.get('phone_number', ''),
                gender=request.data.get('gender', ''),
                profile_picture=request.FILES.get('profile_picture')
            )

            return Response({'message': 'Admin registered successfully'}, status=status.HTTP_201_CREATED)

    except Role.DoesNotExist:
        return Response({'error': 'Admin role not found.'}, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_admin_count(request):
    try:
        total_admins = AdminData.objects.count()

        return Response({'total_admins': total_admins}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_all_admins(request):
    try:
        admins = AdminData.objects.all()
        admin_list = []

        for admin in admins:
            admin_dict = {
                'id': admin.id,
                'first_name': admin.first_name,
                'last_name': admin.last_name,
                'email': admin.email,
                'phone_number': admin.phone_number,
                'gender': admin.gender,
                'profile_picture': admin.profile_picture.url if admin.profile_picture else None,
                'role': admin.role,
                'created_at': admin.created_at,
            }
            admin_list.append(admin_dict)

        return Response({'success': True, 'data': admin_list}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
