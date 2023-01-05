# This script will connect to a vCenter's REST API and power down all of the VMs except the vCenter.
# The script includes code to shut the vCenter down, but its commented out!
#
# Author: Daryl Allen

import requests
import time
import warnings
import urllib3


# Ignore the InsecureRequestWarning warning
warnings.filterwarnings("ignore", category=urllib3.exceptions.InsecureRequestWarning)

# username = input('Type your username: ')
# password = getpass.getpass("Type your password: ")
username = "administrator@vsphere.local"
password = "VMware1!"

# IMPORTANT - PLEASE NAME YOUR VCENTER SO SCRIPT CAN OMIT SHUTTING IT DOWN!
vcenter = "vcenter"

# Sometimes DNS does not provide consistent resolution. Sometimes its best to use ip address, or create a host file.
vcenter_url = 'https://172.17.0.100'

# API call to power down a VM: https://{api_host}/api/vcenter/vm/{vm}/guest/power?action=shutdown

# This script makes many API calls and we don't want to overwhelm the interface. Throttle API calls here:
API_call_interval = 1

# Authentication request
response = requests.post(f'{vcenter_url}/rest/com/vmware/cis/session', auth=(username, password), verify=False)
token = response.json()
cookie = response.cookies
time.sleep(API_call_interval)

# Define header for making API calls that will hold authentication data
headersAPI = {
    'Accept': 'application/json',
    'Authorization': 'Bearer ' + token['value'],
    'Cookie': 'vmware-api-session-id=' + cookie.values()[0]
}

# Request Datacenter info from vCenter
response = requests.get(f'{vcenter_url}/api/vcenter/vm',
                        headers=headersAPI,
                        verify=False)
datacenter_response = response.json()
time.sleep(API_call_interval)

# Print the information vCenter gave me
print(datacenter_response)

# Iterate through the list of VMs
for vm in datacenter_response:
    # Check the power state of the VM
    if vm["power_state"] == "POWERED_ON":
        # Print the name of the powered-on VM
        print(vm["name"])
        # Check if the VM is named "vcenter"
        if vm["name"] == vcenter:
            # Skip the VM if it is named "vcenter"
            continue
        # Get the ID of the VM
        vm_id = vm["vm"]

        # Make the POST request to power off the VM
        response = requests.post(f'{vcenter_url}/api/vcenter/vm/{vm_id}/guest/power',
                            headers=headersAPI,
                            params={"action": "shutdown"},
                            verify=False)
        time.sleep(API_call_interval)

        # Check the status code of the response
        if response.status_code == 200:
            print(f"Successfully powered off VM {vm['name']}")
        else:
            print(f"Failed to power off VM {vm['name']}")

# # Power off the VM named "vcenter"
# for vm in datacenter_response:
#     if vm["name"] == vcenter:
#         # Get the ID of the VM
#         vm_id = vm["vm"]
#
#         # Make the POST request to power off the VM
#         response = requests.post(f'{vcenter_url}/api/vcenter/vm/{vm_id}/guest/power',
#                             headers=headersAPI,
#                             params={"action": "shutdown"},
#                             verify=False)
#         time.sleep(API_call_interval)
#
#         # Check the status code of the response
#         if response.status_code == 200:
#             print(f"Successfully powered off VM {vm['name']}")
#         else:
#             print(f"Failed to power off VM {vm['name']}")
