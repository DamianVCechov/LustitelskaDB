This file is for you to describe the LustitelskaDB application. Typically
you would include information such as the information below:

Installation and Setup
======================

Create configuration::

	$ cp development.ini.template development.ini

Edit configuration file for you DB etc. (optional), i.e.::

	$ editor development.ini

Install ``LustitelskaDB`` using the setup.py script (optional)::

    $ cd LustitelskaDB
    $ python setup.py develop

Create the project database for any model classes defined::

    $ gearbox setup-app

Start the paste http server::

    $ gearbox serve

While developing you may want the server to reload after changes in package files (or its dependencies) are saved. This can be achieved easily by adding the --reload option::

    $ gearbox serve --reload --debug

    or optionally (if you don't used setup.py script for install)::

    $ gearbox serve --relative --reload --debug

Then you are ready to go.
