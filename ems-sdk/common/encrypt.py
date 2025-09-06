def rsa_encrypt(encrypt_exponent, modulus, plaintext):
    """
    使用RSA加密算法对明文进行加密。

    参数:
    encrypt_exponent (int): 公钥指数 e
    modulus (int): 模数 n
    plaintext (str): 明文字符串

    返回:
    str: 加密后的密文（以十六进制字符串形式返回）
    """
    # 将明文字符串转换为整数
    message_int = int.from_bytes(plaintext.encode("utf-8"), "big")

    # 计算密文 c = m^e mod n
    ciphertext_int = pow(message_int, encrypt_exponent, modulus)

    # 将密文整数转换为十六进制字符串
    ciphertext_hex = hex(ciphertext_int)[2:]  # 去掉前缀'0x'

    return ciphertext_hex
