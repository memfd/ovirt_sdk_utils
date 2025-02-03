 The script "info_vlan_for_vm.py" allows you to get data on the quantitative distribution of virtual machines via networks (VLAN) in oVirt. The result of the work is a table in the CSV format, which contains the names of the networks (VLAN) by vertical and the names of the VM that belong to each network - horizontally, a column diagram is used as visualization of data, which allows you to clearly assess the quantitative distribution of virtual machines between the networks. By default, the process of work is accompanied by logging in DEBUG mode to the "ovirt_script.log" file.

"info_vlan_for_vm.py" - supports 2 modes of operation:
1. The case when the names of the networks are specified in the "vlan_list.txt" file, this is the launch of the utility without specifying flags, in the same directory with this file.
2. The case when you need to get data on all existing networks (VLAN) in oVirt. In this case, you need to specify an additional flag when starting, for example:

info_vlan_for_vm.py --all-networks

For launch, I recommend using a virtual environment for Python, this way: