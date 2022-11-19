cd A_2
gunicorn --bind 0.0.0.0:5000 wsgi_frontend:webapp &
gunicorn --bind 0.0.0.0:5001 wsgi_managerapp:webapp &
gunicorn --bind 0.0.0.0:5002 wsgi_backend:webapp &
python3 A_2/autoscaler.py

echo "Web Application Started"