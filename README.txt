To create user and database run the next commands (in the psql):

CREATE DATABASE task_manager;
CREATE USER test_user WITH PASSWORD 'manager123';
GRANT ALL PRIVILEGES ON DATABASE task_manager to test_user;

-----------------------------------

Run celery worker (from virtualenv):

celery worker --loglevel=info -A simple_task_manager --beat