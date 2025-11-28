from machine import Pin, UART
import utime

from utils import AT_trans, aes_decrypt

def mobile_init(mobile, pins:list=[1,2]):
    '''
    @ intros: mobile_init 用于初始化 4G 模块相关 UART 控制器
    @ params: pins    - list  第一个表示 RX, 第二个表示 TX
    @ params: mobile  - UART  后续操作句柄
    @ return: ret     - int   0 表示正常, 其余负数值表示不同的异常
    '''
    try:
        mobile = UART(2, 115200, rx=Pin(pins[0]), tx=Pin(pins[1]))
        mobile.init(115200, bits=8, parity=None, stop=1) # UART 标准初始化
        
        if mobile.any():
            mobile.read()
            mobile.flush() # 清空缓冲区
        
        utime.sleep_ms(100)
        # 发送 AT 命令试验一下
        mobile.write(AT_trans("AT\r\n"))
        
        timeout = 5 # 500ms 连接时间
        while timeout > 0:
            if mobile.any():
                break
            timeout -= 1
            utime.sleep_ms(100)
            
        utime.sleep_ms(100)
        response = mobile.read() # 读取到 AT OK就是正常的
        
        response = str(response) if response is not None else ""
        if 'OK' in response:
            print("(mobile_init) 成功连接到蓝牙模块")
            return 0
        else:
            utime.sleep_ms(10) # 消抖
            if mobile.any():
                response_p2 = mobile.read() # 第二次尝试
                response_p2 = str(response_p2) if response_p2 is not None else ""
                
                response = response + response_p2
                if 'OK' in response:
                    print("(mobile_init) 成功连接到 4G 模块")
                    return 0
            
            print("(mobile_init) 最终失败 response:", response)
            raise Exception("重试后仍未能读取到有效信息")
    except Exception as e:
        print("(mobile_init) 发现错误:", e)
        return -1
    except:
        print("(mobile_init) 发现未知错误")
        return -2