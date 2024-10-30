from rest_framework.routers import DefaultRouter

from authentication.views import UserViewSet, UserRoleViewSet
from board.views import BoardViewSet
from column.views import ColumnViewSet
from comment.views import CommentViewSet
from priority.views import PriorityViewSet
from project.views import ProjectViewSet, ProjectMembersViewSet
from report.views import ReportViewSet
from tag.views import TagViewSet
from task.views import TaskViewSet

router = DefaultRouter()

router.register('auth', UserViewSet)
router.register('role', UserRoleViewSet)
router.register('board', BoardViewSet)
router.register('column', ColumnViewSet)
router.register('comment', CommentViewSet)
router.register('priority', PriorityViewSet)
router.register('project', ProjectViewSet)
router.register('members', ProjectMembersViewSet)
router.register('report', ReportViewSet)
router.register('tag', TagViewSet)
router.register('task', TaskViewSet)
