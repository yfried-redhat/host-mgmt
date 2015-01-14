eventool
=========

Change to check


Installation guide:
* Install git:
  * yum install git
* Rally is required
  * Install rally: https://wiki.openstack.org/wiki/Rally/installation
* Clone eventool:
  * git clone https://github.com/yfried-redhat/eventool.git
  * cd eventool
  * git checkout stable
* Install eventool:
  * [sudo] python setup.py install [--record files.txt]
* Create your hosts_conf:
  * cp etc/host_conf.yaml.sample etc/host_conf.yaml
  * edit
* Remove eventool:
  * cat files.txt | sudo xargs rm -rf
