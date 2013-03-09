# flask-ndb-api

boilderplate / skeleton for creating an api on appengine with flask and ndb.

i've compiled this from a few projects i've worked on using google's appengine.



## some recommended shit to setup

#### install pip, virtualenv & virtualenvwrapper
use pip (`http://pip-installer.org`) to manage python 3rd party dependencies.
virtualenv (`http://virtualenv.org`) creates isolated python environments so you can
work on more than one python project without pip installed library packages
overlapping and conflicting.
virtualenvwrapper (`http://virtualenvwrapper.readthedocs.org`) is a layer that sits
on top of virtualenv to provide some command line sugar, and ease of virtualenv
management.

install pip

    sudo easy_install pip

install virtualenv

    sudo pip install virtualenv virtualenvwrapper

install google appengine sdk (DON'T FUCKING USE THE INSTALLER)

    curl -O http://googleappengine.googlecode.com/files/google_appengine_1.7.4.zip
    unzip -d ~/ -oq google_appengine_1.7.4.zip


#### install virtualenv into shell

update ~/.bash_profile

    # path setup
    export PATH="~/google_appengine:/Library/Frameworks/Python.framework/Versions/2.7/bin:${PATH}"

    # virtualenvwrapper for python
    export WORKON_HOME=~/.virtualenvs
    . /usr/local/bin/virtualenvwrapper.sh


setup virtualenvwrapper so virtual environments can be found in the home
directory in the folder `.virtualenvs`. this, i've discovered, has turned out
to be a solid pattern to use to organize multiple python projects per machine.


#### project specific environments

use virtualenvwrapper to create a new virtualenv environment `flask-ndb-api`.

    mkvirtualenv --no-site-packages flask-ndb-api

now, to activate the specific python environment, run the command:

    workon flask-ndb-api


#### enable the appengine sdk in virtualenv

    cd  ~/.virtualenvs/flask-ndb-api
    echo "~/google_appengine" >> lib/python2.7/site-packages/gae.pth
    echo "import dev_appserver; dev_appserver.fix_sys_path()" >> lib/python2.7/site-packages/gae.pth


this adds google appengine sdk's scripts to shell's executable path, so we can
invoke it's commands.
