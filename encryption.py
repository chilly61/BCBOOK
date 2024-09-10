import base58
import base64
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
import hashlib

# A 生成完整的个人信息


def generate_personal_info(name, email, phone, address, passport):
    return {
        "name": name,
        "email": email,
        "phone": phone,
        "address": address,
        "passport": passport
    }

# A 使用 B 的公钥加密个人信息


def encrypt_personal_info(personal_info, public_key_b):
    # 将个人信息转换为字符串形式并加密
    info_bytes = str(personal_info).encode()
    encrypted_info = public_key_b.encrypt(
        info_bytes,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return encrypted_info

# B 使用私钥解密个人信息


def decrypt_personal_info(encrypted_info, private_key_b):
    decrypted_info = private_key_b.decrypt(
        encrypted_info,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return decrypted_info.decode()

# 计算信息的哈希值


def calculate_hash(data):
    return hashlib.sha256(data.encode()).hexdigest()


def generate_public_key_string():
    private_key_alice = rsa.generate_private_key(
        public_exponent=65537, key_size=2048)
    public_key_alice = private_key_alice.public_key()
    # 将公钥序列化为PEM格式（字节）
    pem_private_key = private_key_alice.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption()  # 无加密
    )
    private_alice = base64.b64encode(pem_private_key).decode('utf-8')

    pem_public_key = public_key_alice.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    public_alice = base64.b64encode(pem_public_key).decode('utf-8')
    return public_alice, private_alice, public_key_alice, private_key_alice


def create_did(decrypted_info, public_alice):
    # 将个人信息拼接成字符串形式
    personal_info_string = decrypted_info
    # 添加公钥，确保每个DID与公钥相关联
    combined_info = personal_info_string + public_alice

    # Step 2: 对拼接后的字符串进行哈希处理 (可用SHA-256)
    did_hash = hashlib.sha256(combined_info.encode('utf-8')).hexdigest()

    # Step 3: 将哈希结果进行Base64编码（或直接使用哈希值作为DID）
    did = base64.b64encode(did_hash.encode('utf-8')).decode('utf-8')

    return did


'''
# A 生成完整的个人信息并加密发送给 B
personal_info = generate_personal_info(
    "John Doe", "john.doe@example.com", "1234567890", "123 Main St, Anytown, USA", "P1234567")

# B 生成公私钥对
private_key_b = rsa.generate_private_key(public_exponent=65537, key_size=2048)
public_key_b = private_key_b.public_key()

# A 使用 B 的公钥加密个人信息
encrypted_info = encrypt_personal_info(personal_info, public_key_b)

# A 计算加密信息的哈希值，用于链上记录
hash_value = calculate_hash(str(encrypted_info))
print(f"A 生成的哈希值: {hash_value}")

# B 解密个人信息
decrypted_info = decrypt_personal_info(encrypted_info, private_key_b)
print(f"B 解密后的个人信息: {decrypted_info}")

# 假设链上记录的是hash值和B的审核签名
# 审核通过后B的签名可以类似于：
# signature = B_sign(hash_value)
'''
