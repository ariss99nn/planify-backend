# analitica/urls/analitica_urls.py
from django.urls import path
from analitica.views.dashboard_view import DashboardView
from analitica.views.snapshot_list_view import SnapshotListView

analitica_urlpatterns = [
    path('',           DashboardView.as_view(),    name='dashboard'),
    path('snapshots/', SnapshotListView.as_view(), name='snapshot-list'),
]