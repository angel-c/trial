#!/usr/bin/env python
import SoftLayer
import optparse
 
def main():
 
    # Describe a parser for command-line options
    parser = optparse.OptionParser()
    parser.add_option('-u', '--username', help='Username of the SoftLayer account (required)')
    parser.add_option('-k', '--api_key', help='API key of the SoftLayer account (required)')
    parser.add_option('-i', '--id', help='ID of the SoftLayer instance to be canceled (required)')
 
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
 
    if not opts.id:
        print('ERROR: ID is required')
        parser.print_help()
        exit(-1)
 
    try:
        # Create a SoftLayer client
        print('Connecting to SoftLayer as %s' % (opts.username))
        client = SoftLayer.Client(username=opts.username, api_key=opts.api_key)
 
        # Cancel a VM
        print('Requesting cancelation of VM with ID: %s' % (opts.id))
        request = client['Virtual_Guest'].deleteObject(id=opts.id)
 
        if request:
            print('Instance with ID: %s removed successfully' % (opts.id))
        else:
            print('Instance with ID: %s not removed successfully' % (opts.id))
    except Exception as e:
        print('Received exception: %s' % (e.faultCode))
        print('Exception details: %s' % (e.faultString))
 
if __name__ == '__main__':
    main()
