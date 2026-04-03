"""
AES加密工具模块
"""
import base64
import hashlib
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from config.settings import JWT_SECRET


def _get_aes_key() -> bytes:
    """获取AES密钥（从JWT_SECRET派生32字节密钥）"""
    # 使用SHA-256将JWT_SECRET转换为32字节密钥
    return hashlib.sha256(JWT_SECRET.encode()).digest()


def aes_encrypt(plain_text: str) -> str:
    """
    AES-256-CBC加密
    返回Base64编码的加密字符串
    """
    if not plain_text:
        return ""

    key = _get_aes_key()
    # 生成16字节IV（使用密钥的前16字节）
    iv = key[:16]

    cipher = AES.new(key, AES.MODE_CBC, iv)
    padded_data = pad(plain_text.encode('utf-8'), AES.block_size)
    encrypted = cipher.encrypt(padded_data)

    return base64.b64encode(encrypted).decode('utf-8')


def aes_decrypt(encrypted_text: str) -> str:
    """
    AES-256-CBC解密
    输入Base64编码的加密字符串
    """
    if not encrypted_text:
        return ""

    try:
        key = _get_aes_key()
        iv = key[:16]

        cipher = AES.new(key, AES.MODE_CBC, iv)
        encrypted_data = base64.b64decode(encrypted_text)
        decrypted = cipher.decrypt(encrypted_data)
        unpadded = unpad(decrypted, AES.block_size)

        return unpadded.decode('utf-8')
    except Exception:
        # 解密失败返回空字符串
        return ""


def is_encrypted(value: str, data_type: str) -> bool:
    """判断是否需要加密/已加密"""
    return data_type == "encrypted"