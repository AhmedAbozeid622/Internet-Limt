import requests as r
from socket import gethostbyname
from base64 import b64encode
import configparser
import logging
import time
from datetime import datetime

Router_config_file = configparser.ConfigParser()
Router_config_file.read('/home/ubuntu/Projects/etisalatApi/configs/Router.ini')

RouterLogging_config_file = configparser.ConfigParser()
RouterLogging_config_file.read('/home/ubuntu/Projects/etisalatApi/configs/RouterLogging.ini')

class Router:
    def __init__(self):
        self.RouterURL = f'http://{Router_config_file["auth"]["hostname"]}:{Router_config_file["auth"]["port"]}'
        self.RouterHeader = { 
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.87 Safari/537.36",
        "Upgrade-Insecure-Requests": "1",
        "Referer": f'http://{Router_config_file["auth"]["hostname"]}/mainFrame.htm'
        }
        self.RouterCookies = {
            "Authorization": f"""Basic {b64encode(f"{Router_config_file['auth']['username']}:{Router_config_file['auth']['password']}".encode('utf-8')).decode('utf-8')}""",
        }
        self.logger2 = logging.getLogger('Router_API_Error')
        self.logger1 = logging.getLogger('Router_API_Info')

        self.log_error_handler = logging.FileHandler(RouterLogging_config_file['Error']['path'])
        self.log_info_handler = logging.FileHandler(RouterLogging_config_file['Info']['path'])
        
        self.log_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        
        self.log_error_handler.setLevel(logging.ERROR)
        self.log_info_handler.setLevel(logging.WARNING)

        self.log_error_handler.setFormatter(self.log_format)
        self.log_info_handler.setFormatter(self.log_format)
        
        self.logger2.addHandler(self.log_error_handler)
        self.logger1.addHandler(self.log_info_handler)

        self.DiscordWebhook = 'https://discord.com/api/webhooks/986758602855424030/DT1Wcuk-TKHaCXGLRjL3JtucKTa7Uligc9lMLtIBNlfk5uPrndmus5ALa_ISFFG5wFAQ'
        self.tries = 0
        self.maxTries = 600
        self.Pass = 0


        self.checkHostIp()
        self.checkAuth()
        self.oldSpeed = self.getCurrentSpeed()
    
    def checkAuth(self):
        try:
            response = r.get(
            f'{self.RouterURL}/' ,
            headers=self.RouterHeader, #Send Base64 encoded from text
            cookies=self.RouterCookies
            )

            if "curlock" not in response.text: # If Unauthorized
                last_update = str(datetime.today())
                self.log(typeof='error' , msg={
                    'title': "Error in Authorization (401 Code)",
                    'function': "checkAuth()",
                    "ip_address": gethostbyname(Router_config_file["auth"]["hostname"]),
                    "message": "username or password may be wrong",
                    'last-update': last_update
                })
                self.callDiscordWebhook('error' , {
                    'type': 'Error',
                    'msg': "Error in Authorization (401 Code) \n username or password may be wrong",
                    'function': "checkAuth()",
                    "ip_address": gethostbyname(Router_config_file["auth"]["hostname"]),
                    "message": "username or password may be wrong",
                    'last-update': last_update
                })
                exit()
                return False
        
        except Exception as e:
            last_update = str(datetime.today())
            self.log('error' , msg={
                    'type': "error",
                    'title': "Error in TPLINK CONNECTION",
                    'function': "checkAuth()",
                    "ip_address": gethostbyname(Router_config_file["auth"]["hostname"]),
                    "message": e,
                    'last-update': last_update
                })
            self.callDiscordWebhook('error' , {
                    'type': "error",
                    'msg': f"Error in TPLINK CONNECTION \n {e}",
                    'function': "checkAuth()",
                    "ip_address": gethostbyname(Router_config_file["auth"]["hostname"]),
                    'last-update': last_update
                })
            exit()

        return True

    def updateSpeed(self , speed: str):
        self.newSpeed = speed
        ### check if ip is right ###
        self.checkHostIp()
        ### End of Check ip is right ###

        RouterEndPoint = f"{self.RouterURL}/cgi?2"
        headers = self.RouterHeader
        
        # enable_bandwith_control = 3 # 0 for disable
        body = f"[TC#0,0,0,0,0,0#0,0,0,0,0,0]0,4\r\nenable=3\r\nlinkType=0\r\nupTotalBW=10000\r\ndownTotalBW={speed}\r\n"


        try:
            response = r.post(url=RouterEndPoint , headers=headers , cookies=self.RouterCookies, data=body , timeout=2)
            if response.text.split("\n")[-1] == '[error]0':
                match self.checkSpeed():
                    case True:
                        last_update = str(datetime.today())
                        data = {
                            'type': 'suceess',
                            'msg': f'The speed updated Succesfully. \n The current speed is {self.newSpeed} \n The oldspeed is {self.oldSpeed}',
                            'last-update': last_update
                        }
                        self.log('suceess' , str(data))
                        self.logger1.warning(data)
                        self.callDiscordWebhook('success', data)
                        print(data)

                    case False:
                        last_update = str(datetime.today())
                        data = {
                        'type': 'error',
                        'msg': str(e) + '\n The speed not updated',
                        'last-update': last_update
                        }
                        self.log('error' , data)
                        self.callDiscordWebhook('error', data)
                        print(data)
            else:
                last_update = str(datetime.today())
                data = {
                    'type': 'error',
                    'msg': str(response.text) + '\n The speed not updated',
                    'last-update': last_update
                    }
                self.log('error' , data)
                self.callDiscordWebhook('error', data)
                print(data)
        
        except Exception as e:
            last_update = str(datetime.today())
            data = {
                'type': 'error',
                'msg': str(e) + '\n Error in updateSpeed()',
                'last-update': last_update
            }
            self.log('error' , data)
            self.callDiscordWebhook('error', data)
            print(data)

    def checkHostIp(self):
        if self.tries > self.maxTries :
            last_update = str(datetime.today())
            self.log('error',{
                'type': 'error',
                "msg": "max tries is reached. app is shuted down\n Author: checkHostIp()",
                'last-update': last_update
            })
            self.callDiscordWebhook('error' , {
                'type': 'error',
                "msg": "max tries is reached. app is shuted down\n Author: checkHostIp()",
                'last-update': last_update
            })
            exit()

        self.tries += 1

        ip = gethostbyname(Router_config_file["auth"]["hostname"])
        if self.Pass != 1:
            for something in ip.split("."):
                if type(something) != type(int()):
                    last_update = str(datetime.today())
                    data = {
                        'type': 'error',
                        'msg': str(ip) + '\n Error in HOSTNAME IP ADDRESS \nPlease Restart Router',
                        'last-update': last_update
                    }
                    self.Pass = 1
        try:
            response = r.get(f'http://{ip}:{Router_config_file["auth"]["port"]}', headers=self.RouterHeader,timeout=1)
            if(response.status_code != 200):
                if(response.status_code == 401):
                    self.log('error' , {'type':'error' , 'msg' : 'Username or Password is not correnct'})
                    self.callDiscordWebhook('error' , {'type':'error' , 'msg' : 'Username or Password is not correnct'})
                else:
                    self.handleErrors(response)
        except Exception as e:
            print(e)
            time.sleep(60)
            self.checkHostIp()

    def checkSpeed(self):
        tplink_QOS_endpoint = self.RouterURL + '/cgi?1&5&5'
        text_data = """[TC#0,0,0,0,0,0#0,0,0,0,0,0]0,0
[TC_RULE#0,0,0,0,0,0#0,0,0,0,0,0]1,0
[LAN_WLAN#0,0,0,0,0,0#0,0,0,0,0,0]2,17
name
Standard
SSID
RegulatoryDomain
PossibleChannels
AutoChannelEnable
Channel
X_TP_Bandwidth
Enable
SSIDAdvertisementEnabled
BeaconType
BasicEncryptionModes
WPAEncryptionModes
IEEE11iEncryptionModes
X_TP_Configuration_Modified
WMMEnable
X_TP_FragmentThreshold
"""
        post_data = text_data.replace("\n" , "\r\n") + "\r\n"
        QOS_DATA = r.post(url=tplink_QOS_endpoint , headers=self.RouterHeader , cookies=self.RouterCookies , data=post_data)
        QOS_DATA_SPLITED_BY_NEWLINE = QOS_DATA.text.split("\n")
        QOS_DATA_DICT = {}
        if QOS_DATA_SPLITED_BY_NEWLINE[-1] == '[error]0':
            for Line in QOS_DATA_SPLITED_BY_NEWLINE:
                if "=" in Line:
                    data = Line.split('=')
                    QOS_DATA_DICT.update({data[0]: data[1]})
        else:
            last_update = str(datetime.today())
            data = {
                        'type': 'error',
                        'msg': str(QOS_DATA.text) + '\n Error in checkSpeed()',
                        'last-update': last_update
            }
            self.log('error' , data)
            self.callDiscordWebhook('error', data) # Some log stuff
            exit()

        speed = ''
        if QOS_DATA_DICT.get("downTotalBW"):
            speed = QOS_DATA_DICT.get("downTotalBW")
        
        return int(self.newSpeed) == int(speed)

    def getCurrentSpeed(self):
        tplink_QOS_endpoint = self.RouterURL + '/cgi?1&5&5'
        text_data = """[TC#0,0,0,0,0,0#0,0,0,0,0,0]0,0
[TC_RULE#0,0,0,0,0,0#0,0,0,0,0,0]1,0
[LAN_WLAN#0,0,0,0,0,0#0,0,0,0,0,0]2,17
name
Standard
SSID
RegulatoryDomain
PossibleChannels
AutoChannelEnable
Channel
X_TP_Bandwidth
Enable
SSIDAdvertisementEnabled
BeaconType
BasicEncryptionModes
WPAEncryptionModes
IEEE11iEncryptionModes
X_TP_Configuration_Modified
WMMEnable
X_TP_FragmentThreshold
"""
        post_data = text_data.replace("\n" , "\r\n") + "\r\n"
        QOS_DATA = r.post(url=tplink_QOS_endpoint , headers=self.RouterHeader , cookies=self.RouterCookies, data=post_data)
        QOS_DATA_SPLITED_BY_NEWLINE = QOS_DATA.text.split("\n")
        QOS_DATA_DICT = {}
        if QOS_DATA_SPLITED_BY_NEWLINE[-1] == '[error]0':
            for Line in QOS_DATA_SPLITED_BY_NEWLINE:
                if "=" in Line:
                    data = Line.split('=')
                    QOS_DATA_DICT.update({data[0]: data[1]})
        else:
            last_update = str(datetime.today())
            data = {
                        'type': 'error',
                        'msg': str(QOS_DATA.text) + '\n Error in getCurrentSpeed()',
                        'last-update': last_update
            }
            self.log('error' , data)
            self.callDiscordWebhook('error', data) # Some log stuff
        
        speed = ''
        
        if QOS_DATA_DICT.get("downTotalBW"):
            speed = QOS_DATA_DICT.get("downTotalBW")
        
        return int(speed) if speed != '' else False

    def handleErrors(self, response):
        last_update = str(datetime.today())
        output = {
                            "status-code": response.status_code,
                            "status-code-info": RouterLogging_config_file['HttpCodes'][f'{response.status_code}'],
                            "type": "error",
                            "data": response.text,
                            'last-update': last_update
        }
        self.log('error' , output)
        data = {
        "content": f"""Type: **Error**
Message: **{output['data']}**
Last-Update: **{output['last-update']}**
status-code: **{output['status-code']}**
status-code-info: **{output['status-code-info']}**
        """,
        "embeds": None
        }
        post = r.post(url=self.DiscordWebhook , data=data)  
        exit()      

    def log(self, typeof , msg):
        match typeof:
            case 'error':
                self.logger2.error(str(msg))
                return
            case 'success':
                self.logger1.warning(msg)
                return 

    def callDiscordWebhook(self , typeof , msg):
        data = {
        "content": f"""Type: **{typeof}**
Message: **{msg['msg']}**
Last-Update: **{msg['last-update']}**
        """,
        "embeds": None
        }
        post = r.post(url=self.DiscordWebhook , data=data)
        return True
