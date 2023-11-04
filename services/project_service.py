from models.project_model import Project

def createProject(name):
    newProject = Project.create(
        name=name,
        active=False
    )
    newProject.save()
    return newProject


def getAllProject():
    return Project.select()


def getOneProject(id):
    return Project.get_by_id(id)

def getActiveProjects():
    return Project.select().where(
        Project.active == True
    )
    
# def updateProjectName(id, name):
#     query = Project.update(
#         name=name,
#     ).where(
#         Project.id == id
#     )
#     query.execute()
#     return True

def updateProjectName(id, name):
    project = Project.get_by_id(id)
    project.name = name
    project.save()
    return project
    
def updateProjectStatus(id, active):
    project = Project.get_by_id(id)
    project.active = active
    project.save()
    return project

def deleteAllProject():
    query = Project.delete()

    return query.execute()


def deleteOneProject(id):
    query = Project.delete().where(Project.id == id)
    return query.execute()
