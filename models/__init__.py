from models import project_model, task_model, deadline_model, task_deadline_model



def create_tables():
    project_model.Project.create_table(True)
    task_model.Task.create_table(True)
    deadline_model.Deadline.create_table(True)
    task_deadline_model.TaskDeadline.create_table(True)
