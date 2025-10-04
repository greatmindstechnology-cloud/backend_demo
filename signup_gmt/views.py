from rest_framework.decorators import api_view,parser_classes
from rest_framework.response import Response
from .models import LoginDetails, Role, StudentInformation, VendorData, TrainerData
from .serializers import *
from django.db import transaction
from rest_framework.parsers import MultiPartParser, FormParser
from django.core.mail import send_mail
from django.core.cache import cache
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
import random
from django.utils.dateparse import parse_date
from django.db.models import Q
import re







@api_view(['POST'])
def student_signup(request):
    try:
        data = request.data

        # Validation dictionary: key -> (value, regex, error_message)
        validation_rules = {
            'username': (data.get('username', ''), r'^[a-zA-Z0-9_.-]+$', "Invalid username"),
            'email': (data.get('email', ''), r'^[\w\.-]+@[\w\.-]+\.\w+$', "Invalid email"),
            'contact_number': (data.get('contact_number', ''), r'^\+\d{1,4}\d{6,14}$', "Invalid contact number"),
            'alt_contact': (data.get('alt_contact', ''), r'^\+\d{1,4}\d{6,14}$', "Invalid alternate contact"),
            'pincode': (data.get('pincode', ''), r'^\d{6}$', "Invalid pincode"),
            'account_number': (data.get('account_number', ''), r'^\d{9,18}$', "Invalid account number"),
            'ifsc_code': (data.get('ifsc_code', ''), r'^[A-Z]{4}0[A-Z0-9]{6}$', "Invalid IFSC code"),
            'firstname': (data.get('firstname', ''), r'^[A-Za-z\s]{2,50}$', "Invalid firstname"),
            'lastname': (data.get('lastname', ''), r'^[A-Za-z\s]{0,50}$', "Invalid lastname"),
            'father_name': (data.get('father_name', ''), r'^[A-Za-z\s]{0,50}$', "Invalid father name"),
            'mother_name': (data.get('mother_name', ''), r'^[A-Za-z\s]{0,50}$', "Invalid mother name"),
            'door_number': (data.get('door_number', ''), r'^[\w\s/-]{0,50}$', "Invalid door number"),
            'street_name': (data.get('street_name', ''), r'^[\w\s.,-]{0,100}$', "Invalid street name"),
            'landmark': (data.get('landmark', ''), r'^[\w\s.,-]{0,100}$', "Invalid landmark"),
            'country': (data.get('country', ''), r'^[A-Za-z\s]{0,50}$', "Invalid country"),
            'state': (data.get('state', ''), r'^[A-Za-z\s]{0,50}$', "Invalid state"),
            'city': (data.get('city', ''), r'^[A-Za-z\s]{0,50}$', "Invalid city"),
            'designation': (data.get('designation', ''), r'^[A-Za-z\s]{0,50}$', "Invalid designation"),
            'account_holder_name': (data.get('account_holder_name', ''), r'^[A-Za-z\s]{0,50}$', "Invalid account holder name"),
            'bank_location': (data.get('bank_location', ''), r'^[\w\s.,-]{0,100}$', "Invalid bank location"),
            'bank_name': (data.get('bank_name', ''), r'^[A-Za-z\s]{0,50}$', "Invalid bank name"),
            'branch_name': (data.get('branch_name', ''), r'^[A-Za-z\s]{0,50}$', "Invalid branch name"),
            'institution_name': (data.get('institution_name', ''), r'^[\w\s.,-]{0,100}$', "Invalid institution name"),
            'location': (data.get('location', ''), r'^[\w\s.,-]{0,100}$', "Invalid location"),
            'major_subject': (data.get('major_subject', ''), r'^[A-Za-z\s]{0,100}$', "Invalid major subject"),
            'qualification': (data.get('qualification', ''), r'^[A-Za-z\s]{0,50}$', "Invalid qualification"),
        }

        for field, (value, pattern, error) in validation_rules.items():
            if value and not re.match(pattern, value):
                return Response({'error': f"{error} (Field: {field})"}, status=400)

        if data.get('gender') not in ['Male', 'Female', 'Other']:
            return Response({'error': 'Invalid gender'}, status=400)

        if data.get('cgpa'):
            try:
                float(data.get('cgpa'))
            except ValueError:
                return Response({'error': 'Invalid CGPA'}, status=400)

        if data.get('passedout'):
            try:
                int(data.get('passedout'))
            except ValueError:
                return Response({'error': 'Invalid passed out year'}, status=400)

        with transaction.atomic():
            role = Role.objects.get(role_name='student')

            login = LoginDetails.objects.create(
                username=data.get('username'),
                email=data.get('email'),
                password=data.get('password'),
                role=role
            )

            StudentInformation.objects.create(
                login=login,
                date_of_birth=parse_date(data.get('date_of_birth')),
                firstname=data.get('firstname', ''),
                lastname=data.get('lastname', ''),
                email=data.get('email', ''),
                contact_number=data.get('contact_number', ''),
                alt_contact=data.get('alt_contact', ''),
                father_name=data.get('father_name', ''),
                mother_name=data.get('mother_name', ''),
                door_number=data.get('door_number', ''),
                street_name=data.get('street_name', ''),
                landmark=data.get('landmark', ''),
                country=data.get('country', ''),
                state=data.get('state', ''),
                city=data.get('city', ''),
                pincode=data.get('pincode', ''),
                description=data.get('description', ''),
                designation=data.get('designation', ''),
                gender=data.get('gender', ''),
                skills=data.get('skills', []),
                account_holder_name=data.get('account_holder_name', ''),
                account_number=data.get('account_number', ''),
                bank_location=data.get('bank_location', ''),
                bank_name=data.get('bank_name', ''),
                branch_name=data.get('branch_name', ''),
                ifsc_code=data.get('ifsc_code', ''),
                institution_name=data.get('institution_name', ''),
                location=data.get('location', ''),
                major_subject=data.get('major_subject', ''),
                qualification=data.get('qualification', ''),
                cgpa=float(data.get('cgpa')) if data.get('cgpa') else None,
                passedout=int(data.get('passedout')) if data.get('passedout') else None,
                profile_picture=request.FILES.get('profile_picture')
            )

            return Response({'message': 'Student registered successfully'}, status=201)

    except Role.DoesNotExist:
        return Response({'error': 'Student role not found'}, status=404)
    except Exception as e:
        return Response({'error': str(e)}, status=400)
    
