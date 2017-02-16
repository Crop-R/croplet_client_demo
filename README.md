cropr_demo
==========

Crop-R Demo Application for using the Crop-R API v3

==========
Installation
==========

1. set up virtual env
2. install requirements:
  `pip install -r requirements.txt`
3. rename local_settings_example.py to local_settings.py
4. follow <a href="https://www.crop-r.com/apps/cropletdeveloper/tutorial/">the tutorial</a>
5. copy `client_id` and `client_secret` to settings.py
7. run ./manage.py migrate
8. run ./manage.py createsuperuser
9. run ./manage.py runserver
