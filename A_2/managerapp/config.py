#instance  user1
image_id = ''
Iam_profile = { 'Name': ''}
SecurityGroup_id = ['']
key_name = ''
# define userdata to run user-app at instance launch
user_data = 'Content-Type: multipart/mixed; boundary="//"\n' \
            'MIME-Version: 1.0\n' \
            '--//\n' \
            'Content-Type: text/cloud-config; charset="us-ascii"\n' \
            'MIME-Version: 1.0\n' \
            'Content-Transfer-Encoding: 7bit\n' \
            'Content-Disposition: attachment; filename="cloud-config.txt"\n' \
            '#cloud-config\n' \
            'cloud_final_modules:\n' \
            '- [scripts-user, always]\n' \
            '--//\n' \
            'Content-Type: text/x-shellscript; charset="us-ascii"\n' \
            'MIME-Version: 1.0\n' \
            'Content-Transfer-Encoding: 7bit\n' \
            'Content-Disposition: attachment; filename="userdata.txt"\n' \
            '#!/bin/bash\n' \
            'screen\n' \
            '/home/ubuntu/Desktop/ece1779a1/start.sh\n' \
            '--//'
#elb target group ARN
targetgroup = ''
targetgroupARN = ''
#elb
loadbalancer = ''
loadbalancerARN = ''
loadbalancerDNS = ''
