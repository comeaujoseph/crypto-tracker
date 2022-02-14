venv:
	python3 -m venv env

requirements:
	env/bin/pip install -r requirements.txt

test:
	./env/bin/python manage.py test

server:
	./env/bin/python manage.py runserver 0.0.0.0:8000

scheduler:
	./env/bin/python manage.py scheduler

migrations:
	@./env/bin/python manage.py makemigrations
	@./env/bin/python manage.py migrate

fixtures:
	@./env/bin/python manage.py loaddata initial_metrics

purge:
	@rm -f db.sqlite3
	@(cd crypto_tracker; find . -path "*/migrations/*.py" -not -name "__init__.py" -delete)
	@(cd crypto_tracker; find . -path "*/migrations/*.pyc"  -delete)
