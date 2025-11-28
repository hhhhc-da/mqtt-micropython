import machine
from machine import Pin

def ctrl_init(ctl, pins=[6]):
    try:
        ctl = Pin(pins[0], Pin.IN)
        print("(ctrl_init) 红外接收模块初始化成功")
        return 0, ctl
    except Exception as e:
        print("(ctrl_init) 红外接收模块初始化失败:", e)
        return -1, None
    except Exception as e:
        print("(ctrl_init) 红外接收模块未知错误", e)
        return -2, None