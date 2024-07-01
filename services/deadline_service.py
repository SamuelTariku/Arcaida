from models.deadline_model import Deadline, DeadlineStates
from models.task_deadline_model import TaskDeadline
from models.task_model import Status, Task
from utils.config import database


def checkFixedDeadline(id):
    return int(id) not in (1, 2, 3)


def createDeadline(name, date):
    newDeadline = Deadline.create(name=name, date=date)
    newDeadline.save()
    return newDeadline


def createFixedDeadline(id, name, date):
    newDeadline = Deadline.create(id=id, name=name, date=date)
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


def delayDeadline(id, timeDelta):
    deadline = Deadline.get_by_id(id)

    deadline.date += timeDelta

    deadline.save()

    return deadline


def updateState(id, state):
    deadline = Deadline.get_by_id(id)

    deadline.state = state

    deadline.save()

    return deadline


def moveDeadlineLast(id):
    database.execute_sql(
        """
        update deadline set id = (select max(id) from deadline) + 1 where id = {}
        """.format(
            id
        )
    )


def deleteAllDeadline():
    query = Deadline.delete().where(Deadline.id not in (1, 2, 3))
    return query.execute()


def deleteOneDeadline(id):
    query = Deadline.delete().where(Deadline.id == id)
    return query.execute()


def addTask(id, taskID):
    newTaskDeadline = TaskDeadline.create(task=taskID, deadline=id)
    newTaskDeadline.save()

    return newTaskDeadline


def getAllTasksForDeadline(id):
    return (
        Task.select()
        .join(TaskDeadline)
        .where(TaskDeadline.deadline == id)
        .order_by(TaskDeadline.task)
    )


def getTasksForDeadlineByStatus(id, status):
    return (
        Task.select()
        .join(TaskDeadline)
        .where((TaskDeadline.deadline == id) & (Task.status == status))
        .order_by(TaskDeadline.task)
    )


def getAllDeadlinesForTask(id):
    return Deadline.select().join(TaskDeadline).where(TaskDeadline.task == id)


def getOneTaskDeadline(deadlineID, taskID):
    return TaskDeadline.select().where(
        (TaskDeadline.deadline == deadlineID) & (TaskDeadline.task == taskID)
    )


def getCompletion(id):

    total_tasks = getAllTasksForDeadline(id).count()

    if total_tasks == 0:
        return 0.0

    complete_tasks = (
        TaskDeadline.select()
        .join(Task)
        .where((TaskDeadline.deadline == id) & ((Task.status == Status.DONE.value)))
        .count()
    )

    return complete_tasks / total_tasks


def deleteAllTaskDeadlines():
    query = TaskDeadline.delete()
    return query.execute()


def deleteOneTaskDeadlineById(id):
    query = TaskDeadline.delete().where((TaskDeadline.id == id))
    return query.execute()


def deleteOneTaskDeadline(deadlineID, taskID):
    query = TaskDeadline.delete().where(
        (TaskDeadline.deadline == deadlineID) & (TaskDeadline.task == taskID)
    )
    return query.execute()


def deleteAllTasksForDeadline(id):
    query = TaskDeadline.delete().where((TaskDeadline.deadline == id))
    return query.execute()


def deleteAllDeadlinesForTask(id):
    query = TaskDeadline.delete().where((TaskDeadline.task == id))
    return query.execute()
