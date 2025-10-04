from django.http import JsonResponse
from course_gmt.models import CourseTable
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from signup_gmt.models import StudentInformation
from trainer_gmt.models import QuizQuestion, StudentResponse,StudentResult
import traceback
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from trainer_gmt.models import Topic  # Adjust import if model is in another app
from .serializers import TopicSerializer 

def get_all_courses(request):
    try:
        courses = CourseTable.objects.all()
        course_list = []

        for course in courses:
            course_list.append({
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
                'trainer': str(course.trainer) if course.trainer else None,
            })

        return JsonResponse({'courses': course_list}, status=200)
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
 # Ensure you create this serializer

@api_view(['GET'])
def get_all_topics(request):
    try:
        topics = Topic.objects.filter(is_active=True).order_by('-created_at')
        serializer = TopicSerializer(topics, many=True)
        return Response({'topics': serializer.data}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from trainer_gmt.models import QuizQuestion, Topic
from .serializers import QuizQuestionSerializer  # Make sure to create this

@api_view(['GET'])
def get_quiz_questions_by_topic(request):
    try:
        topic_id = request.query_params.get('topic_id')
        if not topic_id:
            return Response({'error': 'topic_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            topic = Topic.objects.get(pk=topic_id)
        except Topic.DoesNotExist:
            return Response({'error': 'Topic not found'}, status=status.HTTP_404_NOT_FOUND)

        questions = QuizQuestion.objects.filter(topic=topic)
        serializer = QuizQuestionSerializer(questions, many=True)
        return Response({'questions': serializer.data}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def submit_student_answer(request):
    try:
        student_id = request.query_params.get('student_id')

        if not student_id:
            return Response({'error': 'student_id is required as a query parameter'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            student = StudentInformation.objects.get(id=student_id)
        except StudentInformation.DoesNotExist:
            return Response({'error': 'Student not found'}, status=status.HTTP_404_NOT_FOUND)

        answers = request.data  # Direct list
        if not isinstance(answers, list) or not answers:
            return Response({'error': 'Expected a list of answers'}, status=status.HTTP_400_BAD_REQUEST)

        response_data = []

        for ans in answers:
            question_id = ans.get('question_id')
            selected_option = ans.get('selected_option')

            if not question_id or selected_option not in [1, 2, 3, 4]:
                response_data.append({
                    'question_id': question_id,
                    'error': 'Invalid question_id or selected_option'
                })
                continue

            try:
                question = QuizQuestion.objects.get(id=question_id)
            except QuizQuestion.DoesNotExist:
                response_data.append({
                    'question_id': question_id,
                    'error': 'Question not found'
                })
                continue

            if StudentResponse.objects.filter(student=student, question=question).exists():
                response_data.append({
                    'question_id': question_id,
                    'error': 'Already submitted'
                })
                continue

            is_correct = selected_option == question.correct_option
            marks_obtained = question.marks if is_correct else 0

            StudentResponse.objects.create(
                student=student,
                topic=question.topic,
                question=question,
                selected_option=selected_option,
                is_correct=is_correct,
                marks_obtained=marks_obtained
            )

            response_data.append({
                'question_id': question_id,
                'is_correct': is_correct,
                'marks_obtained': marks_obtained
            })

        return Response({'results': response_data}, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({
            'error': str(e),
            'traceback': traceback.format_exc()
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def calculate_student_result(request):
    try:
        student_id = request.query_params.get('student_id')
        topic_id = request.query_params.get('topic_id')

        if not student_id or not topic_id:
            return Response({'error': 'student_id and topic_id are required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            student = StudentInformation.objects.get(id=student_id)
        except StudentInformation.DoesNotExist:
            return Response({'error': 'Student not found'}, status=status.HTTP_404_NOT_FOUND)

        try:
            topic = Topic.objects.get(id=topic_id)
        except Topic.DoesNotExist:
            return Response({'error': 'Topic not found'}, status=status.HTTP_404_NOT_FOUND)

        responses = StudentResponse.objects.filter(student=student, topic=topic).select_related('question')
        if not responses.exists():
            return Response({'error': 'No responses found for this student on this topic'}, status=status.HTTP_400_BAD_REQUEST)

        total_score = sum(r.marks_obtained for r in responses)
        total_possible_marks = sum(r.question.marks for r in responses)

        percentage = (total_score / total_possible_marks) * 100 if total_possible_marks > 0 else 0

        if percentage >= 90:
            grade = 'A+'
        elif percentage >= 75:
            grade = 'A'
        elif percentage >= 60:
            grade = 'B'
        elif percentage >= 50:
            grade = 'C'
        else:
            grade = 'F'

        if StudentResult.objects.filter(student=student, topic=topic).exists():
            return Response({'error': 'Result already calculated for this topic'}, status=status.HTTP_400_BAD_REQUEST)

        result = StudentResult.objects.create(
            student=student,
            topic=topic,
            total_score=total_score,
            grade=grade,
            total_possible_marks=total_possible_marks,
            percentage=round(percentage, 2)
        )

        return Response({
            'message': 'Result calculated and saved successfully',
            'total_score': total_score,
            'total_possible_marks': total_possible_marks,
            'percentage': round(percentage, 2),
            'grade': grade
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import StudentBooking
from .serializers import StudentBookingSerializer
from django.core.mail import send_mail



class StudentBookingCreateView(APIView):
    def post(self, request):
        serializer = StudentBookingSerializer(data=request.data)
        if serializer.is_valid():
            booking = StudentBooking(**serializer.validated_data)
            booking.save() 
            send_mail(
                subject="Internship Registration Confirmation",
                message=f"Hello {booking.student_name},\n\n"
                        f"You have successfully registered for the internship.\n"
                        f"Your booking ID is {booking.booking_id}.",
                from_email=None,  # uses DEFAULT_FROM_EMAIL
                recipient_list=[booking.email],  # assumes your model has an 'email' field
                fail_silently=False,
            ) # triggers auto-fill and booking_id generation
            return Response(StudentBookingSerializer(booking).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
# from .models import StudentBooking

# class DeleteBookingByStudentID(APIView):
#     def delete(self, request, student_id):
#         try:
#             booking = StudentBooking.objects.get(student_id=student_id)
#             booking.delete()
#             return Response({"message": f"Booking for student ID {student_id} deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
#         except StudentBooking.DoesNotExist:
#             return Response({"error": "No booking found for this student ID."}, status=status.HTTP_404_NOT_FOUND)

# views.py
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
# from .models import StudentBooking

# class DeleteBookingByStudentID(APIView):
#     def delete(self, request, student_id):
#         try:
#             # Validate student_id is integer and exists
#             if not student_id:
#                 return Response({"error": "student_id is required."}, status=status.HTTP_400_BAD_REQUEST)

#             # Try to get booking
#             booking = StudentBooking.objects.filter(student_id=student_id).first()

#             if booking:
#                 booking.delete()
#                 return Response(
#                     {"message": f"Booking for student ID {student_id} deleted successfully."},
#                     status=status.HTTP_204_NO_CONTENT
#                 )
#             else:
#                 return Response(
#                     {"error": f"No booking found for student ID {student_id}."},
#                     status=status.HTTP_404_NOT_FOUND
#                 )

#         except Exception as e:
#             # Catch-all to prevent 500 error
#             return Response(
#                 {"error": "Internal server error", "details": str(e)},
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR
#             )


# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import StudentBooking

class DeleteBookingByStudentID(APIView):
    def delete(self, request, student_id):
        try:
            # Get all bookings for this student
            bookings = StudentBooking.objects.filter(student_id=student_id)
            count = bookings.count()

            if count == 0:
                return Response(
                    {"error": f"No bookings found for student ID {student_id}."},
                    status=status.HTTP_404_NOT_FOUND
                )

            # Delete all
            bookings.delete()

            return Response(
                {"message": f"Deleted {count} booking(s) for student ID {student_id}."},
                status=status.HTTP_204_NO_CONTENT
            )

        except Exception as e:
            return Response(
                {"error": "Internal server error", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
