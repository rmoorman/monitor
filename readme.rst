monitor
=======

|

installation
------------

* Do run this inside a virtualenv::

    virtualenv --no-site-packages /srv/monitor/venv

    . venv/bin/activate

    pip3 install -U -r requirements.txt

Run the ``_etc/mk_static.sh`` script to download, unzip (kube, flot, moment, jquery) and copy them together with the images into the static folder.
Make sure the ``unzip`` command is installed.

Create a subfolder called ``./data``, make sure your webserver user has write-access to it.
This is the only directory where stuff is written to.


configuration
-------------

Do not forget to set your api credentials in ``./data/auth.json`` (is generated on first run),
or launch with envvars: ``MONITORUSER=user MONITORPASS=pass ./run.py``



Don't set too low values on ``AUTOREF_MIN`` and ``AUTOREF_MAX``, or your server will burn.

Also avoid setting too high values for ``MAXKEEP`` (how long data will be stored) and ``MAXCONC`` (how old data may be to be taken for status calculation).


.. note::

    * `watcher <https://github.com/spookey/watcher>`_
    * `watcher_modules <https://github.com/spookey/watcher_modules>`_
