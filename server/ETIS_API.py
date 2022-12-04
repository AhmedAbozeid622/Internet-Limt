import configparser
from datetime import datetime
import requests as req
import json
import xmltodict
import logging

# interpolation=None
EtisalatApi_config_file = configparser.ConfigParser()
EtisalatApi_config_file.read('/home/ubuntu/Projects/etisalatApi/configs/EtisalatApi.ini')

EtisalatApiLogging_config_file = configparser.ConfigParser()
EtisalatApiLogging_config_file.read('/home/ubuntu/Projects/etisalatApi/configs/EtisalatApiLogging.ini')

class ETIS_API:
    def __init__(self):
        self.headers = {
            "Host": EtisalatApi_config_file['Auth']['Host'],
            "applicationPassword":  str(EtisalatApi_config_file['Auth']['applicationPassword']) ,
            "applicationName":  EtisalatApi_config_file['Auth']['applicationName'] ,
            "Authorization":  EtisalatApi_config_file['Auth']['Authorization']
            }

        self.url = f"https://{EtisalatApi_config_file['Auth']['Host']}"
        
        # self.logger1 = logging.getLogger('ETIS_API_Info')
        self.logger2 = logging.getLogger('ETIS_API_Error')
        self.logger1 = logging.getLogger('ETIS_API_Info')

        self.log_error_handler = logging.FileHandler(EtisalatApiLogging_config_file['Error']['path'])
        self.log_info_handler = logging.FileHandler(EtisalatApiLogging_config_file['Info']['path'])
        
        self.log_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        
        self.log_error_handler.setLevel(logging.ERROR)
        self.log_info_handler.setLevel(logging.WARNING)

        self.log_error_handler.setFormatter(self.log_format)
        self.log_info_handler.setFormatter(self.log_format)
        
        self.logger2.addHandler(self.log_error_handler)
        self.logger1.addHandler(self.log_info_handler)
    @staticmethod 
    def sendToDiscord(msg):
        pass


    def log(self, typeof , data):
        match typeof:
            case 'error':
                self.logger2.error(str(data))
                return
            case 'success':
                self.logger1.warn(data)
                return

    def handleErrors(self, code, data):
        last_update = str(datetime.today())
        output = {
                            "status-code": code,
                            "status-code-info": EtisalatApi_config_file['HttpCodes'][f'{code}'],
                            "type": "error",
                            "data": data,
                            'last-update': last_update
        }
        self.log(output['type'] , output)
        return output

    @staticmethod
    def detect_200_Errors(response):
        response_dict = xmltodict.parse(response.text)
        response_json__Str = json.dumps(response_dict , indent=2)
        response_json = json.loads(response_json__Str)
        
        # errorCode
        if 'getConsumptionResponse' in response_json.keys():
            if 'fault' in response_json['getConsumptionResponse'].keys():
                return True
        
        elif 'getOpenAmountResponse' in response_json.keys():
            if 'fault' in response_json['getOpenAmountResponse'].keys():
                return True
        else:
            return False
        

    def getGenericConsumptions(self):
        try:
            GenericConsumptions_req = req.get(url=self.url + f"/Saytar/rest/servicemanagement/getGenericConsumptions?requestParam={EtisalatApi_config_file['Auth']['GenericConsumptions_requestParam']}" , headers=self.headers)
            content_Type = GenericConsumptions_req.headers["content-Type"].split(";")[0]
            last_update = str(datetime.today())
            print(GenericConsumptions_req.status_code)
            # print(GenericConsumptions_req.text)
            match GenericConsumptions_req.status_code:
                case 200:
                    if(content_Type == 'text/xml') and (self.detect_200_Errors(GenericConsumptions_req) != True):
                        GenericConsumptions_dict = xmltodict.parse(GenericConsumptions_req.text)
                        GenericConsumptions_json__Str = json.dumps(GenericConsumptions_dict , indent=2)
                        GenericConsumptions_json = json.loads(GenericConsumptions_json__Str)

                        out = {
                            "status-code": GenericConsumptions_req.status_code,
                            "status-code-info": EtisalatApi_config_file['HttpCodes']['200'],
                            "type": "success",
                            "data": GenericConsumptions_json,
                            'last-update': last_update
                        }
                        self.log(out['type'] , out)
                        return out       
                    else:
                        return self.handleErrors(200 , GenericConsumptions_req.text)
                case 401:
                    return self.handleErrors(401, GenericConsumptions_req.text)
                case 404:
                    return self.handleErrors(404, GenericConsumptions_req.text)
                case 500:
                    return self.handleErrors(500, GenericConsumptions_req.text)
        except Exception as e:
            last_update = str(datetime.today())
            out = {
                    "type": "error",
                    "exception": str(e),
                    "function": 'getGenericConsumptions()',
                    'last-update': last_update
            }
            self.log('error' , out)
            return out

    def getOpenAmount(self):
        try:
            getOpenAmount_req = req.get(url=self.url + f"/Saytar/rest/customerprofile/openAmount?getOpenAmountRequest={EtisalatApi_config_file['Auth']['GetOpenAmount_requestParam']}" , headers=self.headers)
            content_Type = getOpenAmount_req.headers["content-Type"].split(";")[0]
            last_update = str(datetime.today())
            print(getOpenAmount_req.status_code)
            # print(GenericConsumptions_req.text)
            match getOpenAmount_req.status_code:
                case 200:
                    if(content_Type == 'text/xml') and (self.detect_200_Errors(getOpenAmount_req) != True):
                        GenericConsumptions_dict = xmltodict.parse(getOpenAmount_req.text)
                        GenericConsumptions_json__Str = json.dumps(GenericConsumptions_dict , indent=2)
                        GenericConsumptions_json = json.loads(GenericConsumptions_json__Str)
                        out = {
                            "status-code": getOpenAmount_req.status_code,
                            "status-code-info": EtisalatApi_config_file['HttpCodes']['200'],
                            "type": "success",
                            "data": GenericConsumptions_json,
                            'last-update': last_update
                        }
                        self.log(out['type'] , out)
                        return out       
                    else:
                        return self.handleErrors(200 , getOpenAmount_req.text)
                case 401:
                    return self.handleErrors(401, getOpenAmount_req.text)
                case 404:
                    return self.handleErrors(404, getOpenAmount_req.text)
                case 500:
                    return self.handleErrors(500, getOpenAmount_req.text)
        except Exception as e:
            last_update = str(datetime.today())
            out = {
                    "type": "error",
                    "exception": str(e),
                    "function": 'getOpenAmount()',
                    'last-update': last_update
            }
            self.log('error' , out)
            return out
# api = ETIS_API()
# print(api.getGenericConsumptions())
            