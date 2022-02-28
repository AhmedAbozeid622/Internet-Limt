import requests as r
import sshtunnel

sshtunnel.SSH_TIMEOUT = 0.1
with sshtunnel.open_tunnel(
    ("ahmedmohsin622.duckdns.org", 2000),
    ssh_username="root",
    ssh_pkey="private",
    remote_bind_address=("127.0.0.1", 80),
    local_bind_address=('0.0.0.0', 2000)
) as tunnel:
    data = r.get(f"http://admin:@adminlocalhost:2000/Status_Wireless.live.asp").text
    print(data)

print('FINISH!')
