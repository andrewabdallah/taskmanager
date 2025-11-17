from rest_framework.routers import DefaultRouter

from tasks.views import TaskViewSet

router = DefaultRouter()
router.register("tasks", TaskViewSet, basename="task")
router.register("tasks/recent", TaskViewSet, basename="recent-tasks")

urlpatterns = router.urls
