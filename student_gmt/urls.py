from django.urls import path
from .views import get_all_courses,get_all_topics,get_quiz_questions_by_topic,submit_student_answer,calculate_student_result,StudentBookingCreateView,DeleteBookingByStudentID

urlpatterns = [
    path('all-courses/', get_all_courses, name='get_all_courses'),
    path('topics/', get_all_topics, name='get_all_topics'),
    path('quiz-questions/', get_quiz_questions_by_topic, name='get_quiz_questions_by_topic'),
    path('submit-answer/', submit_student_answer),
    path('calculate-result/', calculate_student_result),
    path('api/student-booking/', StudentBookingCreateView.as_view(), name='student-booking-create'),
    path('api/student-booking/delete-by-student/<int:student_id>/', DeleteBookingByStudentID.as_view(), name='delete-booking-by-student'),
]