@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def trainer_signup(request):
    try:
        data = request.data
        def validate(field, pattern, message):
            value = data.get(field, '')
            if value and not re.match(pattern, value):
                raise ValueError(f"{field}: {message}")
        validate('username', r'^[a-zA-Z0-9_.-]+$', 'Invalid username')
        validate('email', r'^[\w\.-]+@[\w\.-]+\.\w+$', 'Invalid email')
        validate('phone_number', r'^\+\d{1,4}\d{6,14}$', 'Invalid phone number')
        validate('account_number', r'^\d{9,18}$', 'Invalid account number')
        validate('ifsc_code', r'^[A-Z]{4}0[A-Z0-9]{6}$', 'Invalid IFSC code')
        validate('first_name', r'^[A-Za-z\s]{2,50}$', 'Invalid first name')
        validate('last_name', r'^[A-Za-z\s]{0,50}$', 'Invalid last name')
        validate('door_number', r'^[\w\s/-]{0,50}$', 'Invalid door number')
        validate('street_name', r'^[\w\s.,-]{0,100}$', 'Invalid street name')
        validate('landmark', r'^[\w\s.,-]{0,100}$', 'Invalid landmark')
        validate('country', r'^[A-Za-z\s]{0,50}$', 'Invalid country')
        validate('state', r'^[A-Za-z\s]{0,50}$', 'Invalid state')
        validate('city', r'^[A-Za-z\s]{0,50}$', 'Invalid city')
        validate('account_holder_name', r'^[A-Za-z\s]{0,50}$', 'Invalid account holder name')
        validate('bank_location', r'^[A-Za-z0-9\s\.\-]{2,100}$', 'Invalid bank location')
        validate('bank_name', r'^[A-Za-z0-9\s\.\-]{2,100}$', 'Invalid bank name')
        validate('branch_name', r'^[A-Za-z0-9\s\.\-]{2,100}$', 'Invalid branch name')
        validate('highest_qualification', r'^[A-Za-z.\s]{1,50}$', 'Invalid qualification')
        validate('specialization', r'^[A-Za-z\s]{1,100}$', 'Invalid specialization')
        validate('current_organization', r'^[\w\s.,-]{0,100}$', 'Invalid organization name')
        validate('certifications', r'^[\w\s.,-]{0,255}$', 'Invalid certifications')
        validate('previous_teaching_experience', r'^[\w\s.,-]{0,255}$', 'Invalid experience')

        if data.get('gender') not in ['Male', 'Female', 'Other']:
            raise ValueError("gender: Invalid gender")

        if data.get('total_experience_years'):
            try:
                float(data.get('total_experience_years'))
            except:
                raise ValueError("total_experience_years: Must be a number")

        with transaction.atomic():
            role = Role.objects.get(role_name='trainer')

            login = LoginDetails.objects.create(
                username=data['username'],
                email=data['email'],
                password=data['password'],
                role=role
            )

            TrainerData.objects.create(
                login=login,
                first_name=data.get('first_name', ''),
                last_name=data.get('last_name', ''),
                date_of_birth=data.get('date_of_birth', None),
                gender=data.get('gender', ''),
                email=data.get('email', ''),
                phone_number=data.get('phone_number', ''),
                highest_qualification=data.get('highest_qualification', ''),
                specialization=data.get('specialization', ''),
                total_experience_years=data.get('total_experience_years', None),
                current_organization=data.get('current_organization', ''),
                previous_teaching_experience=data.get('previous_teaching_experience', ''),
                certifications=data.get('certifications', ''),
                door_number=data.get('door_number',''),
                street_name=data.get('street_name',''),
                landmark=data.get('landmark',''),
                country=data.get('country',''),
                state=data.get('state',''),
                city=data.get('city',''),
                account_holder_name=data.get('account_holder_name', ''),
                bank_location=data.get('bank_location', ''),
                bank_name=data.get('bank_name', ''),
                branch_name=data.get('branch_name', ''),
                account_number=data.get('account_number', ''),
                ifsc_code=data.get('ifsc_code', ''),
                resume=request.FILES.get('resume', None),
                id_proof=request.FILES.get('id_proof', None),
                educational_certificates=request.FILES.get('educational_certificates', None),
                profile_picture=request.FILES.get('profile_picture', None),
                available_days=data.get('available_days', []),
                available_mode=data.get('available_mode', ''),
                preferred_time_slots=data.get('preferred_time_slots', '')
            )

            return Response({'message': 'Trainer request submitted successfully'}, status=201)

    except Role.DoesNotExist:
        return Response({'error': 'Role "trainer" not found'}, status=404)
    except ValueError as ve:
        return Response({'error': str(ve)}, status=400)
    except Exception as e:
        return Response({'error': str(e)}, status=500)

