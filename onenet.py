from umqtt.simple import MQTTClient
import machine
from machine import Pin
import network, utime

import hashlib
import ubinascii
import ujson

def base64_encode(data: str or bytes) -> str:
    if isinstance(data, str):
        data_bytes = data.encode('utf-8')
    elif isinstance(data, bytes):
        data_bytes = data
    else:
        raise TypeError("输入必须是字符串或字节流")
    b64_bytes = ubinascii.b2a_base64(data_bytes)
    return b64_bytes.decode('utf-8').strip()

def base64_decode(b64_str: str) -> bytes:
    padding = 4 - (len(b64_str) % 4)
    if padding != 4:
        b64_str += '=' * padding
    b64_str = b64_str.replace('%2B', '+').replace('%2F', '/').replace('%3D', '=')
    return ubinascii.a2b_base64(b64_str)

# HMAC-MD5
def hmac_md5(key: bytes, msg: bytes) -> bytes:
    BLOCK_SIZE = 64
    if len(key) > BLOCK_SIZE:
        key = hashlib.md5(key).digest()
    key = key + b'\x00' * (BLOCK_SIZE - len(key)) if len(key) < BLOCK_SIZE else key[:BLOCK_SIZE]

    o_key_pad = b""
    for x in key:
        o_key_pad += bytes([x ^ 0x5c])
    i_key_pad = b""
    for x in key:
        i_key_pad += bytes([x ^ 0x36])
    
    inner_hash = hashlib.md5(i_key_pad + msg).digest()
    hmac_hash = hashlib.md5(o_key_pad + inner_hash).digest()
    return hmac_hash

def hmac_sha256(key: bytes, msg: bytes) -> bytes:
    BLOCK_SIZE = 64
    if len(key) > BLOCK_SIZE:
        key = hashlib.sha256(key).digest()
    key = key + b'\x00' * (BLOCK_SIZE - len(key)) if len(key) < BLOCK_SIZE else key[:BLOCK_SIZE]
    
    o_key_pad = b""
    for x in key:
        o_key_pad += bytes([x ^ 0x5c])
    i_key_pad = b""
    for x in key:
        i_key_pad += bytes([x ^ 0x36])
    
    inner_hash = hashlib.sha256(i_key_pad + msg).digest()
    hmac_hash = hashlib.sha256(o_key_pad + inner_hash).digest()
    return hmac_hash

# OneNET 签名
def onenet_sign(accessKey: str = 'LbPpuWNvnauxa//1aSNvO1Wb3W27o7WXi1OrVfFBHy8',
                StringForSignature: str = "1765420800\nmd5\nproducts/8W284IEf8T/devices/p1\n2018-10-31",
                method: str = "md5") -> str:
    key_bytes = base64_decode(accessKey)
    msg_bytes = StringForSignature.encode('utf-8')
    if method.lower() == "md5":
        hmac_result = hmac_md5(key_bytes, msg_bytes)
    elif method.lower() == "sha256":
        hmac_result = hmac_sha256(key_bytes, msg_bytes)
    else:
        raise ValueError(f"不支持的哈希方法：{method}")

    sign = base64_encode(hmac_result)
    return sign

def url_encode(s: str) -> str:
    encode_map = {
        '%': '%25',
        '+': '%2B',
        ' ': '%20',
        '/': '%2F',
        '?': '%3F',
        '#': '%23',
        '&': '%26',
        '=': '%3D'
    }
    encoded = []
    for c in s:
        encoded.append(encode_map.get(c, c))
    return ''.join(encoded)

def generate_onenet_token_md5(
    access_key: str = "LbPpuWNvnauxa//1aSNvO1Wb3W27o7WXi1OrVfFBHy8",
    product_id: str = "8W284IEf8T",
    device_id: str = "p1"
) -> str:
    """
    生成OneNET MD5加密的Token（适配OneNET的MD5签名方式）
    @ params: access_key - 连接密钥
    @ params: product_id - 产品ID
    @ params: device_id  - 设备名称
    @ return: 完整的Token字符串
    """
    res = f"products/{product_id}/devices/{device_id}"
    method = "md5"
    version = "2018-10-31"
    current_ts = int(utime.time() + 946684800)
    et = current_ts + 3600
    
    sign_str = str(str(et) + '\n' + method + '\n' + res+ '\n' + version)
    sign_md5 = onenet_sign(access_key, sign_str, method="md5")

    final_token = (
        f"version={url_encode(version)}&"
        f"res={url_encode(res)}&"
        f"et={et}&"
        f"method={method}&"
        f"sign={url_encode(sign_md5)}"
    )
    return final_token

def mqtt_send(client, topic="$sys/8W284IEf8T/p1/thing/property/post", value=False):
    # {
    #     "topic": "$sys/8W284IEf8T/p1/thing/property/post",
    #     "data": {
    #         "id": "1764337735479",
    #         "version": "1.0",
    #         "params": {
    #             "flag": {
    #                 "value": true
    #             },
    #             "timestamp": {
    #                 "value": 1764337730
    #             }
    #         }
    #     }
    # }
    
    ndate = utime.localtime()
    
    data = {
        "id": "1764337735479",
        "version": "1.0",
        "params": {
            "flag": {
                "value": value
            },
            "timestamp": {
                "value": f"{ndate[0]}-{ndate[1]}-{ndate[2]} {ndate[3]}:{ndate[4]}:{ndate[5]}"
            }
        }
    }
    
    client.sock.settimeout(100)  # 套接字超时
    try:
        payload = ujson.dumps(data)
        client.publish(topic=topic, msg=payload, retain=False, qos=1)
        print("(mqtt_send) 平台已确认接收数据")
        return True
    except MQTTException as e:
        if "timeout" in str(e).lower():
            print(f"(mqtt_send) 发布超时（{timeout}秒内未收到平台确认）")
        else:
            print(f"(mqtt_send) MQTT错误：{e}")
        return False
    except OSError as e:
        print(f"(mqtt_send) 网络错误：{e}")
        return False
 
def mqtt_connect():
    topic = '$sys/8W284IEf8T/p1/thing/property/post'
    client_id = "p1"
    user_name = "8W284IEf8T" 
    user_password = generate_onenet_token_md5()

    SERVER = "183.230.40.96"
    PORT = 1883

    client = MQTTClient(client_id, SERVER, 0, user_name, user_password, 60)
    client.connect()
    print("(mqtt_connect) 连接成功")
    
    return client

if __name__ == '__main__':
    from wlan import wifi_init
    
    ip = '0.0.0.0'

    data = None
    with open("data.json", "r", encoding="utf-8") as f:
        data = json.loads(f.read())
        print("读取到 data:", data)

    _, ip = wifi_init(ip, data['wlan_ssid'], data['wlan_password'])
    client = mqtt_connect()
    mqtt_send(client, value=False)
