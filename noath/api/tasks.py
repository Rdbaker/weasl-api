"""API routes for tasks."""

from flask import Blueprint, jsonify, request, g

from noath.task.models import Task
from noath.task.schema import TaskSchema
from noath.utils import login_required

blueprint = Blueprint('tasks', __name__, url_prefix='/tasks')

TASK_SCHEMA = TaskSchema()


@blueprint.route('', methods=['GET'], strict_slashes=False)
@login_required
def list_my_tasks():
    """List the tasks under the current user."""
    return jsonify(data=TASK_SCHEMA.dump(Task.query.filter(Task.user_id == g.current_user.id).all(), many=True)), 200


@blueprint.route('', methods=['POST'], strict_slashes=False)
@login_required
def create_task():
    task_data = TASK_SCHEMA.load(request.json)
    task = Task.create(user_id=g.current_user.id, **task_data)
    return jsonify(data=TASK_SCHEMA.dump(task)), 200
