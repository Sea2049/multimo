# API 集成测试脚本
# 测试所有核心 API 端点的功能和错误处理

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:5001/api/v1"

class APITester:
    def __init__(self):
        self.results = {
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "errors": [],
            "test_details": []
        }
    
    def test_endpoint(self, name, method, endpoint, data=None, expected_status=200, check_response=None):
        """测试单个 API 端点"""
        self.results["total_tests"] += 1
        url = f"{BASE_URL}{endpoint}"
        
        try:
            start_time = time.time()
            
            if method == "GET":
                response = requests.get(url, timeout=30)
            elif method == "POST":
                response = requests.post(url, json=data, timeout=30)
            else:
                raise ValueError(f"不支持的方法: {method}")
            
            # 打印调试信息
            print(f"  状态码: {response.status_code}")
            
            elapsed_time = time.time() - start_time
            
            # 检查状态码
            status_ok = response.status_code == expected_status
            
            # 检查响应内容
            response_ok = True
            if check_response and status_ok:
                try:
                    response_data = response.json()
                    response_ok = check_response(response_data)
                except Exception as e:
                    response_ok = False
                    self.results["errors"].append(f"{name}: 响应检查失败 - {str(e)}")
            
            # 记录结果
            test_passed = status_ok and response_ok
            if test_passed:
                self.results["passed"] += 1
            else:
                self.results["failed"] += 1
                if not status_ok:
                    self.results["errors"].append(
                        f"{name}: 期望状态码 {expected_status}, 实际 {response.status_code}"
                    )
            
            self.results["test_details"].append({
                "name": name,
                "method": method,
                "endpoint": endpoint,
                "status_code": response.status_code,
                "expected_status": expected_status,
                "response_time": f"{elapsed_time:.3f}s",
                "passed": test_passed
            })
            
            return test_passed
            
        except Exception as e:
            self.results["failed"] += 1
            self.results["errors"].append(f"{name}: {str(e)}")
            self.results["test_details"].append({
                "name": name,
                "method": method,
                "endpoint": endpoint,
                "error": str(e),
                "passed": False
            })
            return False
    
    def run_tests(self):
        """运行所有 API 测试"""
        print("=" * 60)
        print("开始 API 集成测试")
        print("=" * 60)
        print()
        
        # 1. 健康检查 API
        print("测试健康检查 API...")
        self.test_endpoint(
            "健康检查",
            "GET",
            "/health",
            expected_status=200,
            check_response=lambda r: r.get("success") == True
        )
        
        # 2. 图谱 API - 获取实体列表 (可能为空)
        print("测试图谱 API - 获取实体列表...")
        self.test_endpoint(
            "获取实体列表",
            "GET",
            "/graph/entities",
            expected_status=200
        )
        
        # 3. 图谱 API - 获取关系列表 (可能为空)
        print("测试图谱 API - 获取关系列表...")
        self.test_endpoint(
            "获取关系列表",
            "GET",
            "/graph/relationships",
            expected_status=200
        )
        
        # 4. 模拟 API - 获取历史模拟 (可能为空)
        print("测试模拟 API - 获取历史模拟...")
        self.test_endpoint(
            "获取历史模拟",
            "GET",
            "/simulation/history",
            expected_status=200
        )
        
        # 5. 报告 API - 列出所有报告 (可能为空)
        print("测试报告 API - 列出所有报告...")
        self.test_endpoint(
            "列出所有报告",
            "GET",
            "/report/list",
            expected_status=200
        )
        
        # 6. 错误处理测试 - 无效的图谱 ID
        print("测试错误处理 - 无效的图谱 ID...")
        self.test_endpoint(
            "获取不存在的图谱",
            "GET",
            "/graph/nonexistent-graph-id",
            expected_status=404
        )
        
        # 7. 错误处理测试 - 无效的模拟 ID
        print("测试错误处理 - 无效的模拟 ID...")
        self.test_endpoint(
            "获取不存在的模拟",
            "GET",
            "/simulation/nonexistent-sim-id",
            expected_status=404
        )
        
        # 8. 错误处理测试 - 缺失参数
        print("测试错误处理 - 缺失参数...")
        self.test_endpoint(
            "创建模拟缺失参数",
            "POST",
            "/simulation/create",
            data={},  # 缺失必需参数
            expected_status=400
        )
        
        print()
        print("=" * 60)
        print("API 集成测试完成")
        print("=" * 60)
        self.print_summary()
    
    def print_summary(self):
        """打印测试摘要"""
        print()
        print(f"总测试数: {self.results['total_tests']}")
        print(f"通过: {self.results['passed']}")
        print(f"失败: {self.results['failed']}")
        print(f"通过率: {self.results['passed'] / self.results['total_tests'] * 100:.1f}%")
        
        if self.results['errors']:
            print()
            print("错误详情:")
            for error in self.results['errors']:
                print(f"  - {error}")
        
        print()
        print("测试详情:")
        for detail in self.results['test_details']:
            status = "✓" if detail['passed'] else "✗"
            print(f"  {status} {detail['name']}")
            if 'response_time' in detail:
                print(f"    响应时间: {detail['response_time']}")
            if 'error' in detail:
                print(f"    错误: {detail['error']}")
    
    def save_results(self, filename="api_test_results.json"):
        """保存测试结果到文件"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)
        print(f"\n测试结果已保存到: {filename}")


if __name__ == "__main__":
    tester = APITester()
    tester.run_tests()
    tester.save_results()
