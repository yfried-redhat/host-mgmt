eventool
=========

Installation guide:
----------------------
* Install git  
  `yum install git gcc python-devel`
* Rally is required  
  [Install rally](https://wiki.openstack.org/wiki/Rally/installation)
* Clone eventool  
    `git clone https://github.com/yfried-redhat/eventool.git`  
    `cd eventool`  
    `git checkout stable-product`
* Install eventool  
    `[sudo] python setup.py install [--record files.txt]`
* Create your hosts\_conf  
    `cp etc/hosts_conf.yaml.sample /etc/eventool/hosts_conf.yaml`  
edit `etc/host_conf.yaml`
* Remove eventool  
    `cat files.txt | sudo xargs rm -rf`

***

Configuration file:
---------------------
By default, configuration file is in `eventool/etc/hosts_conf.yaml`. To change that, set environment variable `export HOSTS_CONF=</path/to/file.suffix>`

* Default values for all servers. Each value can be overridden for specific node  
  * password  
  * user
  * private_key (path)
* hosts:  
Each host is defined by addresses (ip/fqdn) and attributes:  
  * alias: a list of aliases for the machine
  * override default values (password, user, etc...)
  * roles: a list of roles associated with the host  
* roles:  
Each role can contain a list of aliases/addresses that will associate this role with the matching host  
* fully_active_services:  
List of services that are Active/Active but don't use VIP. Unable to locate them since they are active on all HA nodes.



***  

Commands:
--------------

* `service`  
    `TARGET service OP SERVICE`  
  OP:  
    * `status`
    * `stop`
    * `start`
    * `restart`

* `raw`  
    `TARGET raw COMMAND`
    
* `script`  
`    TARGET script INTERPRETER FILE`
    
    INTERPRETER - program to execute script with (`/bin/bash`, `/bin/python`...)  
    FILE - path to script

* `pcs` - TBD
* `ha_manage`  
    `TARGET ha_manage OP service`
    
  HA-ROLE - role of HA machines    
  OP:  
    * `find_service` - finds the fixed ip of the HA node currently running the service  
  
