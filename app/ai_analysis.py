import aes_gcm_py
import subprocess
import os
from pathlib import Path

# --------------------------
# 基础配置（适配端侧）
# --------------------------
# GGUF模型路径（安卓端建议放在/data/local/tmp下）
GGUF_MODEL_PATH = "/data/local/tmp/xiaobawang_model.gguf"
# llama.cpp可执行文件路径（安卓端编译后的二进制）
LLAMA_CPP_BIN = "/data/local/tmp/llama-cli"
# AES-256密钥存储路径（安卓端建议用KeyStore，这里临时示例）
KEY_FILE_PATH = "/data/local/tmp/aes_key.txt"

# --------------------------
# 密钥管理（端侧安全）
# --------------------------
def generate_and_save_256_key():
    """生成并安全存储AES-256密钥（安卓端替换为KeyStore）"""
    if not os.path.exists(KEY_FILE_PATH):
        key = os.urandom(32).hex()  # 32字节=256位
        with open(KEY_FILE_PATH, "w", encoding="utf-8") as f:
            f.write(key)
        # 安卓端设置文件权限（仅当前用户可读）
        os.chmod(KEY_FILE_PATH, 0o600)
    with open(KEY_FILE_PATH, "r", encoding="utf-8") as f:
        return f.read().strip()

# --------------------------
# 加密/解密（复用之前的C++模块）
# --------------------------
def encrypt_local_data(plaintext):
    """本地加密用户数据"""
    key = generate_and_save_256_key()
    return aes_gcm_py.encrypt_data(plaintext, key), key

def decrypt_local_data(ciphertext, key):
    """本地解密数据"""
    return aes_gcm_py.decrypt_data(ciphertext, key)

# --------------------------
# GGUF模型本地调用（核心）
# --------------------------
def run_gguf_model(prompt, n_ctx=1024, n_threads=4):
    """
    调用llama.cpp加载GGUF模型，端侧本地推理
    :param prompt: 解密后的明文提示词
    :param n_ctx: 上下文窗口大小（适配小霸王模型）
    :param n_threads: 线程数（端侧建议4核）
    :return: 模型推理结果
    """
    if not os.path.exists(GGUF_MODEL_PATH):
        raise FileNotFoundError(f"GGUF模型文件不存在：{GGUF_MODEL_PATH}")
    if not os.path.exists(LLAMA_CPP_BIN):
        raise FileNotFoundError(f"llama.cpp可执行文件不存在：{LLAMA_CPP_BIN}")

    # llama.cpp调用命令（端侧无网络，纯本地）
    cmd = [
        LLAMA_CPP_BIN,
        "-m", GGUF_MODEL_PATH,
        "-p", prompt,
        "-n", "512",  # 生成最大长度
        "--ctx-size", str(n_ctx),
        "--threads", str(n_threads),
        "--no-color",  # 端侧禁用颜色输出
        "--log-disable"  # 禁用日志，减少资源占用
    ]

    try:
        # 执行模型推理（捕获输出）
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60,  # 端侧推理超时（根据模型大小调整）
            cwd=os.path.dirname(LLAMA_CPP_BIN)
        )
        if result.returncode != 0:
            raise RuntimeError(f"模型调用失败：{result.stderr}")
        return result.stdout.strip()
    except subprocess.TimeoutExpired:
        raise TimeoutError("端侧模型推理超时（建议减小上下文窗口）")
    except Exception as e:
        raise RuntimeError(f"GGUF模型调用异常：{str(e)}")

# --------------------------
# 完整流程：加密→解密→GGUF分析
# --------------------------
def privacy_ai_analysis(plaintext_data):
    """
    端侧隐私AI分析主流程：
    1. 本地加密用户数据
    2. 本地解密（仅内存中）
    3. 调用GGUF模型分析（纯本地）
    """
    # 1. 加密
    ciphertext, key = encrypt_local_data(plaintext_data)
    print(f"✅ 数据已本地加密，密文长度：{len(ciphertext)}")

    # 2. 解密（仅在内存中，不落地）
    decrypted_text = decrypt_local_data(ciphertext, key)
    print(f"✅ 数据已本地解密，明文：{decrypted_text[:50]}...")

    # 3. 调用GGUF模型分析
    prompt = f"分析以下数据并输出结论：{decrypted_text}"
    try:
        analysis_result = run_gguf_model(prompt)
        return {
            "status": "success",
            "ciphertext": ciphertext,
            "analysis_result": analysis_result
        }
    except Exception as e:
        return {
            "status": "failed",
            "error": str(e)
        }

# --------------------------
# 测试入口
# --------------------------
if __name__ == "__main__":
    # 测试数据（端侧用户隐私数据）
    test_data = "用户行为数据：2025-12-27 打开APP，浏览商品A，停留5分钟，未下单"
    
    # 执行端侧隐私分析
    result = privacy_ai_analysis(test_data)
    print("\n===== 端侧隐私AI分析结果 =====")
    print(f"状态：{result['status']}")
    if result["status"] == "success":
        print(f"分析结论：\n{result['analysis_result']}")
    else:
        print(f"错误信息：{result['error']}")
