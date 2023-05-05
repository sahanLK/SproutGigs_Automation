from database import get_session, Job


session = get_session()

# session.add_all([
#     Job(job_id="15fsdfsdf", title="Title"),
#     Job(job_id="15fsdfrerf", title="Title 2"),
# ])
# session.commit()

for i in session.query(Job).all():
    session.delete(i)
    session.commit()
