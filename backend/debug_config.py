import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

# 强制重新加载配置
import importlib
import app.config_new
importlib.reload(app.config_new)

from app.config_new import get_config

config = get_config()

print("="*60)
print("调试配置加载")
print("="*60)

print("\n直接访问属性:")
print(f"  hasattr(config, 'ZEP_API_KEY'): {hasattr(config, 'ZEP_API_KEY')}")
print(f"  getattr(config, 'ZEP_API_KEY', None): {getattr(config, 'ZEP_API_KEY', None)}")

print("\n环境变量检查:")
import os
print(f"  os.environ.get('ZEP_API_KEY'): {os.environ.get('ZEP_API_KEY', 'NOT SET')[:30]}..." if os.environ.get('ZEP_API_KEY') else "  NOT SET")
print(f"  os.environ.get('LLM_API_KEY'): {os.environ.get('LLM_API_KEY', 'NOT SET')[:30]}..." if os.environ.get('LLM_API_KEY') else "  NOT SET")

print("\n.env 文件内容检查:")
env_file = os.path.join(os.path.dirname(__file__), '..', '..', '.env')
if os.path.exists(env_file):
    with open(env_file, 'r') as f:
        for line in f:
            if '=' in line and 'API_KEY' in line:
                key, value = line.split('=', 1)
                print(f"  {key}: {value.strip()[:30]}...")
else:
    print("  .env 文件不存在")

print("\n" + "="*60)
print("模拟 GraphBuilderService 的配置选择逻辑")
print("="*60)

if hasattr(config, 'ZEP_API_KEY') and config.ZEP_API_KEY:
    selected_key = config.ZEP_API_KEY
    source = "ZEP_API_KEY"
    print(f"✓ 选择: {source}")
    print(f"  Key: {selected_key[:30]}...")
else:
    selected_key = config.LLM_API_KEY
    source = "LLM_API_KEY (回退)"
    print(f"✗ 回退到: {source}")
    print(f"  Key: {selected_key[:30]}...")
    print(f"  格式验证: {'✓ 以 z_ 开头' if selected_key.startswith('z_') else '✗ 非 Zep 格式（会导致错误！）'}")
