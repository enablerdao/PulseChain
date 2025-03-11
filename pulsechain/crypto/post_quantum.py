"""
ポスト量子暗号の実装
"""

import os
import base64
import logging
import hashlib
from typing import Tuple, Dict, Any, Optional

# ロガーの設定
logger = logging.getLogger("PostQuantumCrypto")

try:
    # pqcrypto ライブラリがインストールされている場合は使用
    import pqcrypto.sign.dilithium2 as dilithium
    DILITHIUM_AVAILABLE = True
except ImportError:
    DILITHIUM_AVAILABLE = False
    logger.warning("pqcrypto library not available, using fallback implementation")


class DilithiumFallback:
    """
    CRYSTALS-Dilithium の簡易的なフォールバック実装
    注意: これは教育目的の簡易実装です。本番環境では実際のポスト量子暗号ライブラリを使用してください。
    """
    
    @staticmethod
    def keypair() -> Tuple[bytes, bytes]:
        """
        鍵ペアを生成
        
        Returns:
            Tuple[bytes, bytes]: (秘密鍵, 公開鍵)
        """
        # ランダムなシードを生成
        seed = os.urandom(32)
        
        # シードからハッシュを生成
        h = hashlib.sha512(seed)
        hash_bytes = h.digest()
        
        # 前半を秘密鍵、後半を公開鍵として使用
        private_key = hash_bytes[:32]
        public_key = hash_bytes[32:]
        
        # 実際のDilithiumでは鍵のサイズが大きいため、サイズを調整
        private_key = private_key * 4  # 128バイト
        public_key = public_key * 4    # 128バイト
        
        return private_key, public_key
    
    @staticmethod
    def sign(message: bytes, private_key: bytes) -> bytes:
        """
        メッセージに署名
        
        Args:
            message: 署名するメッセージ
            private_key: 秘密鍵
            
        Returns:
            bytes: 署名
        """
        # メッセージと秘密鍵を組み合わせてハッシュを生成
        h = hashlib.sha512(private_key + message)
        signature = h.digest()
        
        # 実際のDilithiumでは署名のサイズが大きいため、サイズを調整
        signature = signature * 4  # 256バイト
        
        return signature
    
    @staticmethod
    def verify(message: bytes, signature: bytes, public_key: bytes) -> bool:
        """
        署名を検証
        
        Args:
            message: 署名されたメッセージ
            signature: 署名
            public_key: 公開鍵
            
        Returns:
            bool: 署名が有効な場合はTrue
        """
        # 実際のDilithiumでは複雑な検証が行われますが、
        # このフォールバック実装では簡易的な検証を行います
        
        # 公開鍵の最初の32バイトを取得
        pk_prefix = public_key[:32]
        
        # メッセージと公開鍵を組み合わせてハッシュを生成
        h = hashlib.sha512(pk_prefix + message)
        expected_prefix = h.digest()[:32]
        
        # 署名の最初の32バイトと比較
        signature_prefix = signature[:32]
        
        # 署名の一部が一致するかどうかを確認
        return hashlib.sha256(expected_prefix).digest()[:16] == hashlib.sha256(signature_prefix).digest()[:16]


