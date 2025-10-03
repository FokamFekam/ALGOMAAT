from django.urls import path

from . import views

app_name = "calendarapp"


urlpatterns = [
    path("calender/", views.CalendarViewNew.as_view(), name="calendar"),
    path("calenders/", views.CalendarView.as_view(), name="calendars"),
    path('delete_event/<int:event_id>/', views.delete_event, name='delete_event'),
    path('next_week/<int:event_id>/', views.next_week, name='next_week'),
    path('next_day/<int:event_id>/', views.next_day, name='next_day'),
    path('event_all_weeks/', views.event_all_weeks, name='event_all_weeks'),
    path("event/new/", views.create_event, name="event_new"),
    path("event/edit/<int:pk>/", views.EventEdit.as_view(), name="event_edit"),
    #path("event/<int:event_id>/details/", views.event_details, name="event-detail"),
    path("event/details/<int:event_id>", views.event_details, name="event-detail"),
    path("event/themes/", views.event_themes, name="event-themes"),
    
    path("create_file/<event_id>/<nodetype_id>/", views.create_file, name="event_create_file"),
    path("create_link/<event_id>/<nodetype_id>/", views.create_link, name="event_create_link"),
    path(
        "add_eventmember/<int:event_id>", views.add_eventmember, name="add_eventmember"
    ),
    path(
        "event/<int:pk>/remove",
        views.EventMemberDeleteView.as_view(),
        name="remove_event",
    ),
    path("all-event-list/", views.AllEventsListView.as_view(), name="all_events"),
    path(
        "running-event-list/",
        views.RunningEventsListView.as_view(),
        name="running_events",
    ),
    path(
        "add_meeting/<int:publication_id>", views.add_meeting, name="add_meeting"
    ),
    path(
        "update_meeting_link/", views.update_meeting_link, name="update_meeting_link"
    ),
    path(
        "save_event_theme/", views.save_event_theme, name="save_event_theme"
    ),
]
