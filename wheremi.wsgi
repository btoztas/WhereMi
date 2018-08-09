activate_this = '/home/administrator/projects/WhereMi/env/bin/activate_this.py'
execfile(activate_this, dict(__file__=activate_this))

from wheremi_app import app as application
