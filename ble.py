from machine import Pin, UART
import json
import utime

from utils import AT_trans, aes_decrypt

def ble_init(ble, pins=[21,20]):
    '''
    @ intros: ble_init 用于初始化蓝牙模块相关 UART 控制器
    @ params: pins - list  第一个表示 RX, 第二个表示 TX
    @ params: ble  - UART  后续操作句柄
    @ return: ret  - int   0 表示正常, 其余负数值表示不同的异常
    '''
    try:
        ble = UART(1, 115200, rx=Pin(pins[0]), tx=Pin(pins[1]))
        ble.init(115200, bits=8, parity=None, stop=1) # UART 标准初始化
        
        if ble.any():
            ble.read()
            ble.flush() # 清空缓冲区
        
        utime.sleep_ms(100)
        # 发送 AT 命令试验一下
        ble.write(AT_trans("AT\r\n"))
        
        timeout = 5 # 500ms 连接时间
        while timeout > 0:
            if ble.any():
                break
            timeout -= 1
            utime.sleep_ms(100)
            
        utime.sleep_ms(100)
        response = ble.read() # 读取到 AT OK就是正常的
        
        response = str(response) if response is not None else ""
        if 'OK' in response:
            print("(ble_init) 成功连接到蓝牙模块")
            return 0, ble
        else:
            utime.sleep_ms(10) # 消抖
            if ble.any():
                response_p2 = ble.read() # 第二次尝试
                response_p2 = str(response_p2) if response_p2 is not None else ""
                
                response = response + response_p2
                if 'OK' in response:
                    print("(ble_init) 成功连接到蓝牙模块")
                    return 0, ble
            
            print("(ble_init) 最终失败 response:", response)
            raise Exception("重试后仍未能读取到有效信息")
    except Exception as e:
        print("(ble_init) 发现错误:", e)
        return -1, None
    except:
        print("(ble_init) 发现未知错误")
        return -2, None
    
def ble_config(ble, crypto_key):
    '''
    @ intros: ble_config 用于使用蓝牙初始化单片机内容, 内容使用 AES-256 加密
    @ params: ble         - UART  后续操作句柄
    @ params: crypto_key  - AES-256 解密使用的密钥
    @ return: ret         - int   0 表示正常, 其余负数值表示不同的异常
    '''
    if ble is None:
        print("(ble_config) 蓝牙 UART 未初始化，先执行 ble_init")
        return -1, ble
    
    try:
        print("(ble_config) 等待蓝牙配置数据...")
        timeout = 10  # 10秒超时
        cipher_data = b""
        while timeout > 0:
            if ble.any():
                cipher_data += ble.read()
                if b"\r\n" in cipher_data:
                    cipher_data = cipher_data.strip(b"\r\n")  # 去除结束符
                    break
            timeout -= 1
            utime.sleep_ms(1000)
        
        if not cipher_data:
            print("(ble_config) 超时未接收到配置数据")
            return -1, ble
        
        # 准备进行 AES-256 解密
        cipher_bytes = cipher_data
        
        plain_text = aes_decrypt(cipher_bytes, crypto_key)
        if not plain_text:
            print("(ble_config) 解密失败，空明文")
            return -2, ble
        
        print("(ble_config) 解密后的配置文本:", plain_text)
        
        # 解析 Json 配置
        try:
            config = ujson.loads(plain_text)
        except Exception as e:
            print("(ble_config) JSON解析失败:", e)
            return -3, ble
        
        try:
            if "uart_baudrate" in config:
                pass
            
            
            print("(ble_config) 本机环境配置完成")
            return 0, ble
        
        except Exception as e:
            print("(ble_config) 配置执行失败:", e)
            return -4, ble
    
    except Exception as e:
        print("(ble_config) 未知异常:", e)
        return -1, ble