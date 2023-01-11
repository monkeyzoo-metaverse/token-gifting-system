import socket

from utils.log import log

def port_scan(target_ip, port):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((target_ip, port))
        s.close()
        return True
    except Exception as e:
        s.close()
        log.error(e)
        return False