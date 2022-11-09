cd A_1
gunicorn --bind 0.0.0.0:5002 wsgi_memcache:webapp &
gunicorn --bind 0.0.0.0:5001 wsgi_managerapp:webapp &
gunicorn --bind 0.0.0.0:5000 wsgi_frontend:webapp &

echo "Frontend & Memcache Started"