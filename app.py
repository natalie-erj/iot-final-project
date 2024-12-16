import random
import time
# from azure.iot.device import IoTHubDeviceClient, Message
import random
import time
import sys
from iothub_client import IoTHubClient, IoTHubClientError, IoTHubTransportProvider, IoTHubClientResult
from iothub_client import IoTHubMessage, IoTHubMessageDispositionResult, IoTHubError, DeviceMethodReturnValue
import config as config
import RPi.GPIO as GPIO
from Adafruit_BME280 import *
import re
from telemetry import Telemetry

PROTOCOL = IoTHubTransportProvider.MQTT
# TO DO -- replace Device ID and Shared Access Key from the information under your device when you press 'connect' at https://iot-final-project.azureiotcentral.com/
"HostName=iot-final-project.azure-devices.net;DeviceId=nat-raspberry-pi;SharedAccessKey=APJ0BbVo8ov8tUhoICzSpygLodvBhOLXOWkD2ZkfnvM="
telemetry = Telemetry()


if len(sys.argv) < 2:
    print ( "You need to provide the device connection string as command line arguments." )
    telemetry.send_telemetry_data(None, EVENT_FAILED, "Device connection string is not provided")
    sys.exit(0)

def is_correct_connection_string():
    m = re.search("HostName=.*;DeviceId=.*;", CONNECTION_STRING)
    if m:
        return True
    else:
        return False

CONNECTION_STRING = sys.argv[1]

if not is_correct_connection_string():
    print ( "Device connection string is not correct." )
    telemetry.send_telemetry_data(None, EVENT_FAILED, "Device connection string is not correct.")
    sys.exit(0)


def iothub_client_init():
    # prepare iothub client
    client = IoTHubClient(CONNECTION_STRING, PROTOCOL)
    client.set_option("product_info", "HappyPath_RaspberryPi-Python")
    if client.protocol == IoTHubTransportProvider.HTTP:
        client.set_option("timeout", TIMEOUT)
        client.set_option("MinimumPollingTime", MINIMUM_POLLING_TIME)
    # set the time until a message times out
    client.set_option("messageTimeout", MESSAGE_TIMEOUT)
    # to enable MQTT logging set to 1
    if client.protocol == IoTHubTransportProvider.MQTT:
        client.set_option("logtrace", 0)
    client.set_message_callback(
        receive_message_callback, RECEIVE_CONTEXT)
    if client.protocol == IoTHubTransportProvider.MQTT or client.protocol == IoTHubTransportProvider.MQTT_WS:
        client.set_device_twin_callback(
            device_twin_callback, TWIN_CONTEXT)
        client.set_device_method_callback(
            device_method_callback, METHOD_CONTEXT)
    return client

def output_to_dict(result_path):
    # Parse the result.txt file from the command line call
    with open(result_path) as f:
        begin = False
        EIP_count = 0
        output = []
        for line in f:
            if "Enter Image Path:" in line:
                EIP_count += 1
            if begin == True and EIP_count == 1:
                result = line.split("\t")
                output.append(result[0])
            if "./img.jpg" in line:
                begin = True
    
    # Replace the keys with your class names
    count_items = {"banana" : 0,
                "apple" : 0,
                "potato": 0}

    # Increment the count of the relevant class for each instance
    for item in output:
        result = item.split(":")
        item_type = result[0]
        count_items[item_type] += 1

    return count_items
  
 
  
def iothub_client_send_telemetry(message):  
    client = iothub_client_init()  
    print("Attempting to Send Messages to Azure IoT")  
    print("Sending message: {}".format(message))  
    client.send_message(message)  
    print("Message Sent")
  
if __name__ == '__main__':  
    message = output_to_dict('result.txt')
    iothub_client_send_telemetry(str(message))
