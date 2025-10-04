from django.urls import path
from .views import get_course_details_by_query_param,update_course_status,get_all_courses,submit_course_feedback,get_feedback_by_course_id,create_project,get_projects_by_course,Project_submit_CreateAPIView,Project_submit_viewAPIView,TaskCreateAPIView,get_tasks_by_course,submit_task,enroll_student_in_course,get_student_courses,get_multiple_courses
urlpatterns = [
    path('course/details/', get_course_details_by_query_param),
    path('update-course-status/', update_course_status, name='update_course_status'),
    path('courses/', get_all_courses, name='get_all_courses'),
    path('api/feedback/', submit_course_feedback, name='submit_course_feedback'),
    path('api/feedback/course/<int:course_id>/', get_feedback_by_course_id),
    path('projects/create/',create_project, name='create-project'),
    path('get/<int:course_id>/projects/', get_projects_by_course, name='projects-by-course'),
    path('api/project_submit/', Project_submit_CreateAPIView.as_view(), name='student-project-create'),
    path('get/project_submit/<int:project_id>/', Project_submit_viewAPIView.as_view(), name='student-project-by-project'),
    path('api/tasks/', TaskCreateAPIView.as_view(), name='task-create'),
    path('get/tasks/<int:course_id>/', get_tasks_by_course, name='get-tasks-by-course'), 
    path('api/task-submit/', submit_task, name='submit-task'),
    path("post/student_course/", enroll_student_in_course, name="enroll-student"),
    path("getstudent/<int:student_id>/student_courses/", get_student_courses, name="student-courses"),
    path("courses/get-multiple/",get_multiple_courses, name="get-multiple-courses"),
    
]
 
