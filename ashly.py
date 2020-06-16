#!/usr/bin/env python3

import socket


def_ashly_port = 3100
def_ashly_timeout = 3000
def_ashly_retry = 2
ashly_getmac_command = 'F8F8F8F8FFFFFFFFFFFFFFFFFFFFFFFF20000000FF'
ashly_channel_command = '8F8F8F8F{0}00000000{1}{2}FF'
ashly_command = '8F8F8F8F{0}00000000{1}FF'

class AshlyAPI():
    def __init__(self, timeout=def_ashly_timeout, retry=def_ashly_retry):
        self.timeout = timeout
        if retry>0:
            self.retry = retry
        else:
            self.retry = 1
        self.sock = None

    def socket_open(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.settimeout(self.timeout/1000)

    def socket_close(self):
        self.sock.close()
        self.sock = None

    def send_wait_receive(self, ipaddress, port, command):
        if not self.sock:
            self.socket_open()
            sock_close = True
        else:
            sock_close = False
        result = None
        for i in range(self.retry):
            self.sock.sendto(command, (ipaddress, port))
            try:
                result = self.sock.recvfrom(1024)
                result = result[0]
                break
#            except socket.timeout:
            except:
                 result = None
        if sock_close:
            self.socket_close()
        return result

    def getmac(self, ipaddress, port):
        macaddress = self.send_wait_receive(ipaddress, port, hex2bytes(ashly_getmac_command))
        if macaddress:
            macaddress = bytes2hex(macaddress[10:16]).upper()
        return macaddress

    def run_command_for_channel(self, ipaddress, port, command, macaddress, channel):
        return self.send_wait_receive(ipaddress, port, 
            hex2bytes(ashly_channel_command.format(macaddress, command, int2hex(channel))))

    def run_command(self, ipaddress, port, command, macaddress):
        return self.send_wait_receive(ipaddress, port, 
            hex2bytes(ashly_command.format(macaddress, command)))

    def run_command_for_all_channels(self, ipaddress, port, command, macaddress):
        results = {}
        for i in range(24):
            result = self.run_command_for_channel(ipaddress, port, command, macaddress, i)
            if result[18]==0:
                break
            results[i] = result
        return results

    def run_commands(self, ipaddress, port, commands, macaddress):
        results = {}
        multi_command = ''
        for icommand, vcommand in commands.items():
            multi_command = multi_command + vcommand['command']
        answer = self.run_command(ipaddress, port, multi_command, macaddress)
        answer = answer[14:-1]
        for icommand, vcommand in commands.items():
            if not answer:
                break
            datasize = answer[1]
            if answer[0]!=hex2int(vcommand['command'][0:2]):
                continue
            command_datasize = hex2int(vcommand['command'][2:4])
            value = answer[command_datasize+2:datasize+2]
            if vcommand['type'] == 0:
                results[icommand] = bytes2int(value)
            elif vcommand['type'] == 1:
                results[icommand] = value.strip(b'\x00').decode('utf-8')
            elif vcommand['type'] == 2:
                for i in range (0, datasize):
                   results[icommand+"_"+ str(i)] = value[i]
            elif vcommand['type'] == 3:
                results[icommand] = bytes2int(value)
            answer = answer[datasize+2:]
        return results

def hex2bytes(hexstr):
    bytes = []
    s = ''.join(hexstr.split(' ')).upper()
    return bytearray.fromhex(s)

def bytes2hex(bytes):
    return bytes.hex()

def int2hex(i):
    return '{:02x}'.format(i)

def hex2int(h):
    return int(h, 16)

def bytes2int(bytes):
    return int.from_bytes(bytes, "big")


if __name__ == "__main__":
    sys.exit(0)
