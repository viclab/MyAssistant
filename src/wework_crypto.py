import hashlib
import struct
import base64
import socket
import time
import random
import string
import xml.etree.ElementTree as ET
from Crypto.Cipher import AES


class WeworkCrypto:
    def __init__(self, token, encoding_aes_key, corp_id):
        self.token = token
        self.key = base64.b64decode(encoding_aes_key + "=")
        self.corp_id = corp_id

    def _get_sha1(self, *args):
        items = sorted(list(args))
        s = "".join(items)
        return hashlib.sha1(s.encode("utf-8")).hexdigest()

    def verify_signature(self, signature, timestamp, nonce, echo_str=""):
        expected = self._get_sha1(self.token, timestamp, nonce, echo_str)
        return expected == signature

    def decrypt(self, ciphertext):
        cipher = AES.new(self.key, AES.MODE_CBC, self.key[:16])
        plain = cipher.decrypt(base64.b64decode(ciphertext))
        # 去除填充
        pad = plain[-1] if isinstance(plain[-1], int) else ord(plain[-1])
        plain = plain[:-pad]
        # 解析：随机16字节 + 消息长度4字节 + 消息内容 + corpid
        msg_len = struct.unpack(">I", plain[16:20])[0]
        msg_content = plain[20:20 + msg_len].decode("utf-8")
        return msg_content

    def encrypt(self, msg_content):
        random_str = "".join(random.choices(string.ascii_letters + string.digits, k=16))
        msg_bytes = msg_content.encode("utf-8")
        msg_len = struct.pack(">I", len(msg_bytes))
        corp_bytes = self.corp_id.encode("utf-8")
        raw = random_str.encode("utf-8") + msg_len + msg_bytes + corp_bytes
        # PKCS7 填充
        block_size = 32
        pad = block_size - len(raw) % block_size
        raw += bytes([pad] * pad)
        cipher = AES.new(self.key, AES.MODE_CBC, self.key[:16])
        encrypted = base64.b64encode(cipher.encrypt(raw)).decode("utf-8")
        return encrypted

    def gen_signature(self, timestamp, nonce, encrypted_msg):
        return self._get_sha1(self.token, timestamp, nonce, encrypted_msg)

    def build_reply_xml(self, to_user, from_user, msg):
        timestamp = str(int(time.time()))
        nonce = "".join(random.choices(string.digits, k=10))
        encrypted = self.encrypt(msg)
        signature = self.gen_signature(timestamp, nonce, encrypted)
        xml = f"""<xml>
<Encrypt><![CDATA[{encrypted}]]></Encrypt>
<MsgSignature><![CDATA[{signature}]]></MsgSignature>
<TimeStamp>{timestamp}</TimeStamp>
<Nonce><![CDATA[{nonce}]]></Nonce>
</xml>"""
        return xml

    @staticmethod
    def parse_xml(xml_str):
        root = ET.fromstring(xml_str)
        return {child.tag: child.text for child in root}
