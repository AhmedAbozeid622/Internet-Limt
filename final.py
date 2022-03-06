
import requests as r
import json
import xmltodict
import time
from bs4 import BeautifulSoup

times = 0
########################
url = "https://mab.etisalat.com.eg:11003/Saytar/rest/servicemanagement/getGenericConsumptions?requestParam=%3C?xml%20version=%221.0%22?%3E%3CdialAndLanguageRequest%3E%3CsubscriberNumber%3E553650654%3C/subscriberNumber%3E%3Clanguage%3E1%3C/language%3E%3C/dialAndLanguageRequest%3E"
headers = {
    "Host": "mab.etisalat.com.eg:11003",
    "applicationPassword":"zFZyqUpqeO9TMhXg4R/9qs0Igwg=",
    "applicationName":"MAB",
    "Authorization":"Basic NTUzNjUwNjU0LDIxMDk0NDEwLUM4MDItNEJBMS1BQTdDLTIzOEEwRDMxOEUxRTo5em4haHZ3Xyt0LXNmLnUp"
}
########################


##### Color Functions ####
def prRed(skk): print("\033[91m {}\033[00m" .format(skk))
########################

def LOG(message, type):
    prRed(message)

# Handle HTTP Requests Errors
def handleErrors(data):
    retry = 0 # FALSE
    # status_code = data.status_code
    # Data = data.data

    # Handle ErrorCode SE_SDP_1
    try:
        if data["getConsumptionResponse"]["fault"]:
            print(f'Error Message: {data["getConsumptionResponse"]["fault"]["userMessageEn"]}')
        if data["getConsumptionResponse"]["fault"]["retry"] == "true":
            retry = 1
            LOG(f'Error Message: {data["getConsumptionResponse"]["fault"]["userMessageEn"]}' , "error")
            return retry
    except:
        pass


    return retry

import urllib.request
def checkInternet(host='http://google.com'):
    try:
        urllib.request.urlopen(host) #Python 3.x
        return True
    except:
        return False

    

# Make GET Request
def getData(url , headers):
    # time.sleep(5)
    # print("connected" if checkInternet() else "no internet!")
    # True if checkInternet() else getData(url , headers)
    
    try:
        Account_Data_xml = r.get(url=url , headers=headers)
        content_Type = Account_Data_xml.headers["content-Type"].split(";")[0]
    except:
        LOG("There is Error in HTTP REQUEST", "error")
        getData(url , headers)

    if content_Type == "text/xml" and Account_Data_xml.status_code == 200:
        #coverting xml to Python dictionary
        Account_Data_dict = xmltodict.parse(Account_Data_xml.text)
        Account_Data_json__Str = json.dumps(Account_Data_dict , indent=2)
        Account_Data_json = json.loads(Account_Data_json__Str)
        if handleErrors(Account_Data_json) == 1:
            getData(url , headers)
        else:
            return Account_Data_json
    
    elif content_Type == "text/html" and Account_Data_xml.status_code == 401:
        if Account_Data_xml.text == "Unauthorized":
            LOG("Unauthorized (ERROR applicationPassword or applicationName)", "error")
            exit()
        soup = BeautifulSoup(Account_Data_xml.text, 'html.parser')
        LOG(f"{soup.title.text}" , "error")
        LOG(f"{soup.p.text}" , "error")
        print(f"Error in Etisalat_API Authorization; content-type: {content_Type}; ({Account_Data_xml.status_code})")
        LOG(f"Error in Etisalat_API Authorization; content-type: {content_Type}; ({Account_Data_xml.status_code})" , "error")
        exit()
    elif Account_Data_xml.status_code == 504:
        print("Error in Etisalat_API SERVER")
        LOG("Error in Etisalat_API SERVER")
        getData(url , headers)
    else:
        LOG(f"({Account_Data_xml.status_code}); {content_Type}; \n{Account_Data_xml}", "error")
        exit()

# Calc Download Speed
def countSpeed(data):
    convertValue = 2276.86703 
    hours_per_day = 12
    
    # remainingDays to renew 
    remainingDays = int(data["getConsumptionResponse"]["ratePlanConsumption"]["remainingDays"])

    # check if there 's not an AddOnConsumption (ADDON PLAN) (100 GB)
    try:
        ratePlanAddOnConsumption_remainingValue = data["getConsumptionResponse"]["ratePlanAddOnConsumption"]["consumptionList"]["consumption"]["remainingValue"]
    except:
        ratePlanAddOnConsumption_remainingValue = 0

    # the amount of main plan (200 GB)
    ratePlanConsumption_remainingValue = data["getConsumptionResponse"]["ratePlanConsumption"]["consumptionList"]["consumption"]
    ratePlanConsumption_remainingValue = ratePlanConsumption_remainingValue[0]["remainingValue"] if isinstance(ratePlanConsumption_remainingValue, list) else ratePlanConsumption_remainingValue["remainingValue"]


    total_remainingValue = float(ratePlanConsumption_remainingValue) + float(ratePlanAddOnConsumption_remainingValue)


    speed = round(total_remainingValue / remainingDays /  hours_per_day * convertValue)
    print(speed)
    return speed

# Send request to ddwrt to change speed
def changeSpeed(ip,speed):
    url = f"http://admin:admin@{ip}/apply.cgi"

    headers = { 
        "Content-Type": "application/x-www-form-urlencoded",
        "Origin": f"http://{ip}",
        "Referer": f"http://{ip}/apply.cgi",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.87 Safari/537.36",
        "Upgrade-Insecure-Requests": "1"
    }


    body = {
        "submit_button": "QoS", 
        "action": "ApplyTake",
        "change_action": "gozila_cgi",
        "submit_type": "save" , 
        "commit": "1",
        "wshaper_enable": "1",
        "wshaper_dev": "WAN",
        "qos_type": "0",
        "qos_aqd": "sfq",
        "wshaper_downlink": speed,
        "wshaper_uplink": "1000",
        "svqos_nosvcs": "0",
        "add_svc": "100bao",
        "svqos_nodevs": "0",
        "svqos_dev": "br0",
        "svqos_noips": "0",
        "svqos_ipaddr0": "0",
        "svqos_ipaddr1": "0",
        "svqos_ipaddr2": "0",
        "svqos_ipaddr3": "0",
        "svqos_netmask": "0",
        "svqos_nomacs": "0",
        "svqos_hwaddr0": "00",
        "svqos_hwaddr1": "00",
        "svqos_hwaddr2": "00",
        "svqos_hwaddr3": "00",
        "svqos_hwaddr4": "00",
        "svqos_hwaddr5": "00",
        "default_downlevel": "100000",
        "default_uplevel": "100000",
        "default_lanlevel": "100000"
}

    data = r.post(url=url , headers=headers, data=body)
    if data.status_code == 200:
        return True
    else:
        return "There is error in DDWRT"

ip = "192.168.5.1"
# DATA = 
speed = countSpeed(getData(url , headers))
# input()
# print(speed)
# print(changeSpeed(ip, speed))
