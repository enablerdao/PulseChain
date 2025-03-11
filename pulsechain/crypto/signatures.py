"""
暗号署名機能を提供するモジュール
"""

import base64
from typing import Tuple, Optional
from cryptography.hazmat.primitives.asymmetric import padding, rsa, utils
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.exceptions import InvalidSignature


def generate_key_pair() -> Tuple[str, str]:
    """
    RSA鍵ペアを生成する
    
    Returns:
        Tuple[str, str]: (秘密鍵, 公開鍵) のBase64エンコードされた文字列
    """
    # RSA鍵ペアを生成
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )
    
    # 秘密鍵をPEM形式でシリアライズ
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    
    # 公開鍵を取得してPEM形式でシリアライズ
    public_key = private_key.public_key()
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    
    # Base64エンコード
    private_b64 = base64.b64encode(private_pem).decode('utf-8')
    public_b64 = base64.b64encode(public_pem).decode('utf-8')
    
    return private_b64, public_b64


def _load_private_key(private_key_b64: str) -> rsa.RSAPrivateKey:
    """Base64エンコードされた秘密鍵を読み込む"""
    private_pem = base64.b64decode(private_key_b64)
    return serialization.load_pem_private_key(
        private_pem,
        password=None
    )


def _load_public_key(public_key_b64: str) -> rsa.RSAPublicKey:
    """Base64エンコードされた公開鍵を読み込む"""
    public_pem = base64.b64decode(public_key_b64)
    return serialization.load_pem_public_key(public_pem)


def sign_data(data: str, private_key_b64: str) -> str:
    """
    データに署名する
    
    Args:
        data: 署名するデータ（文字列）
        private_key_b64: Base64エンコードされた秘密鍵
        
    Returns:
        str: Base64エンコードされた署名
    """
    private_key = _load_private_key(private_key_b64)
    
    # データをバイト列に変換して署名
    signature = private_key.sign(
        data.encode('utf-8'),
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    
    # 署名をBase64エンコード
    return base64.b64encode(signature).decode('utf-8')


def verify_signature(data: str, signature_b64: str, public_key_b64: str) -> bool:
    """
    署名を検証する
    
    Args:
        data: 署名されたデータ（文字列）
        signature_b64: Base64エンコードされた署名
        public_key_b64: Base64エンコードされた公開鍵
        
    Returns:
        bool: 署名が有効な場合はTrue、そうでない場合はFalse
    """
    try:
        public_key = _load_public_key(public_key_b64)
        signature = base64.b64decode(signature_b64)
        
        # 署名を検証
        public_key.verify(
            signature,
            data.encode('utf-8'),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return True
    except (InvalidSignature, ValueError, TypeError):
        return False


def derive_address_from_public_key(public_key_b64: str) -> str:
    """
    公開鍵からアドレスを導出する
    
    Args:
        public_key_b64: Base64エンコードされた公開鍵
        
    Returns:
        str: 16進数形式のアドレス
    """
    public_key = _load_public_key(public_key_b64)
    public_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    
    # SHA-256ハッシュを計算
    h = hashes.Hash(hashes.SHA256())
    h.update(public_bytes)
    digest = h.finalize()
    
    # 最初の40文字（20バイト）を使用
    return digest.hex()[:40]