from models.deadline_model import Deadline, DeadlineStates
from models.task_deadline_model import TaskDeadline
from models.task_model import Status, Task


def createDeadline(name, date):
    newDeadline = Deadline.create(name=name, date=date)
    newDeadline.save()
    return newDeadline


def getAllDeadline():
    return Deadline.select().order_by(Deadline.date)


def getOneDeadline(id):
    try:
        return Deadline.get_by_id(id)
    except:
        return None


def findAllDeadlineState(state):
    return Deadline.select().where(Deadline.state == state).order_by(Deadline.date)


def updateDeadline(id, name=None, date=None):
    deadline = Deadline.get_by_id(id)

    if name:
        deadline.name = name
    if date:
        deadline.date = date

    deadline.save()

    return deadline


def updateState(id, state):
    deadline = Deadline.get_by_id(id)

    deadline.state = state

    deadline.save()

    return deadline


def deleteAllDeadline():
    query = Deadline.delete()
    return query.execute()


def deleteOneDeadline(id):
    query = Deadline.delete().where(Deadline.id == id)
    return query.execute()


def addTask(id, taskID):
    newTaskDeadline = TaskDeadline.create(task=taskID, deadline=id)
    newTaskDeadline.save()

    return newTaskDeadline


def getAllTaskDeadlines(id):
    return Task.select().join(TaskDeadline).where(TaskDeadline.deadline == id)


def getOneTaskDeadlines(id, taskID):
    return TaskDeadline.select().where(
        (TaskDeadline.deadline == id) & (TaskDeadline.task == taskID)
    )


def getCompletion(id):

    total_tasks = getAllTaskDeadlines(id).count()

    if total_tasks == 0:
        return 0.0

    complete_tasks = (
        TaskDeadline.select()
        .join(Task)
        .where((TaskDeadline.deadline == id) & ((Task.status == Status.DONE.value)))
        .count()
    )

    return complete_tasks / total_tasks
