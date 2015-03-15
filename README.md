eventool
=========

Installation guide:
----------------------
* Install system requirements  
      yum install git gcc python-devel
* Clone eventool  
      git clone https://github.com/yfried-redhat/eventool.git
      cd eventool  
      git checkout stable-product
* Install eventool  
      [sudo] python setup.py install [--record files.txt]
    use `--record` if you wish to be able to uninstall Eventool later
* Create your conf file from sample file (See: "Configuration File").  
      cp etc/hosts_conf.yaml.sample /etc/eventool/hosts_conf.yaml  
edit `etc/host_conf.yaml`
* Remove/Uninstall eventool (only if `--record` flag was used in setup)  
      cat files.txt | [sudo] xargs rm -rf

***

Configuration File:
---------------------
By default, Eventool looks for configuration file in `eventool/etc/hosts_conf.yaml`. To change that, set environment variable `export HOSTS_CONF=</path/to/file.suffix>`

* Default values for all servers. Each value can be overridden for specific node  
  * `password`  
  * `user`
  * `private_key` (path)
* `hosts:`  
Each host is defined by addresses (ip/fqdn) and attributes:  
  * `alias`: a list of aliases for the machine
  * override default values (`password`, `user`, etc...)
* `roles:`  
Each role can contain a list of aliases/addresses that will associate this role with the matching host  
* `fully_active_services:`  
List of services that are Active/Active but don't use VIP. Unable to locate them since they are active on all HA nodes.

***  

Commands:
--------------

* `system`  
      TARGET system OP SERVICE  
  OP:  
    * `status`
    * `stop`
    * `start`

* `raw`  
    `TARGET raw OP`  
  OP:  
    * `script` - Execute script via SSH  
          TARGET script INTERPRETER FILE
        INTERPRETER - program to execute script with (`/bin/bash`, `/bin/python`...)  
        FILE - path to script  
    * `command` - Execute command via SSH  
          TARGET command [command [arg1 [arg2[...]]]]
    
* `hosts`  
        TARGET hosts OP
  OP:  
    * `alias` display list of aliases for host based on conf file.  

* `pcs status` - return output of `pcs status` command from host. (for debug only)  
* `ha_manage`  
      HA-ROLE ha_manage OP SERVICE
    
  HA-ROLE - role of HA machines    
  OP:  
    * `find_service` - finds the fixed ip of the HA node currently running the service  
  
