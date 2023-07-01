from models.deadline_model import Deadline


def createDeadline(name, date):
    newDeadline = Deadline.create(
        name=name,
        date=date
    )
    newDeadline.save()
    return newDeadline


def getAllDeadline():
    return Deadline.select().order_by(Deadline.date)


def getOneDeadline(id):
    try:
        return Deadline.get_by_id(id)
    except:
        return None


def updateDeadline(id, name=None, date=None):
    deadline = Deadline.get_by_id(id)

    if (name):
        deadline.name = name
    if (date):
        deadline.date = date

    deadline.save()

    return deadline


def deleteAllDeadline():
    query = Deadline.delete()
    return query.execute()


def deleteOneDeadline(id):
    query = Deadline.delete().where(Deadline.id == id)
    return query.execute()
