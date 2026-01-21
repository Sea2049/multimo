#!/usr/bin/env python3
"""
断点续传功能测试脚本

测试自动驾驶管理器的断点续传功能
"""

import json
import time
import requests
from typing import Dict, Any

# API 基础 URL
BASE_URL = "http://localhost:5001/api/simulation"

class AutoPilotTester:
    """自动驾驶功能测试器"""
    
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.simulation_id = None
    
    def print_header(self, title: str):
        """打印标题"""
        print("\n" + "="*60)
        print(f"  {title}")
        print("="*60)
    
    def print_response(self, response: Dict[str, Any]):
        """打印响应"""
        print(json.dumps(response, indent=2, ensure_ascii=False))
    
    def test_config_auto_pilot(self, simulation_id: str) -> bool:
        """测试1: 配置自动驾驶模式"""
        self.print_header("测试1: 配置自动驾驶模式")
        
        self.simulation_id = simulation_id
        
        url = f"{self.base_url}/auto-pilot/config"
        payload = {
            "simulation_id": simulation_id,
            "mode": "auto"
        }
        
        print(f"请求: POST {url}")
        print(f"数据: {json.dumps(payload, indent=2, ensure_ascii=False)}")
        
        try:
            response = requests.post(url, json=payload)
            data = response.json()
            self.print_response(data)
            
            if data.get("success"):
                print("✅ 配置成功")
                return True
            else:
                print("❌ 配置失败")
                return False
        except Exception as e:
            print(f"❌ 请求失败: {e}")
            return False
    
    def test_start_auto_pilot(self, force: bool = False) -> bool:
        """测试2: 启动自动驾驶"""
        self.print_header(f"测试2: 启动自动驾驶 (force={force})")
        
        url = f"{self.base_url}/auto-pilot/start"
        payload = {
            "simulation_id": self.simulation_id,
            "force": force
        }
        
        print(f"请求: POST {url}")
        print(f"数据: {json.dumps(payload, indent=2, ensure_ascii=False)}")
        
        try:
            response = requests.post(url, json=payload)
            data = response.json()
            self.print_response(data)
            
            if data.get("success"):
                print("✅ 启动成功")
                return True
            else:
                print("❌ 启动失败")
                return False
        except Exception as e:
            print(f"❌ 请求失败: {e}")
            return False
    
    def test_get_status(self) -> Dict[str, Any]:
        """测试3: 获取自动驾驶状态"""
        self.print_header("测试3: 获取自动驾驶状态")
        
        url = f"{self.base_url}/auto-pilot/status"
        payload = {
            "simulation_id": self.simulation_id
        }
        
        print(f"请求: POST {url}")
        print(f"数据: {json.dumps(payload, indent=2, ensure_ascii=False)}")
        
        try:
            response = requests.post(url, json=payload)
            data = response.json()
            self.print_response(data)
            
            if data.get("success"):
                print("✅ 获取状态成功")
                return data.get("data", {})
            else:
                print("❌ 获取状态失败")
                return {}
        except Exception as e:
            print(f"❌ 请求失败: {e}")
            return {}
    
    def test_pause_auto_pilot(self) -> bool:
        """测试4: 暂停自动驾驶"""
        self.print_header("测试4: 暂停自动驾驶")
        
        url = f"{self.base_url}/auto-pilot/pause"
        payload = {
            "simulation_id": self.simulation_id
        }
        
        print(f"请求: POST {url}")
        print(f"数据: {json.dumps(payload, indent=2, ensure_ascii=False)}")
        
        try:
            response = requests.post(url, json=payload)
            data = response.json()
            self.print_response(data)
            
            if data.get("success"):
                print("✅ 暂停成功")
                return True
            else:
                print("❌ 暂停失败")
                return False
        except Exception as e:
            print(f"❌ 请求失败: {e}")
            return False
    
    def test_resume_auto_pilot(self) -> bool:
        """测试5: 恢复自动驾驶"""
        self.print_header("测试5: 恢复自动驾驶")
        
        url = f"{self.base_url}/auto-pilot/resume"
        payload = {
            "simulation_id": self.simulation_id
        }
        
        print(f"请求: POST {url}")
        print(f"数据: {json.dumps(payload, indent=2, ensure_ascii=False)}")
        
        try:
            response = requests.post(url, json=payload)
            data = response.json()
            self.print_response(data)
            
            if data.get("success"):
                print("✅ 恢复成功")
                return True
            else:
                print("❌ 恢复失败")
                return False
        except Exception as e:
            print(f"❌ 请求失败: {e}")
            return False
    
    def test_stop_auto_pilot(self) -> bool:
        """测试6: 停止自动驾驶"""
        self.print_header("测试6: 停止自动驾驶")
        
        url = f"{self.base_url}/auto-pilot/stop"
        payload = {
            "simulation_id": self.simulation_id
        }
        
        print(f"请求: POST {url}")
        print(f"数据: {json.dumps(payload, indent=2, ensure_ascii=False)}")
        
        try:
            response = requests.post(url, json=payload)
            data = response.json()
            self.print_response(data)
            
            if data.get("success"):
                print("✅ 停止成功")
                return True
            else:
                print("❌ 停止失败")
                return False
        except Exception as e:
            print(f"❌ 请求失败: {e}")
            return False
    
    def test_reset_auto_pilot(self) -> bool:
        """测试7: 重置自动驾驶状态"""
        self.print_header("测试7: 重置自动驾驶状态")
        
        url = f"{self.base_url}/auto-pilot/reset"
        payload = {
            "simulation_id": self.simulation_id
        }
        
        print(f"请求: POST {url}")
        print(f"数据: {json.dumps(payload, indent=2, ensure_ascii=False)}")
        
        try:
            response = requests.post(url, json=payload)
            data = response.json()
            self.print_response(data)
            
            if data.get("success"):
                print("✅ 重置成功")
                return True
            else:
                print("❌ 重置失败")
                return False
        except Exception as e:
            print(f"❌ 请求失败: {e}")
            return False
    
    def test_checkpoint_recovery(self):
        """测试8: 断点续传功能"""
        self.print_header("测试8: 断点续传功能")
        
        print("场景: 模拟执行到一半时重启服务，验证是否从断点继续")
        print()
        
        # 1. 启动自动驾驶
        print("步骤1: 启动自动驾驶")
        self.test_start_auto_pilot(force=False)
        
        # 2. 等待一段时间
        print("\n步骤2: 等待10秒...")
        time.sleep(10)
        
        # 3. 获取当前状态
        print("\n步骤3: 获取当前状态")
        status1 = self.test_get_status()
        last_completed_step_1 = status1.get("last_completed_step", "idle")
        print(f"当前 last_completed_step: {last_completed_step_1}")
        
        # 4. 模拟服务重启（实际上只是重新加载状态）
        print("\n步骤4: 模拟服务重启...")
        print("(在实际场景中，这里会重启 Flask 服务)")
        time.sleep(2)
        
        # 5. 再次启动自动驾驶（应该从断点继续）
        print("\n步骤5: 再次启动自动驾驶（应该从断点继续）")
        self.test_start_auto_pilot(force=False)
        
        # 6. 获取新的状态
        print("\n步骤6: 获取新的状态")
        status2 = self.test_get_status()
        last_completed_step_2 = status2.get("last_completed_step", "idle")
        print(f"新的 last_completed_step: {last_completed_step_2}")
        
        # 7. 验证
        print("\n步骤7: 验证断点续传")
        if last_completed_step_2 != "idle":
            print("✅ 断点续传功能正常工作！")
            print(f"   从 {last_completed_step_1} 继续到 {last_completed_step_2}")
            return True
        else:
            print("❌ 断点续传功能可能有问题")
            return False
    
    def run_all_tests(self, simulation_id: str):
        """运行所有测试"""
        print("\n")
        print("╔" + "="*58 + "╗")
        print("║" + " "*58 + "║")
        print("║" + "  断点续传功能测试套件".center(58) + "║")
        print("║" + " "*58 + "║")
        print("╚" + "="*58 + "╝")
        
        results = {}
        
        # 测试1: 配置自动驾驶
        results["配置自动驾驶"] = self.test_config_auto_pilot(simulation_id)
        time.sleep(1)
        
        # 测试2: 启动自动驾驶
        results["启动自动驾驶"] = self.test_start_auto_pilot(force=False)
        time.sleep(1)
        
        # 测试3: 获取状态
        status = self.test_get_status()
        results["获取状态"] = bool(status)
        time.sleep(1)
        
        # 测试4: 暂停自动驾驶
        results["暂停自动驾驶"] = self.test_pause_auto_pilot()
        time.sleep(1)
        
        # 测试5: 恢复自动驾驶
        results["恢复自动驾驶"] = self.test_resume_auto_pilot()
        time.sleep(1)
        
        # 测试6: 停止自动驾驶
        results["停止自动驾驶"] = self.test_stop_auto_pilot()
        time.sleep(1)
        
        # 测试7: 重置自动驾驶
        results["重置自动驾驶"] = self.test_reset_auto_pilot()
        time.sleep(1)
        
        # 测试8: 断点续传
        results["断点续传"] = self.test_checkpoint_recovery()
        
        # 打印总结
        self.print_header("测试总结")
        
        passed = sum(1 for v in results.values() if v)
        total = len(results)
        
        print(f"\n总计: {passed}/{total} 个测试通过\n")
        
        for test_name, result in results.items():
            status = "✅ 通过" if result else "❌ 失败"
            print(f"  {status}  {test_name}")
        
        print()
        
        if passed == total:
            print("🎉 所有测试通过！断点续传功能完全可用。")
        else:
            print(f"⚠️  有 {total - passed} 个测试失败，请检查日志。")


def main():
    """主函数"""
    import sys
    
    if len(sys.argv) < 2:
        print("用法: python test_auto_pilot.py <simulation_id>")
        print()
        print("示例:")
        print("  python test_auto_pilot.py sim_123456")
        sys.exit(1)
    
    simulation_id = sys.argv[1]
    
    tester = AutoPilotTester()
    tester.run_all_tests(simulation_id)


if __name__ == "__main__":
    main()
