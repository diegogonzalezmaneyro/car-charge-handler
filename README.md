# car-charge-handler
some code that handle RPi with: openEVSE, OCPP and Blockchain
(Testing over a pc, not tested in RPi yet)

Create an environment with python >= 3.6.1 and install requirements.txt.
This tutorial may help: https://community.home-assistant.io/t/upgrading-python-in-a-virtualenv/29137/3
Or this one: https://liudr.wordpress.com/2016/02/04/install-python-on-raspberry-pi-or-debian/

if using python <= 3.7 need to change asyncio lines in __main__
This stackoverflow may help: https://stackoverflow.com/questions/52796630/python3-6-attributeerror-module-asyncio-has-no-attribute-run

to know more about how asyncio works go to this link: https://realpython.com/async-io-python/