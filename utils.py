import ucryptolib
import utime

def AT_trans(string: str) -> bytes:
    '''
    @ intros: AT_trans 用于整理字符串为指定 bytes 格式
    @ params: string  - str    需要处理的字符串
    @ return: ret     - bytes  处理完成的字符串
    '''
    # 先将 \r\n 替换为占位符（避免重复替换），再替换单独的 \n 为 \r\n，最后恢复占位符
    placeholder = "\x00" 
    processed = string.replace("\r\n", placeholder)
    processed = processed.replace("\n", "\r\n") 
    processed = processed.replace(placeholder, "\r\n")
    
    return processed.encode('utf-8')

def aes_decrypt(ciphertext: bytes, key: bytes) -> str:
    '''
    @ intros: aes_decrypt 解密函数
              AES解密函数（ECB模式）, 密钥需要为 32Bytes - 使用 AES-256 进行加密
              其中密文是16字节的整数倍（存在PKCS7填充）
    @ params: ciphertext  - bytes  待解密的密文字节流
    @ params: key         - bytes  AES-256解密密钥（自动标准化为32字节）
    @ return: ret         - str    解密后的明文字符串（失败返回空字符串）
    '''
    try:
        # 密钥规范化
        key = key[:32] if len(key) > 32 else key.ljust(32, b'\x00')
        aes = ucryptolib.aes(key, 1)  # ECB 模式
        
        plaintext = b""
        block_size = 16
        if len(ciphertext) % block_size != 0:
            raise ValueError(f"密文长度{len(ciphertext)}不是16字节的整数倍")
        
        for i in range(0, len(ciphertext), block_size):
            block = ciphertext[i:i+block_size]
            plaintext += aes.decrypt(block)
        
        # PKCS7规则：最后一个字节的值 = 填充长度（1~16）
        padding_len = plaintext[-1]
        if padding_len < 1 or padding_len > 16:
            raise ValueError(f"无效的PKCS7填充长度: {padding_len}")
        plaintext = plaintext[:-padding_len]
        
        plain_str = plaintext.decode('utf-8')
        timestamp = f"{utime.localtime()[0]}-{utime.localtime()[1]:02d}-{utime.localtime()[2]:02d} " \
                    f"{utime.localtime()[3]:02d}:{utime.localtime()[4]:02d}:{utime.localtime()[5]:02d}"
        print(f"(aes_decrypt) 解密成功, 时间戳: {timestamp}")
        return plain_str
    
    except ValueError as ve:
        print(f"(aes_decrypt) 解密失败（参数/格式错误）: {ve}")
        return ""
    except Exception as e:
        print(f"(aes_decrypt) 解密失败（未知错误）: {e}")
        return ""