#!/usr/bin/env python3
"""
HuggingFace 连接诊断工具
"""

import subprocess
import sys
import os
from pathlib import Path

def main():
    print("🔍 HuggingFace 连接诊断工具")
    print("=" * 60)

    # 1. 检查网络连接
    print("\n1️⃣ 测试网络连接到 huggingface.co...")
    try:
        result = subprocess.run(
            ['curl', '-I', '-m', '5', 'https://huggingface.co'],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            print("   ✅ 可以连接到 huggingface.co")
        else:
            print("   ❌ 无法连接到 huggingface.co")
            print(f"   错误输出: {result.stderr[:200]}")
    except FileNotFoundError:
        print("   ⚠️ curl 命令不可用，跳过此测试")
    except Exception as e:
        print(f"   ❌ 连接测试失败: {e}")

    # 2. 检查代理设置
    print("\n2️⃣ 检查代理设置...")
    proxy_vars = ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy', 'NO_PROXY', 'no_proxy']
    proxy_found = False
    for var in proxy_vars:
        val = os.getenv(var)
        if val:
            print(f"   {var} = {val}")
            proxy_found = True
    if not proxy_found:
        print("   ℹ️ 未设置代理环境变量")

    # 3. 检查 token 文件
    print("\n3️⃣ 检查 HuggingFace token 文件...")
    token_file = Path.home() / '.huggingface' / 'token'
    if token_file.exists():
        print(f"   ✅ Token 文件存在: {token_file}")
        try:
            with open(token_file) as f:
                token = f.read().strip()
                if token:
                    print(f"   Token 前缀: {token[:10]}...")
                    print(f"   Token 长度: {len(token)} 字符")
                else:
                    print("   ⚠️ Token 文件为空")
        except Exception as e:
            print(f"   ⚠️ 无法读取 token 文件: {e}")
    else:
        print(f"   ❌ Token 文件不存在: {token_file}")
        print(f"   💡 可以运行: mkdir -p ~/.huggingface && echo 'YOUR_TOKEN' > ~/.huggingface/token")

    # 4. 检查环境变量中的 token
    print("\n4️⃣ 检查环境变量中的 token...")
    hf_token = os.getenv('HF_TOKEN') or os.getenv('HUGGINGFACE_TOKEN')
    if hf_token:
        print(f"   ✅ 环境变量已设置")
        print(f"   Token 前缀: {hf_token[:10]}...")
        print(f"   Token 长度: {len(hf_token)} 字符")
    else:
        print("   ℹ️ 环境变量未设置 HF_TOKEN 或 HUGGINGFACE_TOKEN")

    # 5. 测试 Python requests 库
    print("\n5️⃣ 测试 Python requests 库访问 HuggingFace...")
    try:
        import requests
        response = requests.get('https://huggingface.co', timeout=10)
        print(f"   ✅ requests 可以访问 (HTTP {response.status_code})")
    except ImportError:
        print("   ⚠️ requests 库未安装")
    except requests.exceptions.SSLError as e:
        print(f"   ❌ SSL 错误: {e}")
        print("   💡 可能需要更新 SSL 证书或配置代理")
    except requests.exceptions.ConnectionError as e:
        print(f"   ❌ 连接错误: {e}")
        print("   💡 检查网络连接和防火墙设置")
    except requests.exceptions.Timeout:
        print("   ❌ 连接超时")
        print("   💡 可能需要配置代理或检查网络")
    except Exception as e:
        print(f"   ❌ 访问失败: {type(e).__name__}: {e}")

    # 6. 检查 huggingface_hub 包
    print("\n6️⃣ 检查 huggingface_hub 包...")
    try:
        import huggingface_hub
        print(f"   ✅ huggingface_hub 已安装 (版本: {huggingface_hub.__version__})")
    except ImportError:
        print("   ❌ huggingface_hub 未安装")
        print("   💡 运行: pip install huggingface_hub")

    # 7. 检查 DNS 解析
    print("\n7️⃣ 测试 DNS 解析...")
    try:
        import socket
        ip = socket.gethostbyname('huggingface.co')
        print(f"   ✅ DNS 解析成功: huggingface.co -> {ip}")
    except Exception as e:
        print(f"   ❌ DNS 解析失败: {e}")
        print("   💡 检查 DNS 设置")

    # 8. 总结和建议
    print("\n" + "=" * 60)
    print("📋 诊断总结与建议")
    print("=" * 60)

    has_token_file = token_file.exists()
    has_token_env = bool(hf_token)

    if has_token_file:
        print("\n✅ 你已经有 token 文件，可以跳过笔记本的第 3 步（HuggingFace 认证）")
        print("   直接运行第 4 步开始即可。")
    elif has_token_env:
        print("\n✅ 你已经设置了环境变量 token")
        print("   如果第 3 步仍然失败，尝试创建 token 文件：")
        print(f"   echo '{hf_token}' > ~/.huggingface/token")
    else:
        print("\n💡 推荐的解决方案（按顺序尝试）：")
        print("\n   方案 1: 使用命令行工具登录（推荐）")
        print("   ```bash")
        print("   huggingface-cli login")
        print("   # 然后粘贴你的 token")
        print("   ```")
        print("\n   方案 2: 手动创建 token 文件")
        print("   ```bash")
        print("   mkdir -p ~/.huggingface")
        print("   echo 'YOUR_TOKEN_HERE' > ~/.huggingface/token")
        print("   chmod 600 ~/.huggingface/token")
        print("   ```")
        print("\n   方案 3: 在笔记本中直接设置 token")
        print("   在第 3 步的代码中取消注释并填写：")
        print("   HF_TOKEN = \"your_token_here\"")

    print("\n" + "=" * 60)
    print("诊断完成！查看详细解决方案: fix_huggingface_connection.md")
    print("=" * 60)

if __name__ == '__main__':
    main()

