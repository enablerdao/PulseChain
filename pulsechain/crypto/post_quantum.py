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
    
    # Dilithiumのパラメータ
    SECURITY_LEVEL = 2  # NIST Level 2
    N = 256  # 多項式次数
    Q = 8380417  # モジュラス
    D = 13  # 切り捨てビット数
    TAU = 39  # 署名のスパース性パラメータ
    
    @staticmethod
    def keypair() -> Tuple[bytes, bytes]:
        """
        鍵ペアを生成
        
        Returns:
            Tuple[bytes, bytes]: (秘密鍵, 公開鍵)
        """
        # ランダムなシードを生成
        seed = os.urandom(32)
        
        # シードからハッシュを生成して擬似的な多項式を作成
        h1 = hashlib.sha512(seed + b"s1")
        h2 = hashlib.sha512(seed + b"s2")
        h3 = hashlib.sha512(seed + b"A")
        
        # 秘密鍵と公開鍵のコンポーネントを生成
        s1 = h1.digest()  # 秘密多項式1
        s2 = h2.digest()  # 秘密多項式2
        a = h3.digest()   # 公開パラメータA
        
        # 公開鍵t = A*s1 + s2 を計算（実際には複雑な多項式演算）
        # ここでは簡易的にXORとハッシュで代用
        t = bytes(x ^ y for x, y in zip(
            hashlib.sha512(a + s1).digest(),
            s2[:64]
        ))
        
        # 秘密鍵と公開鍵をパッケージ化
        private_key = seed + s1 + s2 + t[:64]  # seed + s1 + s2 + t
        public_key = seed + t  # seed + t
        
        # 実際のDilithiumでは鍵のサイズが大きいため、サイズを調整
        if len(private_key) < 1312:  # Dilithium2の秘密鍵サイズ
            private_key = private_key * (1312 // len(private_key) + 1)
            private_key = private_key[:1312]
        
        if len(public_key) < 1184:  # Dilithium2の公開鍵サイズ
            public_key = public_key * (1184 // len(public_key) + 1)
            public_key = public_key[:1184]
        
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
        # 秘密鍵からコンポーネントを抽出
        seed = private_key[:32]
        s1 = private_key[32:96]
        s2 = private_key[96:160]
        
        # メッセージハッシュを計算
        mu = hashlib.sha3_512(message).digest()
        
        # 署名生成のためのランダム値
        rho = hashlib.sha256(seed + mu).digest()
        
        # ランダムマスクベクトルyを生成（実際には複雑な多項式サンプリング）
        y = hashlib.sha512(rho + b"y").digest()
        
        # チャレンジcを生成
        c = hashlib.sha3_256(mu + y).digest()
        
        # z = y + c*s1 を計算（実際には多項式演算）
        # ここでは簡易的にXORとハッシュで代用
        z = bytes(x ^ y for x, y in zip(
            y[:64],
            hashlib.sha512(c + s1).digest()[:64]
        ))
        
        # h = c*s2 を計算（実際には多項式演算）
        h = hashlib.sha512(c + s2).digest()[:64]
        
        # 署名を構築
        signature = c + z + h
        
        # 実際のDilithiumでは署名のサイズが大きいため、サイズを調整
        if len(signature) < 2420:  # Dilithium2の署名サイズ
            signature = signature * (2420 // len(signature) + 1)
            signature = signature[:2420]
        
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
        try:
            # 署名と公開鍵からコンポーネントを抽出
            if len(signature) < 32 + 64 + 64:
                return False
                
            c = signature[:32]
            z = signature[32:96]
            h = signature[96:160]
            
            seed = public_key[:32]
            t = public_key[32:96]
            
            # メッセージハッシュを計算
            mu = hashlib.sha3_512(message).digest()
            
            # 公開パラメータAを再生成
            a = hashlib.sha512(seed + b"A").digest()
            
            # Az - ct を計算（実際には多項式演算）
            # ここでは簡易的にXORとハッシュで代用
            az = hashlib.sha512(a + z).digest()[:64]
            ct = hashlib.sha512(c + t).digest()[:64]
            w_prime = bytes(x ^ y for x, y in zip(az, ct))
            
            # 再計算したチャレンジc'
            c_prime = hashlib.sha3_256(mu + w_prime).digest()
            
            # c == c' かチェック（タイミング攻撃を防ぐため一定時間比較）
            return DilithiumFallback._constant_time_compare(c, c_prime)
            
        except Exception as e:
            logger.error(f"Verification error: {e}")
            return False
    
    @staticmethod
    def _constant_time_compare(a: bytes, b: bytes) -> bool:
        """タイミング攻撃を防ぐための一定時間比較"""
        if len(a) != len(b):
            return False
        
        result = 0
        for x, y in zip(a, b):
            result |= x ^ y
        
        return result == 0


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