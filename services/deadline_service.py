from models.deadline_model import Deadline


def createDeadline(name, date):
    newDeadline = Deadline.create(
        name=name,
        date=date
    )
    newDeadline.save()
    return newDeadline


def getAllDeadline():
    return Deadline.select()


def getOneDeadline(id):
    return Deadline.get_by_id(id)


def updateDeadlineName(id, name):
    deadline = Deadline.get_by_id(id)
    deadline.name = name
    deadline.save()


def deleteAllDeadline():
    query = Deadline.delete()
    return query.execute()


def deleteOneDeadline(id):
    query = Deadline.delete().where(Deadline.id == id)
    return query.execute()
