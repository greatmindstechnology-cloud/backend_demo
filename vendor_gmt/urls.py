from django.urls import path
from .views import create_vendor_internship,create_vendor_event,get_all_vendor_internships, get_all_vendor_events,update_internship_status,update_event_status,internship_status_counts, event_status_counts,get_internship_by_id,create_csrevent,create_blood_need,get_all_blood_needs,update_request_status,get_all_events
urlpatterns = [
    path('vendor-internship/create/', create_vendor_internship, name='create_vendor_internship'),
    path('vendor-event/create/' , create_vendor_event , name='create_vendor_event'),
    path('vendor-internships/', get_all_vendor_internships, name='get_all_vendor_internships'),
    path('vendor-events/', get_all_vendor_events, name='get_all_vendor_events'),
    path('internship/status/', update_internship_status, name='update_internship_status'),
    path('event/status/', update_event_status, name='update_event_status'),
    path('internship/status-counts/', internship_status_counts, name='internship_status_counts'),
    path('event/status-counts/', event_status_counts, name='event_status_counts'),
    path('api/internship/<int:id>/', get_internship_by_id, name='get_internship'),
    path("create/create_csrevent/", create_csrevent, name="create-csrevent"),
    path("get_all/get_csrevent/", get_all_events, name="get-all-events"),
    path("create/blood_need", create_blood_need, name="create-blood-need"),
    path("get_all/blood_need", get_all_blood_needs, name="get-all-blood-need"),
    path("update/<int:pk>/", update_request_status, name="update-blood-status"),



]

