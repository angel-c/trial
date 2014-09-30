#!/usr/bin/env python

import SoftLayer
import time
import optparse
 
def main():
    # Describe a parser for command-line options
    parser = optparse.OptionParser()
    parser.add_option('-u', '--username', help='Username of the SoftLayer account (required)')
    parser.add_option('-k', '--api_key', help='API key of the SoftLayer account (required)')
    parser.add_option('-n', '--hostname', help='Hostname to be provided to the new instance (required)')
    parser.add_option('-d', '--domainname', help='Domain name to be provided to the new instance (required)')
    parser.add_option('-c', '--cpus', help='Number of CPUs requested for the new instance, default=1 (optional)', default=1)
    parser.add_option('-m', '--memory', help='Memory requested for the new instance (in KB), default=1024 (optional)', default=1024)
    parser.add_option('-b', '--billing', help='Indicate if we need hourly billing (true, false), default=true (optional)', default='true')
    parser.add_option('-o', '--os_code', help='Operating System code of the instance (REDHAT, UBUNTU, CENTOS), default=CENTOS (optional)', default='CENTOS')
 
    # Parse all the command-line options
    (opts, args) = parser.parse_args()
 
    # Check for required options
    if not opts.username:
        print('ERROR: Username is required')
        parser.print_help()
        exit(-1)
 
    if not opts.api_key:
        print('ERROR: API key is required')
        parser.print_help()
        exit(-1)
 
    if not opts.hostname:
        print('ERROR: Hostname is required')
        parser.print_help()
        exit(-1)
 
    if not opts.domainname:
        print('ERROR: Domain name is required')
        parser.print_help()
        exit(-1)
 
    try:
        # Create a SoftLayer client
        print('Connecting to SoftLayer as %s' % (opts.username))
        client = SoftLayer.Client(username=opts.username, api_key=opts.api_key)
 
        # Request a VM
        print('Requesting %s_LATEST VM, FQDN:%s.%s, CPU:%d, Memory:%d, Hourly Billing:%s' % (opts.os_code, opts.hostname, opts.domainname, opts.cpus, opts.memory, opts.billing))
        request = client['Virtual_Guest'].createObject({
                                                    'hostname': opts.hostname,
                                                    'domain': opts.domainname,
                                                    'startCpus': opts.cpus,
                                                    'maxMemory': opts.memory,
                                                    'hourlyBillingFlag': opts.billing,
                                                    'operatingSystemReferenceCode': opts.os_code + '_LATEST',
                                                    'localDiskFlag': 'false'
        })
        vg_id = request['id']
        print('VM requested with ID: %d' % (vg_id))
 
        # Wait for VM to be provisioned
        sleep_time = 30
        status = 'PENDING'
        while  status != 'COMPLETE':
            print('Pausing execution for %d seconds...' % (sleep_time))
            time.sleep(sleep_time)
            print('Checking status of the requested VM')
            virtual_guest = client['Virtual_Guest'].getObject(id=vg_id, mask='id, lastTransaction')
            if 'lastTransaction' in virtual_guest:
                status = virtual_guest['lastTransaction']['transactionStatus']['name']
                print('Recent transaction status: %s' % (status))
            else:
                print("WARNING: No transaction information provided by SoftLayer")
 
        # Fetch relevant information (such as its IP address, login-username, login-password) about the VM
        virtual_guest = client['Virtual_Guest'].getObject(id=vg_id, mask='id, primaryIpAddress, operatingSystem[passwords]')
 
        vg_ipAddress = ''
        if 'primaryIpAddress' in virtual_guest:
            # Grab the IP Address
            vg_ipAddress = virtual_guest['primaryIpAddress']
        else:
            print("WARNING: No primay IP address returned by SoftLayer")
 
        vg_username = ''
        vg_password = ''
        if 'operatingSystem' in virtual_guest:
            if 'passwords' in virtual_guest['operatingSystem']:
                if len(virtual_guest['operatingSystem']['passwords']) > 0:
                    # Grab the username
                    if 'username' in virtual_guest['operatingSystem']['passwords'][0]:
                        vg_username = virtual_guest['operatingSystem']['passwords'][0]['username']
                    else:
                        print("WARNING: No username provided by SoftLayer")
 
                    # Grab the password associated with the user
                    if 'password' in virtual_guest['operatingSystem']['passwords'][0]:
                        vg_password = virtual_guest['operatingSystem']['passwords'][0]['password']
                    else:
                        print("WARNING: No password provided by SoftLayer")
 
        # The following are parsed by UrbanCode Deploy to process as property values
        print('ID=' +  str(vg_id))
        print('USERNAME=' + vg_username)
        print('PASSWORD=' + vg_password)
        print('IPADDRESS=' + vg_ipAddress)
 
    except Exception as e:
        print('Received exception: %s' % (e.faultCode))
        print('Exception details: %s' % (e.faultString))
 
if __name__ == '__main__':
    main()
