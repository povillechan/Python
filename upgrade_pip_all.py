from pip._internal.utils import misc
from subprocess import call

for dist in misc.get_installed_distributions():
    call("pip install --upgrade " + dist.project_name, shell=True)