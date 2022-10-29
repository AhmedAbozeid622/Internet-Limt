import requests as r
from router.TPLINK_RouterApi import Router
import time
from datetime import datetime
import configparser


Run_config_file = configparser.ConfigParser()
Run_config_file.read('/home/ubuntu/Projects/etisalatApi/configs/InternetLimiter.ini')

API_ENDPOINT = Run_config_file['config']['API_ENDPOINT']
convertValue = float(Run_config_file['config']['convertValue']) 
hours_per_day = float(Run_config_file['config']['hours_per_day']) 



DDWRT_ROUTER  = Router()


retiries = 0
max_retiries = int(Run_config_file['config']['max_retiries']) 

Etisalat_Api_Output = ''
Etisalat_Api_Payment = ''

def getQouteResponse(retiries):
    try:
        Etisalat_Api_Output = r.get(API_ENDPOINT).json()
    except Exception as e:
        last_update = str(datetime.today())
        DDWRT_ROUTER.callDiscordWebhook('error', {
                    'type': 'error' ,
                    'msg': f'The Server is not running\n Author: getQouteResponse()\n Message: {e}',
                    'last-update': last_update
        })
        exit()

    match Etisalat_Api_Output['type']:
        case 'error':
            time.sleep(60)
            if not retiries > max_retiries:
                retiries += 1
                return getQouteResponse(retiries)
            else:
                last_update = str(datetime.today())
                DDWRT_ROUTER.callDiscordWebhook('error', {
                    'type': 'error' ,
                    'msg': 'There is an error in Etisalat Api\n Author: getQouteResponse()',
                    'last-update': last_update
                })
                exit()
        case 'success':
            return Etisalat_Api_Output

def getPaymentResponse(retiries):

    try:
        Etisalat_Api_Payments = r.get(API_ENDPOINT + '/getPayments').json()
    except Exception as e:
        last_update = str(datetime.today())
        DDWRT_ROUTER.callDiscordWebhook('error', {
                    'type': 'error' ,
                    'msg': f'The Server is not running\n Author: getPaymentResponse()\n Message: {e}',
                    'last-update': last_update
        })
        exit()

    match Etisalat_Api_Payments['type']:
        case 'error':
            time.sleep(60)
            if not retiries > max_retiries:
                retiries += 1
                return getPaymentResponse(retiries)
            else:
                last_update = str(datetime.today())
                DDWRT_ROUTER.callDiscordWebhook('error', {
                    'type': 'error' ,
                    'msg': 'There is an error in Etisalat Api \n Author: getPaymentResponse()',
                    'last-update': last_update
                })
                exit()
        case 'success':
            return Etisalat_Api_Payments

Etisalat_Api_Output = getQouteResponse(retiries)
Etisalat_Api_Payment = getPaymentResponse(retiries)

try:
    remainingDays = int(Etisalat_Api_Output['data']["getConsumptionResponse"]["ratePlanConsumption"]["remainingDays"])
except Exception as e:
    print(e)
    last_update = str(datetime.today())
    DDWRT_ROUTER.callDiscordWebhook('Error', {
        'type': 'Error',
        'msg': f"There is an error in remainingDays\n {e} \nEtisalat_Api_Output: {Etisalat_Api_Output}\nEtisalat_Api_Payment: {Etisalat_Api_Payment}",
        'last-update': last_update
    })
    exit()

# check if there 's not an AddOnConsumption (ADDON PLAN) (100 GB)
try:
    ratePlanAddOnConsumption_remainingValue = Etisalat_Api_Output['data']["getConsumptionResponse"]["ratePlanAddOnConsumption"]["consumptionList"]["consumption"]["remainingValue"]
except:
    ratePlanAddOnConsumption_remainingValue = 0

# the amount of main plan (200 GB)
try:
    ratePlanConsumption_remainingValue = Etisalat_Api_Output['data']["getConsumptionResponse"]["ratePlanConsumption"]["consumptionList"]["consumption"]
    ratePlanConsumption_remainingValue = ratePlanConsumption_remainingValue[0]["remainingValue"] if isinstance(ratePlanConsumption_remainingValue, list) else ratePlanConsumption_remainingValue["remainingValue"]
except Exception as e:
    print(e)
    last_update = str(datetime.today())
    DDWRT_ROUTER.callDiscordWebhook('Error', {
        'type': 'Error',
        'msg': f"There is an error in ratePlanConsumption_remainingValue\n {e} \nEtisalat_Api_Output: {Etisalat_Api_Output}\nEtisalat_Api_Payment: {Etisalat_Api_Payment}",
        'last-update': last_update
    })
    exit()

try:
   total_remainingValue = float(ratePlanConsumption_remainingValue) + float(ratePlanAddOnConsumption_remainingValue)
except Exception as e:
    print(e)
    last_update = str(datetime.today())
    DDWRT_ROUTER.callDiscordWebhook('Error', {
        'type': 'Error',
        'msg': f"There is an error in total_remainingValue\n {e} \nEtisalat_Api_Output: {Etisalat_Api_Output}\nEtisalat_Api_Payment: {Etisalat_Api_Payment}",
        'last-update': last_update
    })
    exit()



speed = round(total_remainingValue / remainingDays /  hours_per_day * convertValue)
DDWRT_ROUTER.updateSpeed(speed=str(speed))

try:
    if float(Etisalat_Api_Payment['data']['getOpenAmountResponse']['openAmount']) > 0:
        last_update = str(datetime.today())
        DDWRT_ROUTER.callDiscordWebhook('Warn', {
            'type': 'Warn',
            'msg': f"There is a bill you must pay\n Amount: {Etisalat_Api_Payment['data']['getOpenAmountResponse']['openAmount']} EGP",
            'last-update': last_update
        })
except Exception as e:
    print(e)
    last_update = str(datetime.today())
    DDWRT_ROUTER.callDiscordWebhook('Error', {
        'type': 'Error',
        'msg': f"There is an error in bill\n {e} \nEtisalat_Api_Output: {Etisalat_Api_Output}\nEtisalat_Api_Payment: {Etisalat_Api_Payment}",
        'last-update': last_update
    })
    exit()