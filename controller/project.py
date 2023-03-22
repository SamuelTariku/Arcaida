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
