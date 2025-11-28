import network
import utime

def wifi_init(ip, account, password):
    '''
    @ intros: wifi_init 用于 WIFI 模块
    @ params: account  - str  WIFI 账号
    @ params: password - str  WIFI 密码
    @ params: ip       - str  最后得到的 ip 地址
    @ return: ret      - int  0 表示正常, 其余负数值表示不同的异常
    '''
    try:
        net = network.WLAN(network.STA_IF)
        timeout = 10 # 失败重连次数为 timeout
        
        print("(wifi_init) 开始连接网络 {}".format(account)) # 不提示我自己都看不出来到哪了
        while timeout > 0:
            if net.active(True):
                net.disconnect() # 避免不必要的意外
                net.connect(account, password)
                
                timeout2 = 5 # 连接只给 timeout2 的时间进行重试，内网环境太慢的话就不考虑了
                while(net.ifconfig()[0] == '0.0.0.0' and timeout2 > 0):
                    timeout2 -= 1
                    utime.sleep(1)
                    
                ip = net.ifconfig()[0]
                print("\n(wifi_init) WIFI 连接成功, IP地址为: {}".format(ip))
                return 0, ip
        else:
            print(".", end='')
            timeout -= 1
            
            if timeout <= 0:
                raise RuntimeError("NetWork Activate Failed")
    except RuntimeError as e:
        if str(e) == "NetWork Activate Failed":
            print("\n(wifi_init) 网络连接失败")
            return -1, ip
        else:
            raise # 复抛到后面去处理就可以了
    except Exception as e:
        print("\n(wifi_init) 捕捉到 Exception:", e)
        return -2, ip
    except:
        print("\n(wifi_init) 未知错误, 请重点考虑此类错误")
        return -3, ip