from netmiko import ConnectHandler

iosv_l2_r4 = {
    'device_type': 'cisco_ios',
    'ip': '100.100.100.200',
    'username': 'cisco',
    'password': 'cisco',
    'secret': 'cisco'
}

iosv_l2_r5 = {
    'device_type': 'cisco_ios',
    'ip': '100.100.100.201',
    'username': 'cisco',
    'password': 'cisco',
    'secret': 'cisco'
}

iosv_l2_r6 = {
    'device_type': 'cisco_ios',
    'ip': '100.100.100.202',
    'username': 'cisco',
    'password': 'cisco',
    'secret': 'cisco'
}

with open('iosv_l2_r4_cisco_design.txt') as f:
    lines = f.read().splitlines()
print (lines)
net_connect = ConnectHandler(**iosv_l2_r4)
output = net_connect.send_config_set(lines)
print (output)
with open('iosv_l2_r5_cisco_design.txt') as f:
     lines = f.read().splitlines()
print (lines)
net_connect = ConnectHandler(**iosv_l2_r5)
output = net_connect.send_config_set(lines)
print (output)
with open('iosv_l2_r6_cisco_design.txt') as f:
     lines = f.read().splitlines()
print (lines)
net_connect = ConnectHandler(**iosv_l2_r6)
output = net_connect.send_config_set(lines)
print (output)
############################
input()
############################
with open('iosv_l2_r4_cisco_design_del.txt') as f:
    lines = f.read().splitlines()
print (lines)
net_connect = ConnectHandler(**iosv_l2_r4)
output = net_connect.send_config_set(lines)
print (output)
with open('iosv_l2_r5_cisco_design_del.txt') as f:
     lines = f.read().splitlines()
print (lines)
net_connect = ConnectHandler(**iosv_l2_r5)
output = net_connect.send_config_set(lines)
print (output)
with open('iosv_l2_r6_cisco_design_del.txt') as f:
     lines = f.read().splitlines()
print (lines)
net_connect = ConnectHandler(**iosv_l2_r6)
output = net_connect.send_config_set(lines)
print (output)
