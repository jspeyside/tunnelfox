=========
TunnelFox
=========
.. image:: https://travis-ci.org/jspeyside/tunnelfox.svg?branch=master
    :target: https://travis-ci.org/jspeyside/tunnelfox

.. image:: https://codecov.io/gh/jspeyside/tunnelfox/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/jspeyside/tunnelfox

.. contents::


Overview
========

TunnelFox is a python command line tool for port-Forwarding via SSH. Have you ever needed to access a port on a remote server, but the port is not accessible. If you have SSH access you can forward the port via ssh so that it is accessible locally.

For example, if I want to access port `8080` on a remove server `foo.com`, I can use TunnelFox to access that port locally. By running: `tunnelfox new -s foo.com -p 8080`. I can locally access hat is running on foo.com by running `curl http://localhost:8080`.


Usage
=====

TunnelFox can be used to start, stop and manage existing tunnels.

List
----

To list existing tunnels run:
.. code-block:: bash
  $ tunnelfox ls

  1: foo.com 5050:5050
  2: bar.com 8000:8000
  3: foobar.com 9000:9000

The format for the output is:
.. code-block:: bash
  <remote_host> <locally_accessible_port>:<remote_port>


If a connection died (i.e. the connection was interrupted) it will be displayed in the output:

.. code-block:: bash
  $ tunnelfox ls

  1: foo.com 5050:5050
  2: bar.com 8000:8000 (dead)
  3: foobar.com 9000:9000


New
---

To establish new tunnels use the `new` command.

Establish a new tunnel to `foo.com` forwarding remote port `8080` to local port `8080`:
.. code-block:: bash
  tunnelfox new -s foo.com -p 8080 -l 8080

A shorter version of forwarding remote port `8080` to local port `8080`:
.. code-block:: bash
  tunnelfox new -s foo.com -p 8080

Establish a new tunnel to `bar.com` forwarding remote port `443` to local port `8443`:
.. code-block:: bash
  tunnelfox new -s foo.com -p 443 -l 8443

Stop
----

To stop existing tunnels use the `ls` command to find their numbers then use the `stop` command:
.. code-block:: bash
  tunnelfox stop 2


Install
=======
With `pip` installed, run
.. code-block:: bash
  pip install tunnelfox

You can now run `tunnelfox` from the command line.

## License
MIT License
