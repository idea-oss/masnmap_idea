# masnmap
masscan + nmap 快速端口存活检测和服务识别。

思路很简单，将masscan在端口探测的高速和nmap服务探测的准确性结合起来，达到一种相对比较理想的效果。
先使用masscan以较高速率对ip存活端口进行探测，再以多进程的方式，使用nmap对开放的端口进行服务探测。

## 安装依赖
需先安装`masscan `、`nmap`和`python-nmap`库。 masscan和nmap请自行安装，python-nmap库可通过如下命令安装。




 
## 参数配置说明
简要参数说明如下：

* ip_file = ''   					 # ip地址
* masscan_exe = '/usr/bin/masscan'   # masscan可执行文件路径
* masscan_rate = 1000000                 # masscan扫描速率
* masscan_file = 'masscan.json'          # masscan扫描结果文件
* process_num = 800				# 执行nmap扫描的进程数量

具体参数值可以自行调优。

## 检测说明
主要执行步骤调用在main函数中，如下：

	def main():
	    # Step 1, run masscan to detect all the open port on all ips
	    run_masscan()

	    # Step 2, extract masscan result file:masscan.json to ip:port format
	    extract_masscan()
	
	    # Step 3, using nmap to scan ip:port
	    run_nmap()
	
	    # Step 4, save results
	    save_results()




## 脚本优化

### 版本探测

如上说明，masnmap.py只是探测服务的，如需获取服务的版本信息，可以使用`-sV`替换`-sS`。

使用如下替换nmap_scan中对应的内容，可以获取服务详细版本信息，但速率会有较大的影响。

```
    ret = nm.scan(ip, port, arguments='-sV')
    # print(ret)
    name = ret['scan'][ip]['tcp'][int(port)]['name']
    product = ret['scan'][ip]['tcp'][int(port)]['product']
    version = ret['scan'][ip]['tcp'][int(port)]['version']
    msg = '{}:{}:{}:{}:{}:{}'.format(index, ip, port, name, product, version)
```

### 其它可优化项

* 使用其它更`有效`的方式替换多进程；
* 针对重要服务的版本探测，提高检测速率；

### 使用
python3 masnmap.py ip或者域名

这里只是修改了一些bug和一些功能
原工具地址https://github.com/starnightcyber/masnmap
