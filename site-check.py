"""
site-check.py
Automation script to connect to Arista devices and record state to a txt file.
To be run Pre and Post maintenance event to check for state differences.
https://github.com/brentnowak/arista-tools
"""

import json
import pyeapi
import datetime
from collections import OrderedDict

switches = ['switch-name']
pyeapi.load_config('nodes.conf')


def sorted_dict(d):
    """
    :param dict: unsorted dictionary
    :return: JSON formatted ordered dictionary by key
    """
    return json.dumps(OrderedDict(sorted(dict_remove_keys(d).items())))

def dict_remove_keys(d):
    """
    Remove dictionary keys that clutter report
    """
    filter = ("lastMove", "sflow", "flowcontrol_send",
              "flowcontrol_receive", "routeAction", "hardwareProgrammed",
              "kernelProgrammed", "directlyConnected", "ttl",
              "type", "entryType", "moves",
              "upDownTime", "msgSent", "inMsgQueue",
              "underMaintenance", "msgReceived", "outMsgQueue",
              "stateTime")
    filter_match = set(filter).intersection(set(d.keys()))
    for key in filter_match:
        del d[key]
    return d

def format_filename(switch):
    """
    Format file name to be easily sortable for diff
    YYYY-MM-DD_NAME_HH_MM.txt
    """
    now = datetime.datetime.now()
    return str(now.strftime("%Y-%m-%d")) + "_" + str(switch) + "_" + str(now.strftime("%H_%M")) + ".txt"

def print_line(f):
    f.write("--------------------------------------" + '\n')
    return

def print_datetime(f):
    print_line(f)
    f.write(str(datetime.datetime.now()) + '\n')
    return

def print_header(f, switch, command):
    print_line(f)
    f.write(switch + '\n')
    f.write(command + '\n')
    print_line(f)
    return

def print_list_to_file(f, list):
    for row in list:
        f.write(str(sorted_dict(row)) + '\n')
    f.write('\n')
    return

def print_dict_to_file(f, dict):
    for k,v in sorted(dict.items()):
        f.write(str(k) + " : " + str(sorted_dict(v)) + '\n')
    return

def get_routemaps(node):
    return node.api('routemaps').getall()

def show_mac_addresstable(node):
    return node.enable('show mac address-table')[0]['result']['unicastTable']['tableEntries']

def show_interfaces_status(node):
    return node.api('interfaces').getall()

def show_lldp_neighbors(node):
    return node.enable('show lldp neighbors')[0]['result']['lldpNeighbors']

def show_ip_arp(node):
    return node.enable('show ip arp')[0]['result']['ipV4Neighbors']

def show_ip_bgp_summary(node):
    # TODO Enhance output to account for multiple vrf and ospf instances
    return node.enable('show ip bgp summary')[0]['result']['vrfs']['default']['peers']

def show_ip_ospf_neighbor(node):
    # TODO Enhance output to account for multiple vrf and ospf instances
    # TODO Cleanup 'details' dictionary to remove unnessary items like 'stateTime', 'inactivity'
    return node.enable('show ip ospf neighbor')[0]['result']['vrfs']['default']['instList']['1']['ospfNeighborEntries']

def show_ip_route(node):
    return node.enable('show ip route')[0]['result']['vrfs']['default']['routes']

def show_inventory(node):
    return node.enable('show inventory')[0]['result']['xcvrSlots']

def show_vlan(node):
    return node.api('vlans').getall()



def main():
    for switch in switches:
        f = open(format_filename(switch), "a")

        try:
            node = pyeapi.connect_to(switch)

            print_datetime(f)

            print_header(f, switch, "show inventory")
            print_dict_to_file(f, show_inventory(node))

            print_header(f, switch, "show vlan")
            print_dict_to_file(f, show_vlan(node))

            print_header(f, switch, "show mac address-table")
            print_list_to_file(f, show_mac_addresstable(node))

            print_header(f, switch, "show interfaces status")
            print_dict_to_file(f, show_interfaces_status(node))

            print_header(f, switch, "show lldp neighbors")
            print_list_to_file(f, show_lldp_neighbors(node))

            print_header(f, switch, "show ip arp")
            print_list_to_file(f, show_ip_arp(node))

            print_header(f, switch, "show ip bgp summary")
            print_dict_to_file(f, show_ip_bgp_summary(node))

            print_header(f, switch, "show ip ospf neighbor")
            print_list_to_file(f, show_ip_ospf_neighbor(node))

            print_header(f, switch, "show ip route")
            print_dict_to_file(f, show_ip_route(node))

        except Exception as e:
            print(e)
            f.write(str(e) + '\n')
        f.close()

if __name__ == '__main__':
    main()
