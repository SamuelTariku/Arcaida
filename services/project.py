from models.project import Project


def createProject(name, started=False):
    newProject = Project.create(
        name=name,
        started=started
    )
    newProject.save()
    return newProject


def getAllProject():
    return Project.select()


def getOneProject(id):
    return Project.get_by_id(id)


def updateProjectName(id, name):
    query = Project.update(
        name=name,
    ).where(
        Project.id == id
    )
    query.execute()
    return True


def deleteAllProject():
    query = Project.delete()

    return query.execute()


def deleteOneProject(id):
    query = Project.delete().where(Project.id == id)
    return query.execute()
