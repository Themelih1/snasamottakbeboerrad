from django.urls import path, include
from django.utils.translation import gettext_lazy as _
from .views import (
    index, ActivityListView, ActivityDetailView, 
    BlogPostListView, BlogPostDetailView,
    ParticipationCreateView, participation_success,
    calendar_view, verify_participation
)
app_name = 'core'

urlpatterns = [
    path('', index, name='index'),
    path(_('aktiviteter/'), ActivityListView.as_view(), name='activities'),
    path(_('aktiviteter/<int:pk>/'), ActivityDetailView.as_view(), name='activity_detail'),
    path(_('blogg/'), BlogPostListView.as_view(), name='blog'),
    path(_('blogg/<int:pk>/'), BlogPostDetailView.as_view(), name='blog_detail'),
    path(_('aktiviteter/<int:pk>/deltakelse/'), ParticipationCreateView.as_view(), name='participation'),
    path(_('deltakelse/suksess/<int:pk>/'), participation_success, name='participation_success'),  # burası değişti
    path(_('kalender/'), calendar_view, name='calendar'),
    path('tinymce/', include('tinymce.urls')),
    path("verify/<int:pk>/<uuid:token>/", verify_participation, name="verify_participation"),
    path('verify-participation/<int:pk>/<str:token>/', verify_participation, name='verify_participation'),
]


