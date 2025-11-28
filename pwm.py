from machine import Pin, PWM
import utime

def pwm_init(pwm, pins:list=[3,4]):
    '''
    @ intros: pwm_init 用于初始化 pwm 控制器
    @ params: pins - list  第一个表示 pwm 正极, 第二个表示 pwm 负极
    @ params: pwm  - PWM   后续操作句柄
    @ return: ret  - int   0 表示正常, 其余负数值表示不同的异常
    '''
    try:
        pwm = PWM(Pin(pins[0]))
        pwm.freq(1000)
        pwm.duty(0) # duty 是 0-1023 的一个占空比控制
        
        pin = Pin(pins[1], Pin.OUT)
        pin.value(0) # 直接 low 负极
        
        print("(pwm_init) 成功开启 PWM 功能")
        return 0, pwm
    except Exception as e:
        print("(pwm_init) 发现错误:", e)
        return -1, None
    except:
        print("(pwm_init) 发现未知错误")
        return -2, None
    
def pwm_call(pwm):
    '''
    @ intros: pwm_call 蜂鸣器正常运行
    @ params: pwm  - PWM   pwm 操作句柄
    @ return: ret  - int   0 表示正常, 其余负数值表示不同的异常
    '''
    try:
        pwm.duty(256)
        utime.sleep_ms(50)
        pwm.duty(0)
        utime.sleep_ms(50)
        pwm.duty(256)
        utime.sleep_ms(50)
        pwm.duty(0)
        utime.sleep_ms(50)
        pwm.duty(256)
        utime.sleep_ms(50)
        pwm.duty(0)
        utime.sleep_ms(50)
        pwm.duty(256)
        utime.sleep_ms(50)
        pwm.duty(0)
        utime.sleep_ms(1250)
        
        pwm.duty(256)
        utime.sleep_ms(200)
        pwm.duty(0)
        utime.sleep_ms(250)
        pwm.duty(256)
        utime.sleep_ms(150)
        pwm.duty(0)

        print("(pwm_call) PWM 警报触发")
    except Exception as e:
        print("(pwm_call) 发现错误:", e)
    except:
        print("(pwm_call) 发现未知错误")