@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def vendor_signup(request):
    try:
        data = request.data

        def validate(field, pattern, message):
            value = data.get(field, '')
            if value and not re.match(pattern, value):
                raise ValueError(f"{field}: {message}")
        validate('username', r'^[a-zA-Z0-9_.-]+$', 'Invalid username')
        validate('email', r'^[\w\.-]+@[\w\.-]+\.\w+$', 'Invalid email')
        validate('contact_phone', r'^\+\d{1,4}\d{6,14}$', 'Invalid contact number')
        validate('alternate_contact', r'^\+\d{1,4}\d{6,14}$', 'Invalid alternate contact')
        validate('account_number', r'^\d{9,18}$', 'Invalid account number')
        validate('ifsc_code', r'^[A-Z]{4}0[A-Z0-9]{6}$', 'Invalid IFSC code')
        validate('firstname', r'^[A-Za-z\s]{2,50}$', 'Invalid first name')
        validate('lastname', r'^[A-Za-z\s]{0,50}$', 'Invalid last name')
        validate('business_name', r'^[\w\s.&-]{2,100}$', 'Invalid business name')
        validate('business_type', r'^[A-Za-z\s]{2,50}$', 'Invalid business type')
        validate('gst_number', r'^\d{2}[A-Z]{5}\d{4}[A-Z]{1}[A-Z\d]{1}[Z]{1}[A-Z\d]{1}$', 'Invalid GST number')
        validate('registration_number', r'^[\w-]{5,30}$', 'Invalid registration number')
        validate('door_number', r'^[\w\s/-]{0,50}$', 'Invalid door number')
        validate('street_name', r'^[\w\s.,-]{0,100}$', 'Invalid street name')
        validate('landmark', r'^[\w\s.,-]{0,100}$', 'Invalid landmark')
        validate('country', r'^[A-Za-z\s]{0,50}$', 'Invalid country')
        validate('state', r'^[A-Za-z\s]{0,50}$', 'Invalid state')
        validate('city', r'^[A-Za-z\s]{0,50}$', 'Invalid city')
        validate('account_holder_name', r'^[A-Za-z\s]{0,50}$', 'Invalid account holder name')
        validate('bank_location', r'^[A-Za-z0-9\s\.\-]{2,100}$', 'Invalid bank location')
        validate('bank_name', r'^[A-Za-z0-9\s\.\-]{2,100}$', 'Invalid bank name')
        validate('branch_name', r'^[A-Za-z0-9\s\.\-]{2,100}$', 'Invalid branch name')
        validate('events_type', r'^[\w\s,.-]{0,100}$', 'Invalid events type')
        validate('event_history', r'^[\w\s.,-]{0,1000}$', 'Invalid event history')

        # Validate year
        if data.get('year_of_establishment'):
            try:
                year = int(data.get('year_of_establishment'))
                if year < 1900 or year > 2100:
                    raise ValueError("year_of_establishment: Must be a valid year")
            except:
                raise ValueError("year_of_establishment: Must be a number")

        # Save vendor
        with transaction.atomic():
            role = Role.objects.get(role_name='vendor')

            login = LoginDetails.objects.create(
                username=data['username'],
                email=data['email'],
                password=data['password'],
                role=role
            )

            VendorData.objects.create(
                login=login,
                firstname=data.get('firstname', ''),
                lastname=data.get('lastname', ''),
                business_name=data.get('business_name', ''),
                business_type=data.get('business_type', ''),
                gst_number=data.get('gst_number', ''),
                registration_number=data.get('registration_number', ''),
                year_of_establishment=data.get('year_of_establishment', None),
                contact_email=data.get('email', ''),
                contact_phone=data.get('contact_phone', ''),
                alternate_contact=data.get('alternate_contact', ''),
                door_number=data.get('door_number', ''),
                street_name=data.get('street_name', ''),
                landmark=data.get('landmark', ''),
                country=data.get('country', ''),
                state=data.get('state', ''),
                city=data.get('city', ''),
                account_holder_name=data.get('account_holder_name', ''),
                bank_location=data.get('bank_location', ''),
                bank_name=data.get('bank_name', ''),
                branch_name=data.get('branch_name', ''),
                account_number=data.get('account_number', ''),
                ifsc_code=data.get('ifsc_code', ''),
                gst_certificate=request.FILES.get('gst_certificate', None),
                business_license=request.FILES.get('business_license', None),
                pan_card=request.FILES.get('pan_card', None),
                profile_picture=request.FILES.get('profile_picture', None),
                events_type=data.get('events_type', ''),
                event_history=data.get('event_history', '')
            )

            return Response({'message': 'Vendor request submitted successfully'}, status=201)

    except Role.DoesNotExist:
        return Response({'error': 'Role "vendor" not found'}, status=404)
    except ValueError as ve:
        return Response({'error': str(ve)}, status=400)
    except Exception as e:
        return Response({'error': str(e)}, status=500)