class PostQuantumCrypto:
    """ポスト量子暗号を提供するクラス"""
    
    def __init__(self, use_dilithium: bool = True):
        """
        ポスト量子暗号の初期化
        
        Args:
            use_dilithium: Dilithiumを使用するかどうか
        """
        self.use_dilithium = use_dilithium and DILITHIUM_AVAILABLE
        
        if self.use_dilithium:
            logger.info("Using CRYSTALS-Dilithium for post-quantum cryptography")
        else:
            logger.info("Using fallback implementation for post-quantum cryptography")
    
    def generate_keypair(self) -> Tuple[str, str]:
        """
        ポスト量子暗号の鍵ペアを生成
        
        Returns:
            Tuple[str, str]: (秘密鍵, 公開鍵) のBase64エンコードされた文字列
        """
        if self.use_dilithium:
            public_key, private_key = dilithium.keypair()
        else:
            private_key, public_key = DilithiumFallback.keypair()
        
        # Base64エンコード
        private_b64 = base64.b64encode(private_key).decode('utf-8')
        public_b64 = base64.b64encode(public_key).decode('utf-8')
        
        return private_b64, public_b64
    
    def sign(self, message: str, private_key_b64: str) -> str:
        """
        メッセージに署名
        
        Args:
            message: 署名するメッセージ
            private_key_b64: Base64エンコードされた秘密鍵
            
        Returns:
            str: Base64エンコードされた署名
        """
        # 秘密鍵をデコード
        private_key = base64.b64decode(private_key_b64)
        
        # メッセージをバイト列に変換
        message_bytes = message.encode('utf-8')
        
        if self.use_dilithium:
            signature = dilithium.sign(message_bytes, private_key)
        else:
            signature = DilithiumFallback.sign(message_bytes, private_key)
        
        # Base64エンコード
        return base64.b64encode(signature).decode('utf-8')
    
    def verify(self, message: str, signature_b64: str, public_key_b64: str) -> bool:
        """
        署名を検証
        
        Args:
            message: 署名されたメッセージ
            signature_b64: Base64エンコードされた署名
            public_key_b64: Base64エンコードされた公開鍵
            
        Returns:
            bool: 署名が有効な場合はTrue
        """
        try:
            # 公開鍵と署名をデコード
            public_key = base64.b64decode(public_key_b64)
            signature = base64.b64decode(signature_b64)
            
            # メッセージをバイト列に変換
            message_bytes = message.encode('utf-8')
            
            if self.use_dilithium:
                return dilithium.verify(message_bytes, signature, public_key)
            else:
                return DilithiumFallback.verify(message_bytes, signature, public_key)
            
        except Exception as e:
            logger.error(f"Error verifying signature: {e}")
            return False
    
    def derive_address(self, public_key_b64: str) -> str:
        """
        公開鍵からアドレスを導出
        
        Args:
            public_key_b64: Base64エンコードされた公開鍵
            
        Returns:
            str: 16進数形式のアドレス
        """
        # 公開鍵をデコード
        public_key = base64.b64decode(public_key_b64)
        
        # SHA3-256ハッシュを計算
        h = hashlib.sha3_256()
        h.update(public_key)
        digest = h.digest()
        
        # 最初の20バイトを使用
        return digest[:20].hex()
    
    @staticmethod
    def is_quantum_resistant(algorithm: str) -> bool:
        """
        アルゴリズムが量子耐性を持つかどうかを確認
        
        Args:
            algorithm: アルゴリズム名
            
        Returns:
            bool: 量子耐性がある場合はTrue
        """
        quantum_resistant_algorithms = {
            "dilithium", "kyber", "falcon", "sphincs+", "picnic",
            "sike", "bike", "classic-mceliece", "frodokem"
        }
        
        return algorithm.lower() in quantum_resistant_algorithms
    
    def get_algorithm_info(self) -> Dict[str, Any]:
        """
        使用しているアルゴリズムの情報を取得
        
        Returns:
            Dict[str, Any]: アルゴリズム情報
        """
        if self.use_dilithium:
            return {
                "name": "CRYSTALS-Dilithium",
                "version": getattr(dilithium, "__version__", "unknown"),
                "is_quantum_resistant": True,
                "key_size": "2048-bit equivalent",
                "signature_size": "2420 bytes",
                "security_level": "NIST Level 2",
                "implementation": "pqcrypto library"
            }
        else:
            return {
                "name": "Dilithium-Fallback",
                "version": "0.1.0",
                "is_quantum_resistant": False,  # フォールバック実装は実際には量子耐性がない
                "key_size": "128 bytes",
                "signature_size": "256 bytes",
                "security_level": "Educational only",
                "implementation": "Fallback (not secure)"
            }