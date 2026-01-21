import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.config_new import get_config

config = get_config()

print("="*60)
print("测试新的配置逻辑")
print("="*60)

print(f"\n配置检查:")
print(f"  LLM_API_KEY: {'已配置' if config.LLM_API_KEY else '未配置'}")
if config.LLM_API_KEY:
    print(f"    值: {config.LLM_API_KEY[:15]}... (长度: {len(config.LLM_API_KEY)})")
    print(f"    格式: {'✓ 以 z_ 开头' if config.LLM_API_KEY.startswith('z_') else '✗ 非 Zep 格式'}")

print(f"  ZEP_API_KEY: {'已配置' if config.ZEP_API_KEY else '未配置'}")
if config.ZEP_API_KEY:
    print(f"    值: {config.ZEP_API_KEY[:20]}... (长度: {len(config.ZEP_API_KEY)})")
    print(f"    格式: {'✓ 以 z_ 开头' if config.ZEP_API_KEY.startswith('z_') else '✗ 非 Zep 格式'}")

print("\n" + "="*60)
print("将使用的 Key:")
print("="*60)

# 模拟代码中的逻辑
if config.ZEP_API_KEY:
    selected_key = config.ZEP_API_KEY
    source = "ZEP_API_KEY"
else:
    selected_key = config.LLM_API_KEY
    source = "LLM_API_KEY (回退)"

if selected_key:
    print(f"  来源: {source}")
    print(f"  Key: {selected_key[:20]}...")
    print(f"  格式验证: {'✓ 有效' if selected_key.startswith('z_') else '✗ 无效（应为 z_ 开头）'}")
else:
    print("  ✗ 没有可用的 API Key!")

print("\n" + "="*60)
print("实际测试 Zep 连接:")
print("="*60)

if selected_key and selected_key.startswith('z_'):
    from app.services.graph_builder import GraphBuilderService
    
    try:
        builder = GraphBuilderService()
        print("✓ GraphBuilderService 初始化成功!")
        
        # 测试获取图谱数据
        graph_id = "mirofish_fc08b5ea351c491e"
        print(f"\n尝试获取图谱: {graph_id}")
        graph_data = builder.get_graph_data(graph_id)
        
        print(f"\n✓ 成功获取图谱数据!")
        print(f"  节点数: {graph_data.get('node_count', 'N/A')}")
        print(f"  边数: {graph_data.get('edge_count', 'N/A')}")
        
    except ValueError as ve:
        print(f"\n✗ 配置错误: {ve}")
    except Exception as e:
        print(f"\n✗ 连接失败!")
        print(f"  错误类型: {type(e).__name__}")
        print(f"  错误信息: {str(e)[:100]}...")
else:
    print("\n✗ 无法测试：没有有效的 Zep API Key")
    print("  请确保 .env 文件中包含有效的 ZEP_API_KEY")
