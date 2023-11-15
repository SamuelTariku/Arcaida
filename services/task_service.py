from models.task_model import Task, Status
from utils.config import database
import datetime

from peewee import fn

def createTask(name, project):
    taskOrder = getTasksByProject(project.id).count() + 1

    newTask = Task.create(
        name=name,
        project=project,
        order=taskOrder
    )
    newTask.save()
    return newTask


def getAllTasks():
    return Task.select()


def countProjectTasks(project):
    tasks = Task.select().where(
        Task.project == project.id
    ).count()

    return tasks


def getOneTask(id):
    return Task.get_by_id(id)

def getManyTask(projectID, idList):
    tasks = Task.select().where(
        Task.project == projectID,
        Task.order << idList
    )

    return tasks

def getTaskByOrder(projectID, order):
    tasks = Task.select().where(
        Task.project == projectID,
        Task.order == order
    )

    if (len(tasks) == 0):
        return None

    return tasks[0]


def getTasksByProject(id):
    return Task.select().where(
        Task.project == id
    ).order_by(Task.order)

def getCompletionForProject(projectID):
    total_tasks = Task.select().where(
        Task.project == projectID
    ).count()
    
    if(total_tasks == 0):
        return 1.0
    
    complete_tasks = Task.select().where(
        (Task.status == Status.DONE.value) &
        (Task.project == projectID)
    ).count()
    
    return complete_tasks / total_tasks

def findAllTaskStatus(status, order="default"):
    
    if(order=="default"):
        orderBy = Task.order
    elif(order == "random"):
        orderBy = fn.Random()
    elif(order == "endDate"):
        orderBy = Task.endDate
    else:
        raise Exception("Unknown Order Type")
    
    return Task.select().where(
        Task.status == status
    ).order_by(orderBy)


def findAllTaskStatusForProject(status, projectID, order="default"):
    
    if(order=="default"):
        orderBy = Task.order
    elif(order == "random"):
        orderBy = fn.Random()
    elif(order == "endDate"):
        orderBy = Task.endDate
    else:
        raise Exception("Unknown Order Type")
    return Task.select().where(
        (Task.status == status) &
        (Task.project == projectID)
    ).order_by(orderBy)

def findActiveTaskForProject(projectID):
    return Task.select().where(
        (Task.status == Status.IN_PROGRESS) &
        (Task.project == projectID)
    )


def updateStatus(task, status):
    
    # Task is given a start date when its set to IN-PROGRESS
    # end date is assigned when its set to DONE
    if(status == Status.IN_PROGRESS.value):
        task.startDate = datetime.datetime.utcnow()
    elif(status == Status.BACKLOG.value):
        task.startDate = None
        task.endDate = None
    elif(status == Status.DONE.value):
        if(not task.startDate):
            task.startDate = datetime.datetime.utcnow()
        task.endDate = datetime.datetime.utcnow()
    
    # TODO: Add validation to restrict only one IN-PROGRESS TASK
    task.status = status
    
    task.save()
    
    reassignOrder(task.project.id)

    return task


def deleteTask(task):

    projectID = task.project
    deleted = task.delete_instance()
    reassignOrder(projectID)

    return deleted


def deleteTasksForProject(id):
    query = Task.delete().where(Task.project == id)
    return query.execute()


def reassignOrder(projectID):
    
    # Reorders the tasks based on the status given
    # Todo's are last 
    database.execute_sql(
        """
        update task
        set "order" = (
	        select (
		       	select count(*)
				from task b
				where project_id=={projectID} and ((a.status == b.status and a.id >= b.id) or (a.status > b.status)) 
	        ) as num 
	        from task a 
	        where project_id == {projectID} and task.id == a.id
        )
        where project_id == {projectID}
    """.format(projectID=projectID)
    )


def updateOrder(projectID, current, destination):

    initial = int(current)
    final = int(destination)

    tasks = getTasksByProject(projectID)

    movedTask = tasks[initial-1]

    # Set the initial order position to null
    movedTask.order = None
    movedTask.save()

    # Update all the records that are between the values
    if (initial < final):
        query = Task.update(order=Task.order - 1).where(
            (Task.project == projectID) &
            (Task.order > initial) & (Task.order <= final)
        )
        query.execute()
    elif (initial > final):
        query = Task.update(order=Task.order + 1).where(
            (Task.order < initial) & (Task.order >= final)
        )
        query.execute()

    # Now that destination is moved
    movedTask.order = final
    movedTask.save()

    # return movedTask
    return movedTask
