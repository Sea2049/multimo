import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.config_new import get_config

config = get_config()

print("="*60)
print("当前 Zep API Key 配置状态")
print("="*60)
print(f"LLM_API_KEY 已配置: {bool(config.LLM_API_KEY)}")
if config.LLM_API_KEY:
    print(f"Key 前缀: {config.LLM_API_KEY[:10]}...")
    print(f"Key 长度: {len(config.LLM_API_KEY)} 字符")
print("="*60)

if not config.LLM_API_KEY:
    print("\n错误: LLM_API_KEY 未配置!")
    print("\n解决方案:")
    print("1. 在系统环境变量中设置 LLM_API_KEY")
    print("2. 或在 .env 文件中设置 LLM_API_KEY=your_key_here")
    print("3. 或直接编辑 backend/app/config_new.py")
else:
    print("\nAPI Key 已配置,正在测试连接...")
    
    from app.services.graph_builder import GraphBuilderService
    
    try:
        builder = GraphBuilderService(api_key=config.LLM_API_KEY)
        print("✓ GraphBuilderService 初始化成功")
        
        graph_id = "mirofish_fc08b5ea351c491e"
        print(f"\n尝试获取图谱: {graph_id}")
        graph_data = builder.get_graph_data(graph_id)
        
        print(f"\n✓ 成功获取图谱数据!")
        print(f"  节点数: {graph_data.get('node_count', 'N/A')}")
        print(f"  边数: {graph_data.get('edge_count', 'N/A')}")
        
    except Exception as e:
        print(f"\n✗ 连接失败!")
        print(f"错误类型: {type(e).__name__}")
        print(f"错误信息: {str(e)}")
        
        if "401" in str(e) or "unauthorized" in str(e).lower():
            print("\n诊断: API Key 认证失败!")
            print("可能原因:")
            print("  1. API Key 已过期")
            print("  2. API Key 无效")
            print("  3. 账户权限不足")
            print("\n请访问 https://www.getzep.com 获取新的 API Key")
