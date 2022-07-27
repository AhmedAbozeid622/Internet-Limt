import requests as r
from socket import gethostbyname
from base64 import b64encode
import configparser
import logging
import time
from bs4 import BeautifulSoup
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
        "Authorization": f"""Basic {b64encode(f"{Router_config_file['auth']['username']}:{Router_config_file['auth']['password']}".encode('utf-8')).decode('utf-8')}""",
        'Connection':'close'
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
        self.maxTries = 30

        self.checkHostIp()
        self.checkAuth()
        self.oldSpeed = self.getCurrentSpeed()
    
    def checkAuth(self):
        try:
            response = r.get(
            f'{self.RouterURL}/Status_Wireless.live.asp' ,
            headers=self.RouterHeader #Send Base64 encoded from text
            )

            if response.status_code == 401: # If Unauthorized
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
                    'title': "Error in DDWRT CONNECTION",
                    'function': "checkAuth()",
                    "ip_address": gethostbyname(Router_config_file["auth"]["hostname"]),
                    "message": e,
                    'last-update': last_update
                })
            self.callDiscordWebhook('error' , {
                    'type': "error",
                    'msg': "Error in DDWRT CONNECTION \n {e}",
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

        RouterEndPoint = f"{self.RouterURL}/apply.cgi"
        headers = self.RouterHeader
        headers.update({
        "Content-Type": "application/x-www-form-urlencoded",
        "Origin": self.RouterURL,
        "Referer": f'{self.RouterURL}/QoS.asp',
        })
        
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

        try:
            response = r.post(url=RouterEndPoint , headers=headers , data=body , timeout=2)
        except Exception as e:
            print('I will sleep for 111 seconds and i will check for you.')
            print('\n Sleeeping .......')
            time.sleep(111)

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
        ddwrt_QOS_endpoint = self.RouterURL + '/QoS.asp'
        QOS_DATA = r.get(url=ddwrt_QOS_endpoint , headers=self.RouterHeader)
        soup = BeautifulSoup(QOS_DATA.text, 'html.parser')
        # isEnabled = soup.findAll('input', attrs={'class':'spaceradio', "name":'wshaper_enable'})[0].get('checked') # if not None it is enabled
        speed = soup.find('input', attrs={'name': 'wshaper_downlink'}).get('value')
        return int(self.newSpeed) == int(speed)

    def getCurrentSpeed(self):
        ddwrt_QOS_endpoint = self.RouterURL + '/QoS.asp'
        QOS_DATA = r.get(url=ddwrt_QOS_endpoint , headers=self.RouterHeader)
        soup = BeautifulSoup(QOS_DATA.text, 'html.parser')
        speed = soup.find('input', attrs={'name': 'wshaper_downlink'}).get('value')
        return int(speed)

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