@api_view(['POST'])
# @permission_classes([IsAuthenticated])
def login_view(request):
    try:
        identifier = request.data.get('identifier')
        password = request.data.get('password')

        if not identifier or not password:
            return Response({'error': 'Username/email and password are required'}, status=400)

        user = LoginDetails.objects.filter(
            Q(username=identifier) | Q(email=identifier)
        ).select_related('role').first()
        print(user)
        print(user.role_id)
        if not user:
            return Response({'error': 'Invalid credentials'}, status=401)
        if user.password != password:
            return Response({'error': 'Invalid credentials'}, status=401)

        role_name = user.role.role_name.lower()
        actual_id = None

        if user.role_id == 3:
            vendor = VendorData.objects.filter(login=user).first()
            if vendor:
                if vendor.status == 'waiting':
                    return Response({'error': 'Vendor account is waiting'}, status=403)
                if vendor.status == 'rejected':
                    return Response({'error': 'Vendor account is rejected'}, status=403)
                actual_id = vendor.id

        elif user.role_id == 4:
            trainer = TrainerData.objects.filter(login=user).first()
            if trainer:
                if trainer.status == 'waiting':
                    return Response({'error': 'Trainer account is waiting'}, status=403)
                if trainer.status == 'rejected':
                    return Response({'error': 'Trainer account is rejected'}, status=403)
                actual_id = trainer.id

        elif user.role_id == 5:
            student = StudentInformation.objects.filter(login=user).first()
            print(student)
            if student:
                actual_id = student.id

        return Response({
            'status': 'Login success',
            'role': role_name,
            'email': user.email,
            'id': actual_id 
        })

    except Exception as e:
        return Response({'error': str(e)}, status=500)


@api_view(['POST'])
def signup_view(request):
    serializer = EmailOnlySerializer(data=request.data)

    if serializer.is_valid():
        email = request.data.get('email')
        send_otp_via_email(email)
        return Response({"status": "otp_sent", "message": "OTP sent to your email."})
    return Response(serializer.errors, status=400)
def send_otp_via_email(email):
    otp = str(random.randint(100000, 999999))
    cache.set(email, otp, timeout=300)  
    subject = 'Your OTP Code'
    text_content = f'Your OTP code is {otp}'
    from_email = settings.DEFAULT_FROM_EMAIL
    to = [email]  
        
    html_content = render_to_string('index.html', {'otp': otp})
    text_content = f'Your OTP code is {otp}'

    msg = EmailMultiAlternatives(subject, text_content, from_email, to)
    msg.attach_alternative(html_content, "text/html")
    msg.send()

@api_view(['POST'])
def verify_otp_view(request):
    email = request.data.get('email')
    otp = request.data.get('otp')

    if not email or not otp:
        return Response({'status': 'error', 'message': 'Email and OTP are required'}, status=400)

    cached_otp = cache.get(email)
    if cached_otp == otp:
        return Response({'status': 'success', 'message': 'OTP verified successfully'})
    else:
        return Response({'status': 'error', 'message': 'Invalid or expired OTP'}, status=400)