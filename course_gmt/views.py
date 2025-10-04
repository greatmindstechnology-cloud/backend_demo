from rest_framework.decorators import api_view,parser_classes
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
from .models import CourseTable, Section, Lecture ,Project,CourseFeedback,Project_submit,TaskTable,TaskSubmit,StudentCourse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import logging
from .serializers import ProjectSerializer ,CourseFeedbackSerializer,Project_submit_Serializer,TaskSerializer,TaskSubmitSerializer,StudentCourseSerializer,CourseTableSerializer

@api_view(['GET'])
def get_course_details_by_query_param(request):
    course_id = request.query_params.get('course_id')
    
    if not course_id:
        return Response({'error': 'course_id is required as a query parameter'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        course = CourseTable.objects.get(course_id=course_id)

        # Get all sections for the course
        sections = Section.objects.filter(course=course).order_by('order')
        section_list = []

        for section in sections:
            # Get all lectures for the section
            lectures = Lecture.objects.filter(section=section).order_by('order')
            lecture_list = []

            for lecture in lectures:
                lecture_list.append({
                    'id': lecture.id,
                    'title': lecture.title,
                    'duration': str(lecture.duration),
                    'completed': lecture.completed,
                    'active': lecture.active,
                    'order': lecture.order,
                    'video_file': lecture.video_file.url if lecture.video_file else None
                })

            section_list.append({
                'id': section.id,
                'section_title': section.section_title,
                'order': section.order,
                'lectures': lecture_list
            })
        course_data = {
            'course_id': course.course_id,
            'course_title': course.course_title,
            'course_price': str(course.course_price),
            'course_description': course.course_description,
            'course_rating': course.course_rating,
            'about_course': course.about_course,
            'total_students_enrolled': course.total_students_enrolled,
            'course_specification': course.course_specification,
            'preknowledge': course.preknowledge,
            'why_this_course': course.why_this_course,
            'course_image': course.course_image.url if course.course_image else None,
            'status': course.status,
            'sections': section_list
        }

        return Response(course_data)

    except CourseTable.DoesNotExist:
        return Response({'error': 'Course not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['PUT'])
def update_course_status(request):
    try:
        data = request.data
        course_id = data.get('course_id')
        course_title = data.get('course_title')
        new_status = data.get('status')

        if new_status not in ['approved', 'rejected']:
            return Response({"error": "Status must be either 'approved' or 'rejected'."}, status=status.HTTP_400_BAD_REQUEST)

        if not course_id and not course_title:
            return Response({"error": "Either 'course_id' or 'course_title' is required."}, status=status.HTTP_400_BAD_REQUEST)

        course = None
        if course_id:
            course = CourseTable.objects.filter(course_id=course_id).first()
        elif course_title:
            course = CourseTable.objects.filter(course_title=course_title).first()

        if not course:
            return Response({"error": "Course not found."}, status=status.HTTP_404_NOT_FOUND)

        course.status = new_status
        course.save()

        return Response({"message": f"Course status updated to '{new_status}'."}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



logger = logging.getLogger(__name__)

@csrf_exempt
def get_all_courses(request):
    if request.method == 'GET':
        try:
            courses = CourseTable.objects.all()
            course_list = []

            for course in courses:
                course_data = {
                    'course_id': course.course_id,
                    'course_title': course.course_title,
                    'course_price': float(course.course_price),
                    'course_description': course.course_description,
                    'course_rating': course.course_rating,
                    'about_course': course.about_course,
                    'total_students_enrolled': course.total_students_enrolled,
                    'course_specification': course.course_specification,
                    'preknowledge': course.preknowledge,
                    'why_this_course': course.why_this_course,
                    'status': course.status,
                    'course_image': course.course_image.url if course.course_image else None,
                    'trainer_id': course.trainer.id if course.trainer else None,
                }
                course_list.append(course_data)

            return JsonResponse({
                "status": "success",
                "message": "Courses retrieved successfully",
                "data": course_list
            }, status=200)

        except Exception as e:
            logger.error(f"Error while fetching courses: {str(e)}")
            return JsonResponse({
                "status": "error",
                "message": "An error occurred while retrieving courses",
                "error": str(e)
            }, status=500)

    else:
        return JsonResponse({
            "status": "error",
            "message": "Method not allowed. Use GET."
        }, status=405)


@api_view(['POST'])
def submit_course_feedback(request):
    try:
        serializer = CourseFeedbackSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_feedback_by_course_id(request, course_id):
    feedbacks = CourseFeedback.objects.filter(course_id=course_id)
    if feedbacks.exists():
        serializer = CourseFeedbackSerializer(feedbacks, many=True)
        return Response(serializer.data, status=200)
    return Response({'error': 'No feedback found for this course'}, status=404)


# Create project
@api_view(['POST'])
def create_project(request):
    serializer = ProjectSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def get_projects_by_course(request, course_id):
    projects = Project.objects.filter(course_id=course_id)
    if not projects.exists():
        return Response({"message": "No projects found for this course"}, status=status.HTTP_404_NOT_FOUND)

    serializer = ProjectSerializer(projects, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)




class Project_submit_CreateAPIView(APIView):
    def post(self, request):
        serializer = Project_submit_Serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"status": True, "message": "Student project created successfully!", "data": serializer.data},
                status=status.HTTP_201_CREATED
            )
        return Response(
            {"status": False, "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )



class Project_submit_viewAPIView(APIView):
    def get(self, request, project_id):
        student_projects = Project_submit.objects.filter(project_id=project_id)
        if not student_projects.exists():
            return Response(
                {"status": False, "message": "No student projects found for this project"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = Project_submit_Serializer(student_projects, many=True)
        return Response(
            {"status": True, "data": serializer.data},
            status=status.HTTP_200_OK
        )

class TaskCreateAPIView(APIView):
    def post(self, request):
        serializer = TaskSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"status": True, "message": "Task created successfully!", "data": serializer.data},
                status=status.HTTP_201_CREATED
            )
        return Response(
            {"status": False, "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )

@api_view(['GET'])
def get_tasks_by_course(request, course_id):
    tasks = TaskTable.objects.filter(course_id=course_id)
    if not tasks.exists():
        return Response(
            {"status": False, "message": "No tasks found for this course"},
            status=status.HTTP_404_NOT_FOUND
        )

    serializer = TaskSerializer(tasks, many=True)
    return Response(
        {"status": True, "data": serializer.data},
        status=status.HTTP_200_OK
    )
from rest_framework.decorators import api_view, parser_classes

from rest_framework.parsers import MultiPartParser, FormParser


@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])  # allows file upload
def submit_task(request):
    serializer = TaskSubmitSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(
            {"status": True, "message": "Task submitted successfully!", "data": serializer.data},
            status=status.HTTP_201_CREATED
        )
    return Response(
        {"status": False, "errors": serializer.errors},
        status=status.HTTP_400_BAD_REQUEST
    )

@api_view(["POST"])
def enroll_student_in_course(request):
    serializer = StudentCourseSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"status": True, "message": "Student enrolled successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
    return Response({"status": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

@api_view(["GET"])
def get_student_courses(request, student_id):
    enrollments = StudentCourse.objects.filter(student_id=student_id)
    if not enrollments.exists():
        return Response(
            {"status": False, "message": "No courses found for this student"},
            status=status.HTTP_404_NOT_FOUND
        )
    
    course_ids = enrollments.values_list("course_id", flat=True)
    return Response({"status": True, "student_id": student_id, "course_ids": list(course_ids)})

@api_view(["POST"])
def get_multiple_courses(request):
    course_ids = request.data.get("course_ids", [])

    if not course_ids or not isinstance(course_ids, list):
        return Response(
            {"status": False, "message": "course_ids must be provided as a list"},
            status=status.HTTP_400_BAD_REQUEST
        )

    courses = CourseTable.objects.filter(course_id__in=course_ids)
    if not courses.exists():
        return Response(
            {"status": False, "message": "No courses found for given IDs"},
            status=status.HTTP_404_NOT_FOUND
        )

    serializer = CourseTableSerializer(courses, many=True)
    return Response({"status": True, "courses": serializer.data})
