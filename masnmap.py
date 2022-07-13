#!/usr/bin/python3
# coding=utf-8

import sys
import nmap
import datetime
import json
from queue import Queue
from multiprocessing import Pool
import os
import socket
import re

# masscan_exe = 'masscan'
ip=''
masscan_exe = 'masscan'
masscan_rate = 2000
masscan_file = '/root/masnmap/mmasscan.json'
task_queue = Queue()
result_queue = Queue()
process_num = 50
total_ports = 0
services_info = []


def run_masscan():
    command = 'sudo {}  {} -p0-65535 -oJ {} --rate {}'.format(masscan_exe, ip, masscan_file, masscan_rate)
    msg = 'executing ==> {}'.format(command)
    print(msg)
    os.system(command)
    pass


def extract_masscan():
    """
    extract masscan result file masscan.json into ip:port format, and add to queue
    """
    with open(masscan_file, 'r') as fr:
        tmp_lines  = fr.readlines()
        global total_ports
        total_ports = len(tmp_lines)
        for line in tmp_lines[:-1]:
            tmp = line.strip(',\n')
            tmp= json.dumps(tmp)
            line_json = json.loads(tmp)
            ip = re.findall(r'ip: "(\d+\.\d+\.\d+\.\d+)"', line_json)[0]
            port=re.findall(r'\{port: (\d+)', line_json)[0]
            # extract ip & port
            ip_port = '{}:{}'.format(ip, port)
            task_queue.put(ip_port)
    pass


def nmap_scan(ip_port, index):
    # print('scan ==> {}'.format(ip_port))
    try:
        ip, port = ip_port.split(':')
        nm = nmap.PortScanner()
        ret = nm.scan(ip, port, arguments='-Pn,-sS')
        service = ret['scan'][ip]['tcp'][int(port)]['name']
        msg = ("%s:%s %18s" % (str(ip), str(port), str(service)))
        print(msg)
        return msg
    except:
        print('sth bad happen ...')


def setcallback(msg):
    services_info.append(msg)


def run_nmap():
    pool = Pool(process_num)  # 创建进程池
    index = 0
    while not task_queue.empty():
        index += 1
        ip_port = task_queue.get(timeout=1.0)
        pool.apply_async(nmap_scan, args=(ip_port, index), callback=setcallback)
    pool.close()
    pool.join()


def save_results():
    print('save_results ...')
    print("services {} lines".format(len(services_info)))
    with open("/root/masnmap/services.txt", 'w') as fw:
        for line in services_info:
            fw.write(line+'\n')


def main():
    # Step 1, run masscan to detect all the open port on all ips
    run_masscan()

    # Step 2, extract masscan result file:masscan.json to ip:port format
    extract_masscan()

    # Step 3, using nmap to scan ip:port
    run_nmap()

    # Step 4, save results
    save_results()

def checkip(ip):
    p = re.compile('^((25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(25[0-5]|2[0-4]\d|[01]?\d\d?)$')
    if p.match(ip):
        return True
    else:
        return False

def url_ip(url):
	res = socket.getaddrinfo(url, None)
	ip = res[0][4][0]
	return ip

#判断是否为域名
pattern = re.compile(
    r'^(([a-zA-Z]{1})|([a-zA-Z]{1}[a-zA-Z]{1})|'
    r'([a-zA-Z]{1}[0-9]{1})|([0-9]{1}[a-zA-Z]{1})|'
    r'([a-zA-Z0-9][-_.a-zA-Z0-9]{0,61}[a-zA-Z0-9]))\.'
    r'([a-zA-Z]{2,13}|[a-zA-Z0-9-]{2,30}.[a-zA-Z]{2,3})$'
)

def is_valid_domain(url):
    """ 
    Return whether or not given value is a valid domain.
    If the value is valid domain name this function returns ``True``, otherwise False
    :param value: domain string to validate
    """
    if pattern.match(url):
        ip=url_ip(url)
        return ip
    else:
        print("error domain")
        sys.exit(0)
if __name__ == '__main__':
    ip = sys.argv[1]
    if checkip(ip) == False:
    	ip=is_valid_domain(ip)
    else:
    	pass    	
    start = datetime.datetime.now()
    main()
    end = datetime.datetime.now()
    spend_time = (end - start).seconds
    msg = 'It takes {} process {} seconds to run ... {} tasks'.format(process_num, spend_time, total_ports)
    print(msg)
