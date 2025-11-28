import machine
from machine import Pin
from pwm import pwm_init

def radar_init(radar, pwm=None, pins=[5]):
    '''
    @ intros: radar_init 用于初始化毫米波雷达控制器
    @ params: pins   - list   其实只有一个 Pin 口
    @ params: pwm    - PWM    用于检测是否正常开启
    @ params: radax  - Pin    后续操作句柄
    @ return: ret    - int    0 表示正常, 其余负数值表示不同的异常
    '''
    try:
        radar = Pin(pins[0], Pin.IN, Pin.PULL_DOWN) # 没有人的时候是 low 的
        
        if pwm is None:
            pwm_init(pwm) # 初始化 pwm 之后才可以进行绑定不然会出现问题
        
        print("(radar_init) 成功初始化毫米波雷达功能")
        return 0, radar, pwm
    except Exception as e:
        print("(radar_init) 发现错误:", e)
        return -1, None, pwm
    except:
        print("(radar_init) 发现未知错误")
        return -2, None, pwm