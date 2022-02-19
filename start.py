import requests as r
import xmltodict
import json
import datetime

######################
# 12  number of active hours on internet

# New number 
## 2276.86703 ##

# old number 
## ١٨٩.٧٣ => 190 ##

######################

## Constants ##
convertValue = 2276.86703 
hours_per_day = 12
ERROR_CODE = 401
####################

# Important is  applicationPassword and Authorization [you must get them from the etisalat_app]
headers = {
    "Host": "mab.etisalat.com.eg:11003",
    "applicationPassword":"ZFZyqUpqeO9TMhXg4R/9qs0Igwg=",
    "applicationName":"MAB",
    "Authorization":"Basic NTUzNjUwNjU0LDIxMDk0NDEwLUM4MDItNEJBMS1BQTdDLTIzOEEwRDMxOEUxRTo5em4haHZ3Xyt0LXNmLnUp"
}

url = "https://mab.etisalat.com.eg:11003/Saytar/rest/servicemanagement/getGenericConsumptions?requestParam=%3C?xml%20version=%221.0%22?%3E%3CdialAndLanguageRequest%3E%3CsubscriberNumber%3E553650654%3C/subscriberNumber%3E%3Clanguage%3E1%3C/language%3E%3C/dialAndLanguageRequest%3E"

Account_Data_xml = r.get(url=url , headers=headers)

if Account_Data_xml.status_code == ERROR_CODE:
    print("Error in Etisalat_API")
    exit()



#coverting xml to Python dictionary
Account_Data_dict = xmltodict.parse(Account_Data_xml.text)
Account_Data_json__Str = json.dumps(Account_Data_dict , indent=2)
Account_Data_json = json.loads(Account_Data_json__Str)

# remainingDays to renew 
remainingDays = int(Account_Data_json["getConsumptionResponse"]["ratePlanConsumption"]["remainingDays"])

# check if there 's not an AddOnConsumption (ADDON PLAN) (100 GB)
try:
    ratePlanAddOnConsumption_remainingValue = Account_Data_json["getConsumptionResponse"]["ratePlanAddOnConsumption"]["consumptionList"]["consumption"]["remainingValue"]
except:
    ratePlanAddOnConsumption_remainingValue = 0

# the amount of main plan (200 GB)
ratePlanConsumption_remainingValue = Account_Data_json["getConsumptionResponse"]["ratePlanConsumption"]["consumptionList"]["consumption"]
ratePlanConsumption_remainingValue = ratePlanConsumption_remainingValue[0]["remainingValue"] if isinstance(ratePlanConsumption_remainingValue, list) else ratePlanConsumption_remainingValue["remainingValue"]


total_remainingValue = float(ratePlanConsumption_remainingValue) + float(ratePlanAddOnConsumption_remainingValue)


speed = round(total_remainingValue / remainingDays /  hours_per_day * convertValue)
print(total_remainingValue)
print(speed)

# Send request to ddwrt to change speed
def changeSpeed(speed):
    ip = "ahmedmohsin622.duckdns.org:2000"
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

# print(changeSpeed(speed))


file = open("file.txt", "a")
file.write(f"{str(datetime.datetime.now())} \n")
file.close()
# input()

# عنترة ابن ابن شداد
