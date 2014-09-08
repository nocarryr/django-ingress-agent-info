import os.path

SECRET_KEY = None
SECRET_KEY_FILE = 'secret_key.conf'

def create_secret_key():
    from django.utils.crypto import get_random_string
    chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
    secret_key = get_random_string(50, chars)
    with open(SECRET_KEY_FILE, 'w') as f:
        f.write(secret_key)
    return secret_key
    
def get_secret_key():
    if not os.path.exists(SECRET_KEY_FILE):
        secret_key = create_secret_key()
    else:
        with open(SECRET_KEY_FILE, 'r') as f:
            secret_key = f.read()
    return secret_key
    
if SECRET_KEY is None:
    SECRET_KEY = get_secret_key()

ALLOWED_HOSTS = []
DATABASES = {
#    'default': {
#        'ENGINE':'django.db.backends.mysql', 
#        'NAME':'ingress_agent_info', 
#        'USER':'ingress_agent', 
#        'PASSWORD':'ingress', 
#        'HOST':'192.168.1.50', 
#        'PORT':'3306', 
#    }, 
}

DEBUG = True
TEMPLATE_DEBUG = True
