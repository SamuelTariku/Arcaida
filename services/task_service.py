from models.task_model import Task
from utils.config import database


def reassignOrder(projectID):
    database.execute_sql(
        """
        update task
        set "order" = (
	        select (
		        select count(*) 
		        from task b 
		        where a.id >= b.id and project_id == {projectID}
	        ) as num 
	        from task a 
	        where project_id == {projectID} and task.id == a.id
        )
    """.format(projectID=projectID)
    )


def updateOrder(projectID, current, destination):

    initial = int(current)
    final = int(destination)

    tasks = getTasksByProject(projectID)

    movedTask = tasks[initial-1]

    # Avoiding unique constraint
    movedTask.order = None
    movedTask.save()

    # Update all the records that are between the values
    if(initial < final):
        query = Task.update(order=Task.order - 1).where(
            (Task.project == projectID) &
            (Task.order > initial) & (Task.order <= final)
        )
        query.execute()
    elif(initial > final):
        query = Task.update(order=Task.order + 1).where(
            (Task.order < initial) & (Task.order >= final)
        )
        query.execute()

        # database.execute_sql("""
        # UPDATE "task"
        # SET "order" = ("task"."order" + 1)
        # FROM (
        #     SELECT "order"
        #     FROM "task"
        #     ORDER BY "order" DESC
        # ) as ts
        # WHERE (("ts"."order" < {final}) AND ("ts"."order" >= {initial}))
        # """.format(initial=initial, final=final))

    # Now that destination is moved
    movedTask.order = final
    movedTask.save()

    # return movedTask


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


def getOneTask(id):
    return Task.get_by_id(id)


def getTaskByOrder(projectID, order):
    return Task.select().where(
        Task.project == projectID,
        Task.order == order
    )[0]


def getTasksByProject(id):
    return Task.select().where(
        Task.project == id
    ).order_by(Task.order)


def countProjectTasks(project):
    tasks = Task.select().where(
        Task.project == project.id
    ).count()

    return tasks


def updateTask(task, name=None, status=None):

    if(name):
        task.name = name
    if(status):
        task.status = status

    task.save()

    return task


def deleteTask(task):

    projectID = task.project
    deleted = task.delete_instance()
    reassignOrder(projectID)

    return deleted


def deleteTasksForProject(id):
    query = Task.delete().where(Task.project == id)
    return query.execute()
