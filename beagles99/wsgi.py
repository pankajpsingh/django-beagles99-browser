activate_this = 'C:/Users/Administrator/Envs/99beagles/Scripts/activate_this.py'
# execfile(activate_this, dict(__file__=activate_this))
exec(open(activate_this).read(),dict(__file__=activate_this))

import os, site, sys

# Add the site-packages of the chosen virtualenv to work with
site.addsitedir('C:/Users/Administrator/Envs/99beagles/Lib/site-packages')

# Add the app's directory to the PYTHONPATH
sys.path.append('C:/django/beagles99')
sys.path.append('C:/django/beagles99/beagles99')

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "beagles99.settings.dev")

application = get_wsgi_application()
