#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 ESM3 API 是否正确
用于验证当前脚本使用的 API 是否与官方文档一致
"""
import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

def test_esm3_imports():
    """测试导入"""
    print("测试 1: 检查 ESM3 模块导入...")
    try:
        import esm
        print(f"  [OK] ESM 包已安装")
        try:
            print(f"  [INFO] ESM 版本: {esm.__version__}")
        except:
            print(f"  [INFO] ESM 路径: {esm.__file__}")
    except ImportError as e:
        print(f"  [FAIL] ESM 包未安装: {e}")
        print("  请运行: pip install esm>=3.2.1.post1")
        return False
    
    try:
        from esm.models.esm3 import ESM3
        print("  [OK] ESM3 model class imported")
    except ImportError as e:
        print(f"  [FAIL] ESM3 import: {e}")
        return False
    
    try:
        from esm.sdk.api import ESMProtein, GenerationConfig
        print("  [OK] ESM SDK API imported")
    except ImportError as e:
        print(f"  [FAIL] ESM SDK import: {e}")
        print("  可能的原因:")
        print("    1. ESM 包版本不正确")
        print("    2. API 已更改，需要更新代码")
        return False
    
    return True

def test_esm3_model_loading():
    """测试模型加载"""
    print("\n测试 2: 检查模型加载...")
    try:
        from esm.models.esm3 import ESM3
        
        print("  正在加载 ESM3 模型 (esm3-sm-open-v1)...")
        print("  注意: 首次加载会下载模型，可能需要一些时间")
        
        model = ESM3.from_pretrained('esm3-sm-open-v1')
        print("  [OK] Model loaded successfully")
        return True, model
    except Exception as e:
        print(f"  [FAIL] Model loading: {e}")
        import traceback
        traceback.print_exc()
        return False, None

def test_esm3_generation(model):
    """测试生成功能"""
    print("\n测试 3: 检查生成功能...")
    if model is None:
        print("  [SKIP] 模型未加载，跳过生成测试")
        return False
    
    try:
        from esm.sdk.api import ESMProtein, GenerationConfig
        
        # 使用短序列测试
        test_sequence = "MKVLWAALLVTFLAGCAKAKGEVVNKVK"
        print(f"  测试序列: {test_sequence[:30]}... (长度: {len(test_sequence)})")
        
        prot = ESMProtein(sequence=test_sequence)
        gen_cfg = GenerationConfig(track='structure', num_steps=8)
        
        print("  正在生成结构...")
        result = model.generate(prot, gen_cfg)
        
        print("  [OK] Generation successful")
        
        # 检查结果
        if hasattr(result, 'to_pdb'):
            print("  [OK] Result has to_pdb method")
        else:
            print("  [WARN] Result does not have to_pdb method")
        
        return True
    except Exception as e:
        print(f"  [FAIL] Generation: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("=" * 60)
    print("ESM3 API 测试")
    print("=" * 60)
    print()
    
    # 测试 1: 导入
    if not test_esm3_imports():
        print("\n" + "=" * 60)
        print("测试失败: 无法导入 ESM3 模块")
        print("=" * 60)
        print("\n建议:")
        print("1. 安装 ESM 包: pip install esm>=3.2.1.post1")
        print("2. 如果已安装，检查版本是否兼容")
        print("3. 查看官方文档确认 API 是否有变化")
        return 1
    
    # 测试 2: 模型加载
    success, model = test_esm3_model_loading()
    if not success:
        print("\n" + "=" * 60)
        print("测试失败: 无法加载 ESM3 模型")
        print("=" * 60)
        print("\n可能的原因:")
        print("1. 模型名称不正确")
        print("2. 网络问题导致无法下载模型")
        print("3. API 调用方式不正确")
        return 1
    
    # 测试 3: 生成功能
    if not test_esm3_generation(model):
        print("\n" + "=" * 60)
        print("测试失败: 生成功能异常")
        print("=" * 60)
        return 1
    
    print("\n" + "=" * 60)
    print("所有测试通过！")
    print("=" * 60)
    print("\n你的 ESM3 脚本 API 使用正确。")
    return 0

if __name__ == "__main__":
    sys.exit(main())
