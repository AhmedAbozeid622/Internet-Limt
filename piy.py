import subprocess 
import requests as r
port = "9080"
data = subprocess.Popen(["sshpass", "-p" ,"admin" ,"ssh" ,"-N" ,"root@ahmedmohsin622.duckdns.org" , "-p", "2000" , "-L", f"{port}:localhost:80"])
# data = subprocess.Popen(["ssh" , "-p",  "admin",  "ssh" , "-N", "root@ahmedmohsin622.duckdns.org" , "-p", "2000" , "-L", "2000:localhost:80"])

# output = data.communicate(timeout=5)
# try:
    # outs, errs = data.communicate(timeout=5)
# except TimeoutExpired:
    # data = data.stdout
    # print(data.read())
    # outs, errs = proc.communicate() 

# rc = data.returncode
# print(output)
# print(rc)
# print(data.pid)
data = r.get(f"http://admin:admin@localhost:{port}/Status_Wireless.live.asp").text
print(data)
