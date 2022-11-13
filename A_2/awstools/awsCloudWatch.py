import time
import datetime
from dateutil.tz import tzutc
import boto3
from awstools.credential import ConfigAWS


class CloudwatchAPI(object):

    def __init__(self, aws_access_key_id, aws_secret_access_key):
        self.client = boto3.client('cloudwatch',
                                   region_name='us-east-1',
                                   aws_access_key_id=aws_access_key_id,
                                   aws_secret_access_key=aws_secret_access_key)

    def createCloudwatchClient(aws_access_key_id, aws_secret_access_key):
        '''
        Generate a cloudwatch client.
        Use __init__ instead.
        '''
        return

    def putCacheMissRate(self, missrate, instance_name):
        '''
        Send Memcache Miss Rate to AWS CloudWatch. Return a response message.
        missrate: value to send
        instance_name: current memcache instance identifier (could be anything based on your implementation)
        '''
        response = self.client.put_metric_data(
            MetricData=[{
                'MetricName': 'miss_rate',
                'Dimensions': [{
                    'Name': 'instance',
                    'Value': instance_name
                }],
                'Unit': 'Percent',
                'Value': missrate}],
            Namespace='ece1779/memcache')
        return response

    def getCacheMissRateStatistics(self, instances: list, intervals=60, period=60):
        '''
        Get miss rate STATISTICS from a specified server from cloudwatch. return a dict containing responses.
        retrieve the average missrate value in responses[i]['Datapoints'][-1]['Average']
        instances: List of instance names used to specify the dimension of metrics
        intervals:  Starttime = Endtime - intervals
        period:    of which to be calculated together as average.
                len(responses[i]['Datapoints']) == intervals // periods
        '''
        responses = []
        for i in instances:
            responses.append(
                self.client.get_metric_statistics(
                    Namespace='ece1779/memcache',
                    MetricName='miss_rate',
                    Dimensions=[{
                        "Name": "instance",
                        "Value": i
                    }],
                    StartTime=datetime.datetime.utcnow() - datetime.timedelta(seconds=intervals),
                    EndTime=datetime.datetime.utcnow(),
                    Period=period,
                    # Statistics=['Average'],
                    Statistics=['Maximum'],
                    Unit='Percent',
                )
            )
        return responses

    def getLastMeanMissRate(self, responses):
        '''
        Calculate the global miss rate of past 1 minute, with responses from cloudwatch given.
        responses: responses returned by getCacheMissRateStatistics(self, instances: list, intervals=60, period=60)
        '''
        sum_mean = 0
        numOfinstances = 0
        for i in responses:
            datapoints = i['Datapoints']
            if len(datapoints) == 0:
                # print('Current Instance have no datapoint in response, skipping.......')
                continue
            elif len(datapoints) == 1:
                latest_data = datapoints[0]
                numOfinstances += 1
            else:  # len(datapoints) > 1
                numOfinstances += 1
                timestamps = [j['Timestamp'] for j in datapoints]
                timestamps.sort()
                latest_data = None
                for data in datapoints:
                    if data['Timestamp'] == timestamps[-1]:
                        latest_data = data
                        break
            if latest_data is None:
                raise Exception('Error finding latest datapoint when processing responces')
            else:
                print('Retrieve data from cloudwatch ......')
                print(latest_data['Maximum'])
                sum_mean += latest_data['Maximum']
        if numOfinstances == 0:
            return 0.0
        else:
            return sum_mean / numOfinstances


if __name__ == '__main__':
    cli = CloudwatchAPI(ConfigAWS.aws_access_key_id, ConfigAWS.aws_secret_access_key)
    # test upload
    for i in range(10):
        print(str(i) + '.................')
        resp = cli.putCacheMissRate(i * 0.01, 'test2')
        print(resp)
        resp = cli.putCacheMissRate(1 - i * 0.01, 'test3')
        print(resp)
        time.sleep(10)

    # test download
    response = cli.getCacheMissRateStatistics(['test2', 'test3'], intervals=60, period=60)
    print(response)
    with open("./logs/cloudwatch.log", 'a') as f:
        f.write(str(response))
