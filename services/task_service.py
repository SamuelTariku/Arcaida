from models.task_model import Task


def createTask(name, project):

    newTask = Task.create(
        name=name,
        project=project
    )

    newTask.save()
    return newTask


def getAllTasks():
    return Task.select()


def getOneTask(id):
    return Task.get_by_id(id)


def getTasksByProject(id):
    return Task.select().where(
        Task.project == id
    )


def countProjectTasks(project):
    tasks = Task.select().where(
        Task.project == project.id
    ).count()

    return tasks


def updateTask(id, name=None, status=None):
    task = Task.get_by_id(id)
    if(name):
        task.name = name
    if(status):
        task.status = status

    Task.save()


def deleteTask(id):
    query = Task.delete().where(Task.id == id)
    return query.execute()


def deleteTasksForProject(id):
    query = Task.delete().where(Task.project == id)
    return query.execute()
