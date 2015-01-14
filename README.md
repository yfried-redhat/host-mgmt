eventool
=========

Temp version

Installation guide:
===================

* Install git:
  * yum install git
* Rally is required
  * Install rally: https://wiki.openstack.org/wiki/Rally/installation
* Clone eventool:
  * git clone https://github.com/yfried-redhat/eventool.git
  * cd eventool
  * git checkout stable_product
* Install eventool:
  * [sudo] python setup.py install [--record files.txt]
* Create your hosts_conf:
  * cp etc/host_conf.yaml.sample etc/host_conf.yaml
  * edit
* Remove eventool:
  * cat files.txt | sudo xargs rm -rf


Commands:
=========

    * service
        TARGET service OP SERVICE
        
        OPs:
        * status
        * stop
        * start
        * restart

    * raw
        TARGET raw COMMAND
        
    * script
        TARGET script INTERPRETER FILE
        
        INTERPRETER - program to execute script with (/bin/bash, /bin/python...)
        FILE - path to script
    
    * pcs
    * ha_manage
        TARGET ha_manage OP service
        
        TARGET - role of HA machines
        OPs:
        * find_service - finds the fixed ip of the HA node currently running the service
