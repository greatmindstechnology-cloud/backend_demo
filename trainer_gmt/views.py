from rest_framework.decorators import api_view, permission_classes,parser_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from course_gmt.models import CourseTable, Section, Lecture
from .serializers import TrainerCourseSerializer, SectionSerializer,CounselorApplicationSerializer,CounselorSerializer, CounselingRequestSerializer,CounselingFeedbackSerializer
from django.db.models import Max
from signup_gmt.models import TrainerData,StudentInformation, LoginDetails
from rest_framework.parsers import MultiPartParser, FormParser,JSONParser
from .models import Topic, TrainerData,QuizQuestion,AssignmentResult,StudentAssignmentSubmission,Assignment,CounselorApplication,Counselor, CounselingRequest,CounselingFeedback
from django.utils import timezone
import traceback
from django.core.exceptions import ObjectDoesNotExist
# from .utils import create_calendar_event
from .utils import create_jitsi_meeting
from django.utils import timezone
from datetime import datetime
import logging
import json
from django.core.files.storage import default_storage

logger = logging.getLogger(__name__)


@api_view(['POST'])
def trainer_create_course(request):
    try:
        trainer_id = request.query_params.get('trainer_id')
        if not trainer_id:
            return Response({'error': 'trainer_id query param is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            trainer = TrainerData.objects.get(id=trainer_id)
        except TrainerData.DoesNotExist:
            return Response({'error': 'Trainer not found'}, status=status.HTTP_404_NOT_FOUND)

        data = request.data.copy()
        data['trainer'] = trainer.id
        data['status'] = 'waiting'

        serializer = TrainerCourseSerializer(data=data)
        if serializer.is_valid():
            course = serializer.save(trainer=trainer)
            response_data = TrainerCourseSerializer(course).data
            response_data['course_id'] = course.course_id
            return Response(response_data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def trainer_add_section(request):
    try:
        course_id = request.query_params.get('course_id')
        if not course_id:
            return Response({'error': 'course_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            course = CourseTable.objects.get(pk=course_id)
        except CourseTable.DoesNotExist:
            return Response({'error': 'Course not found'}, status=status.HTTP_404_NOT_FOUND)

        section_title = request.data.get('section_title')
        if not section_title:
            return Response({'error': 'section_title is required'}, status=status.HTTP_400_BAD_REQUEST)

        section = Section(course=course, section_title=section_title)
        section.save()

        serializer = SectionSerializer(section)
        response_data = serializer.data.copy()
        response_data['section_id'] = section.id 

        return Response(response_data, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def trainer_add_lecture(request):
    try:
        section_id = request.query_params.get('section_id')
        if not section_id:
            return Response({'error': 'section_id is required as a query parameter'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            section = Section.objects.get(pk=section_id)
        except Section.DoesNotExist:
            return Response({'error': 'Section not found'}, status=status.HTTP_404_NOT_FOUND)
        title = request.data.get('title')
        duration = request.data.get('duration')
        active = request.data.get('active')
        video_file = request.FILES.get('video_file')
        pdf = request.FILES.get('pdf')
        ppt = request.FILES.get('ppt')
        if not title or not isinstance(title, str):
            return Response({'error': 'Title is required and must be a string.'}, status=status.HTTP_400_BAD_REQUEST)
        if not duration:
            return Response({'error': 'Duration is required.'}, status=status.HTTP_400_BAD_REQUEST)
        if active is None:
            return Response({'error': 'Active field is required.'}, status=status.HTTP_400_BAD_REQUEST)
        from datetime import timedelta
        try:
            h, m, s = map(int, duration.split(':'))
            duration_td = timedelta(hours=h, minutes=m, seconds=s)
        except:
            return Response({'error': 'Invalid duration format. Use HH:MM:SS'}, status=status.HTTP_400_BAD_REQUEST)

        if isinstance(active, str):
            active = active.lower() in ['true', '1']
        lecture = Lecture(
            section=section,
            title=title,
            duration=duration_td,
            active=active,
            video_file=video_file,
            pdf=pdf,
            ppt=ppt


        )
        lecture.save()
        return Response({
            'id': lecture.id,
            'title': lecture.title,
            'duration': str(lecture.duration),
            'active': lecture.active,
            'video_file': lecture.video_file.url if lecture.video_file else None,
            'pdf': lecture.pdf.url if lecture.pdf else None,
            'ppt': lecture.ppt.url if lecture.ppt else None

        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_trainer_course_data(request):
    try:
        trainer_id = request.query_params.get('trainer_id')
        if not trainer_id:
            return Response({"error": "trainer_id parameter is required."}, status=status.HTTP_400_BAD_REQUEST)
        trainer = TrainerData.objects.get(pk=trainer_id)
        trainer_info = {
            "first_name": trainer.first_name,
            "last_name": trainer.last_name,
        }
        courses = CourseTable.objects.filter(trainer=trainer)
        course_data = []

        for course in courses:
            sections = Section.objects.filter(course=course)
            section_data = []

            for section in sections:
                lectures = Lecture.objects.filter(section=section)
                lecture_data = []

                for lecture in lectures:
                    lecture_data.append({
                        "id": lecture.id,
                        "title": lecture.title,
                        "duration": str(lecture.duration),
                        "completed": lecture.completed,
                        "active": lecture.active,
                        "order": lecture.order,
                        "video_file": lecture.video_file.url if lecture.video_file else None,
                    })

                section_data.append({
                    "id": section.id,
                    "title": section.section_title,
                    "order": section.order,
                    "lectures": lecture_data,
                })

            course_data.append({
                "id": course.course_id,
                "title": course.course_title,
                "price": float(course.course_price),
                "description": course.course_description,
                "rating": course.course_rating,
                "about_course": course.about_course,
                "specification": course.course_specification,
                "preknowledge": course.preknowledge,
                "why_this_course": course.why_this_course,
                "image": course.course_image.url if course.course_image else None,
                "status": course.status,
                "students_enrolled": course.total_students_enrolled,
                "sections": section_data,
                "author_name":course.author_name,
                "created_date":course.created_date
            })

        return Response({
            "trainer": trainer_info,
            "courses": course_data,
        }, status=status.HTTP_200_OK)

    except TrainerData.DoesNotExist:
        return Response({"error": "Trainer not found."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['POST'])
def create_topic(request):
    try:
        trainer_id = request.query_params.get('trainer_id')
        if not trainer_id:
            return Response({'error': 'trainer_id is required in query parameters'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            trainer = TrainerData.objects.get(id=trainer_id)
        except TrainerData.DoesNotExist:
            return Response({'error': 'Trainer not found'}, status=status.HTTP_404_NOT_FOUND)

        data = request.data

        topic = Topic.objects.create(
            trainer=trainer,
            title=data.get('title'),
            description=data.get('description', ''),
            duration=data.get('duration', 0),
            is_active=data.get('is_active', True),
            created_at=timezone.now()
        )

        return Response({
            'message': 'Topic created successfully',
            'topic_id': topic.id,
            'title': topic.title
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def create_quiz_question(request):
    try:
        topic_id = request.query_params.get('topic_id')

        if not topic_id:
            return Response({'error': 'topic_id is required as a query parameter'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            topic = Topic.objects.get(id=topic_id)
        except Topic.DoesNotExist:
            return Response({'error': 'Topic not found'}, status=status.HTTP_404_NOT_FOUND)

        questions_data = request.data

        if not isinstance(questions_data, list):
            return Response({'error': 'Request data must be a list of questions'}, status=status.HTTP_400_BAD_REQUEST)

        created_questions = []
        errors = []

        required_fields = ['question', 'option1', 'option2', 'option3', 'option4', 'correct_option']

        for index, data in enumerate(questions_data):
            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                errors.append({'index': index, 'error': f'Missing fields: {", ".join(missing_fields)}'})
                continue

            try:
                question = QuizQuestion.objects.create(
                    topic=topic,
                    question=data.get('question'),
                    option1=data.get('option1'),
                    option2=data.get('option2'),
                    option3=data.get('option3'),
                    option4=data.get('option4'),
                    correct_option=data.get('correct_option'),
                    explanation=data.get('explanation', ''),
                    marks=data.get('marks', 1),
                    difficulty=data.get('difficulty', 'medium')
                )
                created_questions.append({'index': index, 'question_id': question.id})
            except Exception as e:
                errors.append({
                    'index': index,
                    'error': str(e),
                    'traceback': traceback.format_exc()
                })

        return Response({
            'created_questions': created_questions,
            'errors': errors
        }, status=status.HTTP_207_MULTI_STATUS if errors else status.HTTP_201_CREATED)

    except Exception as e:
        return Response({
            'error': str(e),
            'traceback': traceback.format_exc()
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Assignment, TrainerData, CourseTable  # Make sure CourseTable is imported

@api_view(['POST'])
def create_assignment(request):
    try:
        trainer_id = request.data.get('trainer_id')
        course_id = request.data.get('course_id')  # Get course_id from request
        title = request.data.get('title')
        description = request.data.get('description', '')
        due_date = request.data.get('due_date')
        max_marks = request.data.get('max_marks', 100)

        # Validate trainer existence
        try:
            trainer = TrainerData.objects.get(id=trainer_id)
        except TrainerData.DoesNotExist:
            return Response({'error': 'Trainer not found'}, status=404)

        # Validate course existence
        try:
            course = CourseTable.objects.get(course_id=course_id)
        except CourseTable.DoesNotExist:
            return Response({'error': 'Course not found'}, status=404)

        # Create Assignment
        assignment = Assignment.objects.create(
            trainer=trainer,
            course=course,
            title=title,
            description=description,
            due_date=due_date,
            max_marks=max_marks
        )

        return Response({'message': 'Assignment created successfully', 'id': assignment.id}, status=201)

    except Exception as e:
        return Response({'error': str(e)}, status=400)



@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def submit_assignment(request):
    try:
        student_id = request.data.get('student_id')
        assignment_id = request.data.get('assignment_id')

        # Validate student
        try:
            student = StudentInformation.objects.get(id=student_id)
        except StudentInformation.DoesNotExist:
            return Response({'error': 'Student not found'}, status=404)

        # Validate assignment
        try:
            assignment = Assignment.objects.get(id=assignment_id)
        except Assignment.DoesNotExist:
            return Response({'error': 'Assignment not found'}, status=404)

        # Check for duplicate submission
        if StudentAssignmentSubmission.objects.filter(student=student, assignment=assignment).exists():
            return Response({'error': 'Assignment already submitted'}, status=400)

        # Create submission
        submission = StudentAssignmentSubmission.objects.create(
            student=student,
            assignment=assignment,
            answer_text=request.data.get('answer_text', ''),
            uploaded_file=request.FILES.get('uploaded_file', None)
        )

        return Response({
            'message': 'Assignment submitted successfully',
            'submission_id': submission.id
        }, status=201)

    except Exception as e:
        return Response({'error': str(e)}, status=400)
    
@api_view(['POST'])
def grade_assignment(request):
    try:
        student_id = request.data.get('student_id')
        assignment_id = request.data.get('assignment_id')
        marks = float(request.data.get('marks_obtained'))

        try:
            submission = StudentAssignmentSubmission.objects.get(
                student_id=student_id,
                assignment_id=assignment_id
            )
        except StudentAssignmentSubmission.DoesNotExist:
            return Response({'error': 'Submission not found'}, status=404)

        if getattr(submission, 'is_graded', False):
            return Response({'error': 'This assignment has already been graded'}, status=400)

        # Mark the submission
        submission.marks_obtained = marks
        submission.feedback = ''  # You can change this if needed
        submission.is_graded = True
        submission.save()

        total_marks = submission.assignment.max_marks
        percentage = (marks / total_marks) * 100

        grade = (
            'A' if percentage >= 90 else
            'B' if percentage >= 75 else
            'C' if percentage >= 60 else
            'D'
        )
        AssignmentResult.objects.create(
            student=submission.student,
            assignment=submission.assignment,
            marks_obtained=marks,
            total_possible_marks=total_marks,
            percentage=percentage,
            grade=grade
        )

        return Response({'message': 'Assignment graded successfully'}, status=200)

    except Exception as e:
        return Response({'error': str(e)}, status=400)

@api_view(['PUT'])
@parser_classes([MultiPartParser, FormParser])
def update_course_details(request):
    course_id = request.data.get('course_id')
    if not course_id:
        return Response({'error': 'course_id is required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        course = CourseTable.objects.get(course_id=course_id)

        course.course_title = request.data.get('course_title', course.course_title)
        course.course_price = request.data.get('course_price', course.course_price)
        course.course_description = request.data.get('course_description', course.course_description)
        course.course_rating = request.data.get('course_rating', course.course_rating)
        course.about_course = request.data.get('about_course', course.about_course)
        course.total_students_enrolled = request.data.get('total_students_enrolled', course.total_students_enrolled)
        course.course_specification = request.data.get('course_specification', course.course_specification)
        course.preknowledge = request.data.get('preknowledge', course.preknowledge)
        course.why_this_course = request.data.get('why_this_course', course.why_this_course)
        course.status = request.data.get('status', course.status)

        if 'course_image' in request.FILES:
            course.course_image = request.FILES['course_image']

        course.save()

        sections_data = request.data.getlist('sections')
        for index, section_data_json in enumerate(sections_data):
            import json
            section_data = json.loads(section_data_json)
            section_id = section_data.get('id')
            try:
                section = Section.objects.get(id=section_id, course=course)
                section.section_title = section_data.get('section_title', section.section_title)
                section.order = section_data.get('order', section.order)
                section.save()

                lectures_data = section_data.get('lectures', [])
                for lec_index, lecture_data in enumerate(lectures_data):
                    lecture_id = lecture_data.get('id')
                    try:
                        lecture = Lecture.objects.get(id=lecture_id, section=section)
                        lecture.title = lecture_data.get('title', lecture.title)
                        lecture.duration = lecture_data.get('duration', lecture.duration)
                        lecture.completed = lecture_data.get('completed', lecture.completed)
                        lecture.active = lecture_data.get('active', lecture.active)
                        lecture.order = lecture_data.get('order', lecture.order)

                      
                        prefix = f"lecture_{lecture_id}_"
                        if f"{prefix}video_file" in request.FILES:
                            lecture.video_file = request.FILES[f"{prefix}video_file"]
                        if f"{prefix}ppt" in request.FILES:
                            lecture.ppt = request.FILES[f"{prefix}ppt"]
                        if f"{prefix}pdf" in request.FILES:
                            lecture.pdf = request.FILES[f"{prefix}pdf"]

                        lecture.save()
                    except Lecture.DoesNotExist:
                        continue

            except Section.DoesNotExist:
                continue

        return Response({'message': 'Course and related sections/lectures updated successfully'})

    except CourseTable.DoesNotExist:
        return Response({'error': 'Course not found'}, status=status.HTTP_404_NOT_FOUND)
    

from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Assignment
from .serializers import AssignmentSerializer

@api_view(['GET'])
def get_all_assignments(request):
    try:
        assignments = Assignment.objects.all()
        serializer = AssignmentSerializer(assignments, many=True)
        return Response(serializer.data, status=200)
    except Exception as e:
        return Response({'error': str(e)}, status=400)


from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import StudentAssignmentSubmission
from .serializers import StudentAssignmentSubmissionSerializer

@api_view(['GET'])
def get_all_submissions(request):
    try:
        submissions = StudentAssignmentSubmission.objects.all()
        serializer = StudentAssignmentSubmissionSerializer(submissions, many=True)
        return Response(serializer.data, status=200)
    except Exception as e:
        return Response({'error': str(e)}, status=400)

from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import AssignmentResult
from .serializers import AssignmentResultSerializer

@api_view(['GET'])
def get_student_results(request, student_id):
    try:
        results = AssignmentResult.objects.filter(student_id=student_id)
        if not results.exists():
            return Response({'message': 'No results found for this student'}, status=404)

        serializer = AssignmentResultSerializer(results, many=True)
        return Response(serializer.data, status=200)
    except Exception as e:
        return Response({'error': str(e)}, status=400)



@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def counselor_apply(request):
    try:
        logger.info(f"Received request: {request.META.get('CONTENT_TYPE')}")
        trainer_id = request.query_params.get('trainer_id')
        logger.info(f"trainer_id: {trainer_id}")
        if not trainer_id:
            logger.error("trainer_id missing")
            return Response({'error': 'trainer_id is required in query parameters'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            trainer = TrainerData.objects.get(id=trainer_id)
        except TrainerData.DoesNotExist:
            logger.error(f"Trainer with ID {trainer_id} not found")
            return Response({'error': 'Trainer not found'}, status=status.HTTP_404_NOT_FOUND)

        data = request.data
        logger.debug(f"Request data: {data}")
        domains = data.get('domains')
        if isinstance(domains, str):
            try:
                domains = json.loads(domains)
            except json.JSONDecodeError:
                logger.error(f"Invalid domains JSON: {domains}")
                domains = [d.strip() for d in domains.split(',') if d.strip()]

        if not isinstance(domains, list):
            logger.error(f"Domains not a list: {domains}")
            return Response({'error': 'domains must be a list or comma-separated string'}, status=status.HTTP_400_BAD_REQUEST)

        why_interested = data.get('why_interested')
        if not why_interested:
            logger.error("why_interested missing")
            return Response({'error': 'why_interested is required'}, status=status.HTTP_400_BAD_REQUEST)

        availability = data.get('availability')
        if isinstance(availability, str):
            try:
                availability = json.loads(availability)
            except json.JSONDecodeError:
                logger.error(f"Invalid availability JSON: {availability}")
                return Response({'error': 'availability must be valid JSON'}, status=status.HTTP_400_BAD_REQUEST)

        if not isinstance(availability, dict):
            logger.error(f"Availability not a dict: {availability}")
            return Response({'error': 'availability must be a dictionary'}, status=status.HTTP_400_BAD_REQUEST)

        docs = request.FILES.getlist('docs')
        logger.info(f"Received {len(docs)} documents")
        for doc in docs:
            if doc.size > 5 * 1024 * 1024:  # 5MB limit
                logger.error(f"File {doc.name} exceeds 5MB")
                return Response({'error': 'File size exceeds 5MB'}, status=status.HTTP_400_BAD_REQUEST)
            if not doc.name.lower().endswith(('.pdf', '.doc', '.docx')):
                logger.error(f"Invalid file type for {doc.name}")
                return Response({'error': 'Only PDF/DOC files allowed'}, status=status.HTTP_400_BAD_REQUEST)

        application = CounselorApplication.objects.create(
            trainer=trainer,
            domains=domains,
            why_interested=why_interested,
            availability=availability,
            status='Pending'
        )

        uploaded_paths = []
        for doc in docs:
            path = default_storage.save(f'counselor_docs/{application.id}/{doc.name}', doc)
            uploaded_paths.append(path)
            logger.info(f"Saved file: {path}")

        application.uploaded_docs = uploaded_paths
        application.save()
        logger.info(f"Application created with ID: {application.id}")

        return Response({'application_id': application.id}, status=status.HTTP_201_CREATED)

    except Exception as e:
        logger.error(f"Error in counselor_apply: {str(e)}", exc_info=True)
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
@api_view(['GET'])
def get_counselor_applications_admin(request):
    try:
        status_filter = request.query_params.get('status')
        domain_filter = request.query_params.get('domain')

        applications = CounselorApplication.objects.all()

        if status_filter:
            if status_filter not in ['Pending', 'Approved', 'Rejected']:
                return Response({'error': 'Invalid status filter'}, status=status.HTTP_400_BAD_REQUEST)
            applications = applications.filter(status=status_filter)

        if domain_filter:
            applications = applications.filter(domains__contains=[domain_filter])

        serializer = CounselorApplicationSerializer(applications, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Error in get_counselor_applications_admin: {str(e)}")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# counselor_gmt/views.py

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from .models import CounselorApplication, Counselor
from .serializers import CounselorApplicationSerializer
from signup_gmt.models import TrainerData
from django.contrib.auth.models import User
import logging

# Setup logging
logger = logging.getLogger(__name__)

# Placeholder for notification service (SendGrid/Twilio)
def send_notification(email, message, phone=None):
    """
    Placeholder for sending email/SMS notifications using SendGrid/Twilio.
    Configure with your service credentials in production.
    """
    try:
        # Example: SendGrid email
        # from sendgrid import SendGridAPIClient
        # from sendgrid.helpers.mail import Mail
        # sg = SendGridAPIClient('YOUR_SENDGRID_API_KEY')
        # mail = Mail(
        #     from_email='from@example.com',
        #     to_emails=email,
        #     subject='Counselor Application Status Update',
        #     plain_text_content=message
        # )
        # sg.send(mail)
        
        # Example: Twilio SMS
        # from twilio.rest import Client
        # client = Client('TWILIO_ACCOUNT_SID', 'TWILIO_AUTH_TOKEN')
        # client.messages.create(body=message, from_='+1234567890', to=phone)
        
        logger.info(f"Notification sent to {email}: {message}")
        return True
    except Exception as e:
        logger.error(f"Failed to send notification to {email}: {str(e)}")
        return False


        
@api_view(['GET'])
def get_counselor_applications(request):
    try:
        status_filter = request.query_params.get('status')
        domain_filter = request.query_params.get('domain')

        applications = CounselorApplication.objects.all()

        if status_filter:
            if status_filter not in ['Pending', 'Approved', 'Rejected']:
                return Response({'error': 'Invalid status filter'}, status=status.HTTP_400_BAD_REQUEST)
            applications = applications.filter(status=status_filter)

        if domain_filter:
            applications = applications.filter(domains__contains=[domain_filter])

        serializer = CounselorApplicationSerializer(applications, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Error in get_counselor_applications: {str(e)}")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PATCH'])
@parser_classes([MultiPartParser, FormParser])
def update_counselor_application(request, id):
    try:
        try:
            application = CounselorApplication.objects.get(id=id)
        except CounselorApplication.DoesNotExist:
            return Response({'error': 'Application not found'}, status=status.HTTP_404_NOT_FOUND)

        trainer_id = request.query_params.get('trainer_id')
        if not trainer_id or application.trainer.id != int(trainer_id):
            return Response({'error': 'Not authorized to update this application'}, status=status.HTTP_403_FORBIDDEN)

        if application.status != 'Pending':
            return Response({'error': 'Can only update pending applications'}, status=status.HTTP_400_BAD_REQUEST)

        data = request.data
        updated = False

        if 'domains' in data:
            domains = data['domains']
            if isinstance(domains, str):
                try:
                    domains = json.loads(domains)
                except json.JSONDecodeError:
                    return Response({'error': 'domains must be valid JSON'}, status=status.HTTP_400_BAD_REQUEST)
            if isinstance(domains, list):
                application.domains = domains
                updated = True

        if 'why_interested' in data:
            application.why_interested = data['why_interested']
            updated = True

        if 'availability' in data:
            availability = data['availability']
            if isinstance(availability, str):
                try:
                    availability = json.loads(availability)
                except json.JSONDecodeError:
                    return Response({'error': 'availability must be valid JSON'}, status=status.HTTP_400_BAD_REQUEST)
            if isinstance(availability, dict):
                application.availability = availability
                updated = True

        if 'docs' in request.FILES:
            docs = request.FILES.getlist('docs')
            uploaded_paths = application.uploaded_docs.copy() if application.uploaded_docs else []
            for doc in docs:
                if doc.size > 5 * 1024 * 1024:
                    return Response({'error': 'File size exceeds 5MB'}, status=status.HTTP_400_BAD_REQUEST)
                if not doc.name.lower().endswith(('.pdf', '.doc', '.docx')):
                    return Response({'error': 'Only PDF/DOC files allowed'}, status=status.HTTP_400_BAD_REQUEST)
                path = default_storage.save(f'counselor_docs/{application.id}/{doc.name}', doc)
                uploaded_paths.append(path)
            application.uploaded_docs = uploaded_paths
            updated = True

        if updated:
            application.save()
            return Response({'message': 'Application updated successfully'}, status=status.HTTP_200_OK)
        else:
            return Response({'message': 'No updates provided'}, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Error in update_counselor_application: {str(e)}")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        
@api_view(['PATCH'])
def update_counselor_application_status(request, id):
    try:
        try:
            application = CounselorApplication.objects.get(id=id)
        except CounselorApplication.DoesNotExist:
            return Response({'error': 'Application not found'}, status=status.HTTP_404_NOT_FOUND)

        data = request.data
        new_status = data.get('status')
        admin_comments = data.get('comments')

        if new_status not in ['Approved', 'Rejected']:
            return Response({'error': 'Status must be Approved or Rejected'}, status=status.HTTP_400_BAD_REQUEST)

        if not admin_comments:
            return Response({'error': 'Comments are required'}, status=status.HTTP_400_BAD_REQUEST)

        application.status = new_status
        application.admin_comments = admin_comments
        application.save()

        if new_status == 'Approved':
            login_details = application.trainer.login  # This is already a LoginDetails object
            if not Counselor.objects.filter(user=login_details).exists():
                Counselor.objects.create(
                    user=login_details,
                    approved_domains=application.domains
            )


        email = application.trainer.login.email
        message = f"Your counselor application (ID: {application.id}) has been {new_status.lower()}. Comments: {admin_comments}"
        if not send_notification(email, message):
            logger.warning(f"Notification failed for application {application.id}")

        return Response({'message': f'Application {new_status.lower()} successfully'}, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Error in update_counselor_application_status: {str(e)}")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    


@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser, JSONParser])  # Added JSONParser
def submit_counseling_request(request):
    try:
        logger.debug(f"Request data: {request.data}")
        data = request.data
        student_id = data.get('student_id')
        domain = data.get('domain')
        description = data.get('description')
        preferred_times = data.get('preferred_times')
        resume = request.FILES.get('resume')

        if not all([student_id, domain, description, preferred_times]):
            logger.error(f"Missing required fields: student_id={student_id}, domain={domain}, description={description}, preferred_times={preferred_times}")
            return Response({'error': 'student_id, domain, description, and preferred_times are required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            student = StudentInformation.objects.get(id=student_id)
            if student.login.role.role_name != 'student':
                logger.error(f"User with ID {student_id} is not a student")
                return Response({'error': 'User must have student role'}, status=status.HTTP_400_BAD_REQUEST)
        except StudentInformation.DoesNotExist:
            logger.error(f"Student with ID {student_id} not found")
            return Response({'error': 'Student not found'}, status=status.HTTP_404_NOT_FOUND)

        if isinstance(preferred_times, str):
            try:
                preferred_times = json.loads(preferred_times)
            except json.JSONDecodeError as e:
                logger.error(f"Invalid preferred_times JSON: {preferred_times}, error: {str(e)}")
                return Response({'error': 'preferred_times must be valid JSON'}, status=status.HTTP_400_BAD_REQUEST)

        if not isinstance(preferred_times, dict):
            logger.error(f"preferred_times is not a dictionary: {preferred_times}")
            return Response({'error': 'preferred_times must be a dictionary'}, status=status.HTTP_400_BAD_REQUEST)

        if resume:
            if resume.size > 5 * 1024 * 1024:
                logger.error(f"Resume file size exceeds 5MB: {resume.size}")
                return Response({'error': 'Resume file size exceeds 5MB'}, status=status.HTTP_400_BAD_REQUEST)
            if not resume.name.lower().endswith(('.pdf', '.doc', '.docx')):
                logger.error(f"Invalid resume file type: {resume.name}")
                return Response({'error': 'Resume must be PDF/DOC file'}, status=status.HTTP_400_BAD_REQUEST)

        counselors = Counselor.objects.filter(approved_domains__contains=[domain]).order_by('total_sessions')
        matched_counselor = None
        for counselor in counselors:
            latest_application = CounselorApplication.objects.filter(
                trainer__login=counselor.user, status='Approved'
            ).order_by('-updated_at').first()
            if not latest_application:
                continue
            counselor_availability = latest_application.availability
            has_overlap = False
            for day, times in preferred_times.items():
                if day in counselor_availability:
                    if any(time in counselor_availability[day] for time in times):
                        has_overlap = True
                        break
            if has_overlap:
                matched_counselor = counselor
                break

        request_obj = CounselingRequest.objects.create(
            student=student,
            counselor=matched_counselor,
            domain=domain,
            description=description,
            preferred_times=preferred_times,
            status='Assigned' if matched_counselor else 'Pending'
        )

        if resume:
            resume_path = default_storage.save(f'counseling_resumes/{request_obj.id}/{resume.name}', resume)
            request_obj.resume = resume_path
            request_obj.save()

        student_email = student.login.email
        status_message = 'assigned to a counselor' if matched_counselor else 'pending assignment'
        student_message = f"Your counseling request (ID: {request_obj.id}) for {domain} has been {status_message}."
        send_notification(student_email, student_message)

        if matched_counselor:
            counselor_email = matched_counselor.user.email
            counselor_message = f"A new counseling request (ID: {request_obj.id}) for {domain} has been assigned to you."
            send_notification(counselor_email, counselor_message)

        return Response({
            'message': 'Counseling request submitted successfully',
            'request_id': request_obj.id,
            'status': request_obj.status,
            'counselor_id': matched_counselor.id if matched_counselor else None
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        logger.error(f"Error in submit_counseling_request: {str(e)}")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def get_counseling_requests(request):
    try:
        student_id = request.query_params.get('student_id')
        status_filter = request.query_params.get('status')

        if not student_id:
            return Response({'error': 'student_id is required in query parameters'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            student = StudentInformation.objects.get(id=student_id)
            if student.login.role.role_name != 'student':
                return Response({'error': 'User must have student role'}, status=status.HTTP_400_BAD_REQUEST)
        except StudentInformation.DoesNotExist:
            return Response({'error': 'Student not found'}, status=status.HTTP_404_NOT_FOUND)

        requests = CounselingRequest.objects.filter(student=student)

        if status_filter:
            if status_filter not in ['Pending', 'Assigned', 'Completed', 'Cancelled']:
                return Response({'error': 'Invalid status filter'}, status=status.HTTP_400_BAD_REQUEST)
            requests = requests.filter(status=status_filter)

        serializer = CounselingRequestSerializer(requests, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Error in get_counseling_requests: {str(e)}")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

@api_view(['GET'])
def get_available_counselors(request):
    try:
        domain_filter = request.query_params.get('domain')
        logger.debug(f"Domain filter: {domain_filter}")

        counselors = Counselor.objects.all()
        if domain_filter:
            counselors = counselors.filter(approved_domains__contains=[domain_filter])
            logger.debug(f"Filtered counselors by domain '{domain_filter}': {counselors.count()} found")

        serializer = CounselorSerializer(counselors, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Error in get_available_counselors: {str(e)}", exc_info=True)
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# 4

@api_view(['PATCH'])
@parser_classes([JSONParser])
def accept_counseling_request(request, id):
    try:
        try:
            counseling_request = CounselingRequest.objects.get(id=id)
        except CounselingRequest.DoesNotExist:
            logger.error(f"Counseling request with ID {id} not found")
            return Response({'error': 'Counseling request not found'}, status=status.HTTP_404_NOT_FOUND)

        if counseling_request.status != 'Assigned':
            logger.error(f"Counseling request {id} is not in Assigned state: {counseling_request.status}")
            return Response({'error': 'Request must be in Assigned state'}, status=status.HTTP_400_BAD_REQUEST)

        if not counseling_request.counselor:
            logger.error(f"No counselor assigned to request {id}")
            return Response({'error': 'No counselor assigned'}, status=status.HTTP_400_BAD_REQUEST)

        data = request.data
        session_time_str = data.get('session_time')
        if not session_time_str:
            logger.error("session_time is required")
            return Response({'error': 'session_time is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            session_time = datetime.fromisoformat(session_time_str.replace('Z', '+00:00'))
        except ValueError:
            logger.error(f"Invalid session_time format: {session_time_str}")
            return Response({'error': 'session_time must be in ISO format (e.g., 2025-08-26T09:00:00Z)'}, status=status.HTTP_400_BAD_REQUEST)

        # Validate session time against counselor's availability
        latest_application = CounselorApplication.objects.filter(
            trainer__login=counseling_request.counselor.user, status='Approved'
        ).order_by('-updated_at').first()
        if not latest_application:
            logger.error(f"No approved application found for counselor {counseling_request.counselor.id}")
            return Response({'error': 'Counselor has no approved application'}, status=status.HTTP_400_BAD_REQUEST)

        counselor_availability = latest_application.availability
        session_day = session_time.strftime('%A').lower()
        session_hour = session_time.strftime('%H:%M')
        valid_slot = False
        if session_day in counselor_availability:
            for time_slot in counselor_availability[session_day]:
                start_time, end_time = time_slot.split('-')
                if start_time <= session_hour <= end_time:
                    valid_slot = True
                    break

        if not valid_slot:
            logger.error(f"Session time {session_time} not in counselor's availability: {counselor_availability}")
            return Response({'error': 'Session time not in counselor\'s availability'}, status=status.HTTP_400_BAD_REQUEST)

        # Create Jitsi Meet link
        student_email = counseling_request.student.login.email
        counselor_email = counseling_request.counselor.user.email
        try:
            meeting_id, meet_link = create_jitsi_meeting(student_email, counselor_email, session_time, counseling_request.domain)
        except Exception as e:
            logger.error(f"Failed to create Jitsi meeting: {str(e)}")
            return Response({'error': f'Failed to create Jitsi meeting: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Update request
        counseling_request.status = 'Accepted'
        counseling_request.session_time = session_time
        counseling_request.meeting_id = meeting_id
        counseling_request.meet_link = meet_link
        counseling_request.save()

        # Send notifications
        student_message = f"Your counseling request (ID: {id}) has been accepted for {session_time}. Join here: {meet_link}"
        send_notification(student_email, student_message)
        counselor_message = f"You have accepted counseling request (ID: {id}) for {session_time}. Join here: {meet_link}"
        send_notification(counselor_email, counselor_message)

        return Response({
            'message': 'Counseling request accepted successfully',
            'meet_link': meet_link,
            'session_time': session_time.isoformat()
        }, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Error in accept_counseling_request: {str(e)}", exc_info=True)
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
      




@api_view(['PATCH'])
@parser_classes([JSONParser])
def reject_counseling_request(request, id):
    try:
        try:
            counseling_request = CounselingRequest.objects.get(id=id)
        except CounselingRequest.DoesNotExist:
            logger.error(f"Counseling request with ID {id} not found")
            return Response({'error': 'Counseling request not found'}, status=status.HTTP_404_NOT_FOUND)

        if counseling_request.status != 'Assigned':
            logger.error(f"Counseling request {id} is not in Assigned state: {counseling_request.status}")
            return Response({'error': 'Request must be in Assigned state'}, status=status.HTTP_400_BAD_REQUEST)

        if not counseling_request.counselor:
            logger.error(f"No counselor assigned to request {id}")
            return Response({'error': 'No counselor assigned'}, status=status.HTTP_400_BAD_REQUEST)

        data = request.data
        comments = data.get('comments')
        if not comments:
            logger.error("Comments are required for rejection")
            return Response({'error': 'Comments are required'}, status=status.HTTP_400_BAD_REQUEST)

        counseling_request.status = 'Rejected'
        counseling_request.save()

        # Send notification to student
        student_email = counseling_request.student.login.email
        student_message = f"Your counseling request (ID: {id}) has been rejected. Comments: {comments}"
        send_notification(student_email, student_message)

        return Response({'message': 'Counseling request rejected successfully'}, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Error in reject_counseling_request: {str(e)}", exc_info=True)
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@parser_classes([JSONParser])
def submit_counseling_feedback(request, id):
    try:
        try:
            counseling_request = CounselingRequest.objects.get(id=id)
        except CounselingRequest.DoesNotExist:
            logger.error(f"Counseling request with ID {id} not found")
            return Response({'error': 'Counseling request not found'}, status=status.HTTP_404_NOT_FOUND)

        if counseling_request.status != 'Accepted':
            logger.error(f"Counseling request {id} is not in Accepted state: {counseling_request.status}")
            return Response({'error': 'Request must be in Accepted state'}, status=status.HTTP_400_BAD_REQUEST)

        data = request.data
        rating = data.get('rating')
        comments = data.get('comments', '')

        if not isinstance(rating, (int, float)) or not 0 <= rating <= 5:
            logger.error(f"Invalid rating: {rating}")
            return Response({'error': 'Rating must be a number between 0 and 5'}, status=status.HTTP_400_BAD_REQUEST)

        # Create feedback
        feedback = CounselingFeedback.objects.create(
            request=counseling_request,
            rating=rating,
            comments=comments
        )

        # Update counselor's average rating
        counselor = counseling_request.counselor
        if counselor:
            feedback_ratings = CounselingFeedback.objects.filter(request__counselor=counselor).values_list('rating', flat=True)
            counselor.rating = sum(feedback_ratings) / len(feedback_ratings) if feedback_ratings else 0.0
            counselor.total_sessions += 1
            counselor.save()

        # Mark request as Completed
        counseling_request.status = 'Completed'
        counseling_request.save()

        # Send notification to counselor
        counselor_email = counseling_request.counselor.user.email
        counselor_message = f"New feedback received for counseling request (ID: {id}): Rating {rating}/5, Comments: {comments}"
        send_notification(counselor_email, counselor_message)

        return Response({
            'message': 'Feedback submitted successfully',
            'feedback_id': feedback.id
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        logger.error(f"Error in submit_counseling_feedback: {str(e)}", exc_info=True)
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_counseling_session(request, id):
    try:
        try:
            counseling_request = CounselingRequest.objects.get(id=id)
        except CounselingRequest.DoesNotExist:
            logger.error(f"Counseling request with ID {id} not found")
            return Response({'error': 'Counseling request not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = CounselingRequestSerializer(counseling_request)
        return Response(serializer.data, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Error in get_counseling_session: {str(e)}", exc_info=True)
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    


# trainer_gmt/views.py
@api_view(['PATCH'])
@parser_classes([JSONParser])
def complete_counseling_request(request, id):
    try:
        counseling_request = CounselingRequest.objects.get(id=id)
        if counseling_request.status != 'Accepted':
            logger.error(f"Counseling request {id} is not in Accepted state: {counseling_request.status}")
            return Response({'error': 'Request must be in Accepted state'}, status=status.HTTP_400_BAD_REQUEST)
        counseling_request.status = 'Completed'
        counseling_request.save()
        send_notification(
            counseling_request.student.login.email,
            f"Your counseling session (ID: {id}) has been completed."
        )
        send_notification(
            counseling_request.counselor.user.email,
            f"You have completed counseling session (ID: {id})."
        )
        return Response({'message': 'Counseling request marked as completed'}, status=status.HTTP_200_OK)
    except CounselingRequest.DoesNotExist:
        logger.error(f"Counseling request with ID {id} not found")
        return Response({'error': 'Counseling request not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error in complete_counseling_request: {str(e)}", exc_info=True)
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    




#INTERVIEWWW
from rest_framework.decorators import api_view, parser_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import JSONParser
from .models import Interviewer, InterviewerApplication, InterviewRequest, InterviewFeedback
from .serializers import InterviewerApplicationSerializer, InterviewRequestSerializer, InterviewFeedbackSerializer
from signup_gmt.models import StudentInformation, TrainerData
from django.conf import settings
from django.db.models import Value
from django.db.models import JSONField
from datetime import datetime
from django.core.mail import send_mail
import logging

logger = logging.getLogger(__name__)

def send_notification(email, message, phone=None):
    try:
        send_mail(
            subject='GMT LMS Interview Notification',
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )
        logger.info(f"Notification sent to {email}: {message}")
        return True
    except Exception as e:
        logger.error(f"Failed to send notification to {email}: {str(e)}")
        return False

@api_view(['POST'])
@parser_classes([JSONParser])
def interviewer_apply(request):
    try:
        data = request.data.copy()
        trainer_id = data.get('trainer_id')
        if not trainer_id:
            return Response({"error": "trainer_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        if 'id' in data:
            del data['id']
        serializer = InterviewerApplicationSerializer(data=data)
        if serializer.is_valid():
            trainer = TrainerData.objects.get(id=trainer_id)
            serializer.save(trainer=trainer)
            send_notification(trainer.email, "Your interviewer application has been submitted.")
            return Response({"application_id": serializer.data['id'], "message": "Application submitted"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except TrainerData.DoesNotExist:
        logger.error(f"No TrainerData found for trainer_id: {trainer_id}")
        return Response({"error": "Trainer profile not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error in interviewer_apply: {str(e)}")
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['PATCH'])
@parser_classes([JSONParser])
def update_interviewer_application(request, id):
    try:
        data = request.data
        trainer_id = data.get('trainer_id')
        if not trainer_id:
            return Response({"error": "trainer_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        application = InterviewerApplication.objects.get(id=id, trainer__id=trainer_id)
        if application.status != 'Pending':
            return Response({"error": "Only pending applications can be updated"}, status=status.HTTP_400_BAD_REQUEST)
        serializer = InterviewerApplicationSerializer(application, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Application updated"}, status=status.HTTP_200_OK)
        logger.error(f"Serializer errors: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except InterviewerApplication.DoesNotExist:
        return Response({"error": "Application not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error in update_interviewer_application: {str(e)}")
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_interviewer_applications_admin(request):
    try:
        applications = InterviewerApplication.objects.all()
        serializer = InterviewerApplicationSerializer(applications, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error in get_interviewer_applications_admin: {str(e)}")
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['PATCH'])
@parser_classes([JSONParser])
def update_interviewer_application_status(request, id):
    try:
        application = InterviewerApplication.objects.get(id=id)
        serializer = InterviewerApplicationSerializer(application, data=request.data, partial=True)
        if serializer.is_valid():
            logger.info(f"Updating application {id} with data: {request.data}, domains: {application.domains}")
            serializer.save()
            application.refresh_from_db()
            if application.status == 'Approved':
                existing_interviewer = Interviewer.objects.filter(user=application.trainer.login).first()
                if not existing_interviewer:
                    Interviewer.objects.create(
                        user=application.trainer.login,
                        approved_domains=application.domains or []
                    )
                    logger.info(f"Created Interviewer for user {application.trainer.login.username} with domains {application.domains}")
                else:
                    existing_interviewer.approved_domains = application.domains or []
                    existing_interviewer.save()
                    logger.info(f"Updated Interviewer for user {application.trainer.login.username} with domains {application.domains}")
                send_notification(application.trainer.email, "Your interviewer application has been approved.")
            elif application.status == 'Rejected':
                send_notification(application.trainer.email, f"Your interviewer application was rejected: {request.data.get('comments', '')}")
            return Response({"message": f"Application {application.status.lower()}"}, status=status.HTTP_200_OK)
        logger.error(f"Serializer errors: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except InterviewerApplication.DoesNotExist:
        logger.error(f"Application with ID {id} not found")
        return Response({"error": "Application not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error in update_interviewer_application_status: {str(e)}")
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_available_interviewers(request):
    try:
        domain = request.query_params.get('domain')
        if domain:
            interviewers = Interviewer.objects.filter(
                approved_domains__contains=Value(domain, output_field=JSONField())
            )
        else:
            interviewers = Interviewer.objects.all()
        
        response_data = []
        for i in interviewers:
            application = InterviewerApplication.objects.filter(trainer__login=i.user, status='Approved').first()
            if not application:
                logger.warning(f"No approved application found for interviewer {i.user.username}")
                continue
            response_data.append({
                'id': i.id,
                'name': i.user.username,
                'domains': i.approved_domains or [],
                'availability': application.availability
            })
        logger.info(f"Returning {len(response_data)} interviewers for domain: {domain or 'all'}")
        return Response(response_data, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error in get_available_interviewers: {str(e)}")
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@parser_classes([JSONParser])
def submit_interview_request(request):
    try:
        data = request.data
        student_id = data.get('student_id')
        if not student_id:
            return Response({"error": "student_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            student = StudentInformation.objects.get(id=student_id)
        except StudentInformation.DoesNotExist:
            logger.error(f"No StudentInformation found for student_id: {student_id}")
            return Response({"error": "Student profile not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = InterviewRequestSerializer(data=data)
        if serializer.is_valid():
            serializer.save(student_id=student_id)
            interviewer = Interviewer.objects.filter(
                approved_domains__contains=Value(data['domain'], output_field=JSONField())
            ).first()
            if interviewer:
                serializer.instance.interviewer = interviewer
                serializer.instance.status = 'Assigned'
                serializer.instance.save()
                send_notification(interviewer.user.email, f"New interview request (ID: {serializer.instance.id}) assigned to you.")
            send_notification(student.email, f"Your interview request (ID: {serializer.instance.id}) has been submitted.")
            return Response({
                "message": "Request submitted",
                "request_id": serializer.data['id'],
                "status": serializer.instance.status,
                "interviewer_id": interviewer.id if interviewer else None
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Error in submit_interview_request: {str(e)}")
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_interview_requests(request):
    try:
        user_type = request.query_params.get('user_type')
        user_id = request.query_params.get('user_id')
        if not user_type or not user_id:
            return Response({"error": "user_type and user_id are required"}, status=status.HTTP_400_BAD_REQUEST)
        if user_type == 'student':
            requests = InterviewRequest.objects.filter(student_id=user_id)
        elif user_type == 'interviewer':
            requests = InterviewRequest.objects.filter(interviewer__id=user_id)
        else:
            return Response({"error": "Invalid user_type"}, status=status.HTTP_400_BAD_REQUEST)
        serializer = InterviewRequestSerializer(requests, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error in get_interview_requests: {str(e)}")
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['PATCH'])
@parser_classes([JSONParser])
def accept_interview_request(request, id):
    try:
        data = request.data
        interviewer_id = data.get('interviewer_id')
        if not interviewer_id:
            return Response({"error": "interviewer_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Modified query to allow null interviewer
        interview_request = InterviewRequest.objects.get(id=id)
        if interview_request.interviewer and interview_request.interviewer.id != int(interviewer_id):
            return Response({"error": "Interviewer ID does not match assigned interviewer"}, status=status.HTTP_400_BAD_REQUEST)
        
        if interview_request.status not in ['Pending', 'Assigned']:
            return Response({"error": "Request must be in Pending or Assigned state"}, status=status.HTTP_400_BAD_REQUEST)
        
        session_time_str = data.get('session_time')
        if not session_time_str:
            return Response({"error": "session_time is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        session_time = datetime.fromisoformat(session_time_str.replace('Z', '+00:00'))
        interviewer = Interviewer.objects.get(id=interviewer_id)
        application = InterviewerApplication.objects.filter(trainer__login=interviewer.user, status='Approved').first()
        if not application:
            return Response({"error": "No approved application found"}, status=status.HTTP_400_BAD_REQUEST)
        
        session_day = session_time.strftime('%A').lower()
        session_hour = session_time.strftime('%H:%M')
        if session_day not in application.availability or not any(
            start_time <= session_hour <= end_time 
            for start_time, end_time in [(t.split('-')[0], t.split('-')[1]) for t in application.availability[session_day]]
        ):
            return Response({"error": "Session time not in interviewer's availability"}, status=status.HTTP_400_BAD_REQUEST)


        room_name = f"gmt-interview-{session_time.isoformat().replace(':', '-')}-{interview_request.domain.lower()}"
        meet_link = f"{settings.JITSI_SERVER_URL}/{room_name}"
        interview_request.status = 'Accepted'
        interview_request.session_time = session_time
        interview_request.meeting_id = room_name
        interview_request.meet_link = meet_link
        interview_request.interviewer = interviewer  # Assign interviewer if not already set
        interview_request.save()
        
        student = StudentInformation.objects.get(id=interview_request.student_id)
        send_notification(student.email, f"Your interview request (ID: {id}) is accepted for {session_time}. Join: {meet_link}. Password: interview123")
        send_notification(interviewer.user.email, f"You accepted interview request (ID: {id}) for {session_time}. Join: {meet_link}. Password: interview123")
        return Response({"message": "Request accepted", "meet_link": meet_link, "session_time": session_time.isoformat()}, status=status.HTTP_200_OK)
    except InterviewRequest.DoesNotExist:
        return Response({"error": "Request not found"}, status=status.HTTP_404_NOT_FOUND)
    except Interviewer.DoesNotExist:
        return Response({"error": "Interviewer not found"}, status=status.HTTP_404_NOT_FOUND)
    except StudentInformation.DoesNotExist:
        logger.error(f"No StudentInformation found for student_id: {interview_request.student_id}")
        return Response({"error": "Student profile not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error in accept_interview_request: {str(e)}")
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    
@api_view(['PATCH'])
@parser_classes([JSONParser])
def reject_interview_request(request, id):
    try:
        data = request.data
        interviewer_id = data.get('interviewer_id')
        if not interviewer_id:
            return Response({"error": "interviewer_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        interview_request = InterviewRequest.objects.get(id=id, interviewer__id=interviewer_id)
        if interview_request.status != 'Assigned':
            return Response({"error": "Request must be in Assigned state"}, status=status.HTTP_400_BAD_REQUEST)
        interview_request.status = 'Rejected'
        interview_request.save()
        student = StudentInformation.objects.get(id=interview_request.student_id)
        send_notification(student.email, f"Your interview request (ID: {id}) was rejected: {data.get('comments', '')}")
        return Response({"message": "Request rejected"}, status=status.HTTP_200_OK)
    except InterviewRequest.DoesNotExist:
        return Response({"error": "Request not found"}, status=status.HTTP_404_NOT_FOUND)
    except StudentInformation.DoesNotExist:
        logger.error(f"No StudentInformation found for student_id: {interview_request.student_id}")
        return Response({"error": "Student profile not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error in reject_interview_request: {str(e)}")
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_interview_session(request, id):
    try:
        interview_request = InterviewRequest.objects.get(id=id)
        serializer = InterviewRequestSerializer(interview_request)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except InterviewRequest.DoesNotExist:
        logger.error(f"Interview request with ID {id} not found")
        return Response({"error": "Interview request not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error in get_interview_session: {str(e)}")
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['PATCH'])
@parser_classes([JSONParser])
def complete_interview_request(request, id):
    try:
        data = request.data
        interviewer_id = data.get('interviewer_id')
        if not interviewer_id:
            return Response({"error": "interviewer_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        interview_request = InterviewRequest.objects.get(id=id, interviewer__id=interviewer_id)
        if interview_request.status != 'Accepted':
            return Response({"error": "Request must be in Accepted state"}, status=status.HTTP_400_BAD_REQUEST)
        interview_request.status = 'Completed'
        interview_request.save()
        student = StudentInformation.objects.get(id=interview_request.student_id)
        send_notification(student.email, f"Your interview session (ID: {id}) has been completed.")
        send_notification(interview_request.interviewer.user.email, f"You completed interview session (ID: {id}).")
        return Response({"message": "Interview completed"}, status=status.HTTP_200_OK)
    except InterviewRequest.DoesNotExist:
        return Response({"error": "Request not found"}, status=status.HTTP_404_NOT_FOUND)
    except StudentInformation.DoesNotExist:
        logger.error(f"No StudentInformation found for student_id: {interview_request.student_id}")
        return Response({"error": "Student profile not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error in complete_interview_request: {str(e)}")
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@parser_classes([JSONParser])
def submit_interview_feedback(request, id):
    try:
        data = request.data
        student_id = data.get('student_id')
        if not student_id:
            return Response({"error": "student_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        interview_request = InterviewRequest.objects.get(id=id, student_id=student_id)
        if interview_request.status != 'Completed':
            return Response({"error": "Request must be in Completed state"}, status=status.HTTP_400_BAD_REQUEST)
        serializer = InterviewFeedbackSerializer(data={'request': id, 'rating': data.get('rating'), 'comments': data.get('comments', '')})
        if serializer.is_valid():
            serializer.save()
            send_notification(interview_request.interviewer.user.email, f"Feedback received for interview (ID: {id}): Rating {data.get('rating')}, Comments: {data.get('comments', '')}")
            return Response({"message": "Feedback submitted"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except InterviewRequest.DoesNotExist:
        return Response({"error": "Request not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error in submit_interview_feedback: {str(e)}")
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

