# 头文件区域 Headers
import machine
from machine import Pin, PWM, UART

import json
import _thread
import utime

from pwm import pwm_init, pwm_call
from ble import ble_init, ble_config
from mobile import mobile_init
from wlan import wifi_init
from radar import radar_init
from onenet import mqtt_connect, mqtt_send
from controller import ctrl_init

# 全局变量区域 GlobalVars
ip = '0.0.0.0'        # 0.0.0.0 表示没有获取到 IP 地址也就是失败
pwm = None            # pwm 句柄
mobile = None         # 4G 模块句柄
ble = None            # 蓝牙模块句柄
radar = None          # 24G 毫米波雷达模块句柄
client = None         # mqtt 服务句柄
ctl = None            # 全局控制句柄

pwm_pins = [3, 4]     # 3+ 4- 直接初始化 4 为 low 就可以了
mobile_pins = [1, 2]  # 1-RX 2-TX, 连接到 4G 模块
ble_pins = [21, 20]   # 21-RX 20-TX, 连接蓝牙模块
radar_pins = [5]      # 5-IO 反转口，连接毫米波雷达
ctl_pins = [6]        # 控制器接口, 0 表示停用

crypto_key = b"11101101101001001110110000100110"   # 32 位随机数生成

def gpio_irq_handler(io):
    global pwm, client
    print("(gpio_irq_handler) 毫米波雷达中断触发")
    
    if ctl.value() == 0:
        print("(gpio_irq_handler) 停用状态, 退出处理函数")
        return
    
    print("(gpio_irq_handler) 启用状态, 处理中断")
    return
    
    gpio_sts = io.value()
    if gpio_sts == 1:
        print("(gpio_irq_handler) 检测到当前状态为 High, 触发蜂鸣器")
        ret = mqtt_send(client, value=True)
        if ret == False:
            print("(gpio_irq_handler) 发布失败, 重连 MQTT 服务中")
            client = mqtt_connect()
            ret = mqtt_send(client, value=True)
            
            if ret == False:
                print("(gpio_irq_handler) MQTT 服务重连失败, 请检查服务")
                
        pwm_call(pwm)
    elif gpio_sts == 0:
        print("(gpio_irq_handler) 检测到当前状态为 Low")
        ret = mqtt_send(client, value=False)
        if ret == False:
            print("(gpio_irq_handler) 发布失败, 重连 MQTT 服务中")
            client = mqtt_connect()
            ret = mqtt_send(client, value=False)
            
            if ret == False:
                print("(gpio_irq_handler) MQTT 服务重连失败, 请检查服务")

# 主函数运行区域 MAIN
if __name__ == '__main__':
    data = None
    with open("data.json", "r", encoding="utf-8") as f:
        data = json.loads(f.read())
        print("读取到 data:", data)
        
    _, ctl = ctrl_init(ctl, ctl_pins)
    sts = ctl.value()
    print("设备状态为:", "启用" if sts == 1 else "停用")
    
    _, ip = wifi_init(ip, data['wlan_ssid'], data['wlan_password'])
    
    #mobile_init(mobile, pins=mobile_pins)
    
    _, ble = ble_init(ble, pins=ble_pins)
    _, pwm = pwm_init(pwm, pins=pwm_pins)
    _, radar, pwm = radar_init(radar, pwm, pins=radar_pins)
    
    client = mqtt_connect()
    
    io = radar.value()
    print("(Main) 毫米波雷达读数字:", io)
    if io == 1:
        pwm_call(pwm)
    
    # 绑定中断事件, 上升沿触发任务
    radar.irq(trigger=machine.Pin.IRQ_RISING|machine.Pin.IRQ_FALLING, handler=gpio_irq_handler)
    print("(Main) 成功绑定 IRQ 到毫米波雷达")
    
    #ble_config(ble)
