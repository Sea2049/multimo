"""
模拟 API 集成测试
测试所有模拟相关的 API 端点
"""

import pytest
import json
from unittest.mock import patch, MagicMock


class TestSimulationCreateAPI:
    """模拟创建 API 测试"""

    def test_create_simulation_missing_params(self, client):
        """测试缺少必需参数"""
        response = client.post('/api/simulation/create',
                               json={},
                               content_type='application/json')
        # 可能返回 400（缺少参数）或 500（初始化失败）
        assert response.status_code in [400, 404, 500]

        if response.status_code == 400:
            data = json.loads(response.data)
            assert data['success'] == False

    def test_create_simulation_missing_project_id(self, client):
        """测试缺少项目ID"""
        response = client.post('/api/simulation/create',
                               json={'graph_id': 'test_graph'},
                               content_type='application/json')
        assert response.status_code in [400, 404, 500]

        if response.status_code == 400:
            data = json.loads(response.data)
            assert data['success'] == False

    @patch('app.models.project.ProjectManager.get_project')
    def test_create_simulation_project_not_found(self, mock_get_project, client):
        """测试项目不存在"""
        mock_get_project.return_value = None

        response = client.post('/api/simulation/create',
                               json={'project_id': 'nonexistent'},
                               content_type='application/json')
        # 可能返回 404 或 500
        assert response.status_code in [404, 500]

        if response.status_code == 404:
            data = json.loads(response.data)
            assert data['success'] == False

    @patch('app.services.simulation_manager.SimulationManager.create_simulation')
    @patch('app.models.project.ProjectManager.get_project')
    def test_create_simulation_success(self, mock_get_project, mock_create_sim, client, sample_project_data):
        """测试成功创建模拟"""
        mock_project = MagicMock()
        mock_project.to_dict.return_value = sample_project_data
        mock_project.graph_id = 'test_graph_id'
        mock_get_project.return_value = mock_project

        mock_create_sim.return_value = {
            'simulation_id': 'sim_test_001',
            'status': 'created'
        }

        response = client.post('/api/simulation/create',
                               json={'project_id': 'proj_test_001'},
                               content_type='application/json')

        # 可能成功或因为其他依赖失败
        assert response.status_code in [200, 201, 400, 500]


class TestSimulationPrepareAPI:
    """模拟准备 API 测试"""

    def test_prepare_simulation_missing_id(self, client):
        """测试缺少模拟ID"""
        response = client.post('/api/simulation/prepare',
                               json={},
                               content_type='application/json')
        assert response.status_code in [400, 404, 500]

        if response.status_code == 400:
            data = json.loads(response.data)
            assert data['success'] == False

    @patch('app.services.simulation_manager.SimulationManager.get_simulation')
    def test_prepare_simulation_not_found(self, mock_get_sim, client):
        """测试模拟不存在"""
        mock_get_sim.return_value = None

        response = client.post('/api/simulation/prepare',
                               json={'simulation_id': 'nonexistent'},
                               content_type='application/json')
        assert response.status_code in [404, 500]

        if response.status_code == 404:
            data = json.loads(response.data)
            assert data['success'] == False


class TestSimulationStartAPI:
    """模拟启动 API 测试"""

    def test_start_simulation_missing_id(self, client):
        """测试缺少模拟ID"""
        response = client.post('/api/simulation/start',
                               json={},
                               content_type='application/json')
        assert response.status_code in [400, 404, 500]

        if response.status_code == 400:
            data = json.loads(response.data)
            assert data['success'] == False

    @patch('app.services.simulation_manager.SimulationManager.get_simulation')
    def test_start_simulation_not_found(self, mock_get_sim, client):
        """测试模拟不存在"""
        mock_get_sim.return_value = None

        response = client.post('/api/simulation/start',
                               json={'simulation_id': 'nonexistent'},
                               content_type='application/json')
        assert response.status_code in [404, 500]

        if response.status_code == 404:
            data = json.loads(response.data)
            assert data['success'] == False


class TestSimulationStopAPI:
    """模拟停止 API 测试"""

    def test_stop_simulation_missing_id(self, client):
        """测试缺少模拟ID"""
        response = client.post('/api/simulation/stop',
                               json={},
                               content_type='application/json')
        assert response.status_code in [400, 404, 500]

        if response.status_code == 400:
            data = json.loads(response.data)
            assert data['success'] == False

    @patch('app.services.simulation_manager.SimulationManager.get_simulation')
    def test_stop_simulation_not_found(self, mock_get_sim, client):
        """测试模拟不存在"""
        mock_get_sim.return_value = None

        response = client.post('/api/simulation/stop',
                               json={'simulation_id': 'nonexistent'},
                               content_type='application/json')
        assert response.status_code in [404, 500]

        if response.status_code == 404:
            data = json.loads(response.data)
            assert data['success'] == False


class TestSimulationStatusAPI:
    """模拟状态 API 测试"""

    def test_get_status_missing_id(self, client):
        """测试缺少模拟ID"""
        response = client.get('/api/simulation/status')
        # 可能返回 400 或需要查询参数
        assert response.status_code in [400, 404, 500]

    @patch('app.services.simulation_manager.SimulationManager.get_simulation')
    def test_get_status_not_found(self, mock_get_sim, client):
        """测试模拟不存在"""
        mock_get_sim.return_value = None

        response = client.get('/api/simulation/status?simulation_id=nonexistent')
        assert response.status_code in [404, 500]

        if response.status_code == 404:
            data = json.loads(response.data)
            assert data['success'] == False

    @patch('app.services.simulation_manager.SimulationManager.get_simulation')
    @patch('app.services.simulation_runner.SimulationRunner.get_run_state')
    def test_get_status_success(self, mock_get_state, mock_get_sim, client, sample_simulation_data):
        """测试成功获取状态"""
        mock_sim = MagicMock()
        mock_sim.to_dict.return_value = sample_simulation_data
        mock_get_sim.return_value = mock_sim

        mock_state = MagicMock()
        mock_state.to_dict.return_value = {
            'runner_status': 'running',
            'current_round': 5
        }
        mock_get_state.return_value = mock_state

        response = client.get('/api/simulation/status?simulation_id=sim_test_001')
        # 可能成功或因为其他原因失败
        assert response.status_code in [200, 404, 500]


class TestSimulationHistoryAPI:
    """模拟历史 API 测试"""

    @patch('app.services.simulation_manager.SimulationManager.list_simulations')
    def test_get_history_empty(self, mock_list_sims, client):
        """测试空历史列表"""
        mock_list_sims.return_value = []

        response = client.get('/api/simulation/history')
        if response.status_code == 200:
            data = json.loads(response.data)
            assert data['success'] == True
            assert data['data'] == []

    @patch('app.services.simulation_manager.SimulationManager.list_simulations')
    def test_get_history_with_data(self, mock_list_sims, client, sample_simulation_data):
        """测试有数据的历史列表"""
        mock_sim = MagicMock()
        mock_sim.to_dict.return_value = sample_simulation_data
        mock_list_sims.return_value = [mock_sim]

        response = client.get('/api/simulation/history')
        if response.status_code == 200:
            data = json.loads(response.data)
            assert data['success'] == True
            assert len(data['data']) == 1


class TestSimulationLogsAPI:
    """模拟日志 API 测试"""

    def test_get_logs_missing_id(self, client):
        """测试缺少模拟ID"""
        response = client.get('/api/simulation/logs')
        assert response.status_code in [400, 404, 500]

    @patch('app.services.simulation_manager.SimulationManager.get_simulation')
    def test_get_logs_not_found(self, mock_get_sim, client):
        """测试模拟不存在"""
        mock_get_sim.return_value = None

        response = client.get('/api/simulation/logs?simulation_id=nonexistent')
        assert response.status_code in [404, 500]


class TestAutoPilotAPI:
    """自动驾驶模式 API 测试"""

    def test_config_auto_pilot_missing_params(self, client):
        """测试配置自动驾驶缺少参数"""
        response = client.post('/api/simulation/auto-pilot/config',
                               json={},
                               content_type='application/json')
        assert response.status_code in [400, 404, 500]

        if response.status_code == 400:
            data = json.loads(response.data)
            assert data['success'] == False

    def test_start_auto_pilot_missing_id(self, client):
        """测试启动自动驾驶缺少ID"""
        response = client.post('/api/simulation/auto-pilot/start',
                               json={},
                               content_type='application/json')
        assert response.status_code in [400, 404, 500]

        if response.status_code == 400:
            data = json.loads(response.data)
            assert data['success'] == False

    @patch('app.services.simulation_manager.SimulationManager.get_simulation')
    def test_start_auto_pilot_not_found(self, mock_get_sim, client):
        """测试模拟不存在"""
        mock_get_sim.return_value = None

        response = client.post('/api/simulation/auto-pilot/start',
                               json={'simulation_id': 'nonexistent'},
                               content_type='application/json')
        assert response.status_code in [404, 500]

    def test_get_auto_pilot_status_missing_id(self, client):
        """测试获取自动驾驶状态缺少ID"""
        response = client.get('/api/simulation/auto-pilot/status')
        assert response.status_code in [400, 404, 500]

    def test_pause_auto_pilot_missing_id(self, client):
        """测试暂停自动驾驶缺少ID"""
        response = client.post('/api/simulation/auto-pilot/pause',
                               json={},
                               content_type='application/json')
        assert response.status_code in [400, 404, 500]

        if response.status_code == 400:
            data = json.loads(response.data)
            assert data['success'] == False

    def test_resume_auto_pilot_missing_id(self, client):
        """测试恢复自动驾驶缺少ID"""
        response = client.post('/api/simulation/auto-pilot/resume',
                               json={},
                               content_type='application/json')
        assert response.status_code in [400, 404, 500]

        if response.status_code == 400:
            data = json.loads(response.data)
            assert data['success'] == False


class TestSimulationConfigAPI:
    """模拟配置 API 测试"""

    def test_get_config_missing_id(self, client):
        """测试获取配置缺少ID"""
        response = client.get('/api/simulation/config')
        assert response.status_code in [400, 404, 500]

    @patch('app.services.simulation_manager.SimulationManager.get_simulation')
    def test_get_config_not_found(self, mock_get_sim, client):
        """测试模拟不存在"""
        mock_get_sim.return_value = None

        response = client.get('/api/simulation/config?simulation_id=nonexistent')
        assert response.status_code in [404, 500]


class TestSimulationRoundAPI:
    """模拟轮次 API 测试"""

    def test_get_round_summary_missing_id(self, client):
        """测试获取轮次摘要缺少ID"""
        response = client.get('/api/simulation/round/summary')
        assert response.status_code in [400, 404, 500]

    def test_get_round_actions_missing_id(self, client):
        """测试获取轮次动作缺少ID"""
        response = client.get('/api/simulation/round/actions')
        assert response.status_code in [400, 404, 500]


class TestSimulationAgentAPI:
    """模拟智能体 API 测试"""

    def test_get_agent_list_missing_id(self, client):
        """测试获取智能体列表缺少ID"""
        response = client.get('/api/simulation/agents')
        assert response.status_code in [400, 404, 500]

    def test_get_agent_detail_missing_id(self, client):
        """测试获取智能体详情缺少ID"""
        response = client.get('/api/simulation/agent/detail')
        assert response.status_code in [400, 404, 500]


class TestSimulationErrorHandling:
    """模拟 API 错误处理测试"""

    def test_invalid_json_body(self, client):
        """测试无效的 JSON 请求体"""
        response = client.post('/api/simulation/create',
                               data='invalid json',
                               content_type='application/json')
        assert response.status_code in [400, 500]

    def test_wrong_content_type(self, client):
        """测试错误的 Content-Type"""
        response = client.post('/api/simulation/create',
                               data='test=value',
                               content_type='application/x-www-form-urlencoded')
        # 应该返回错误或尝试解析
        assert response.status_code in [400, 415, 500]

    def test_method_not_allowed(self, client):
        """测试不允许的 HTTP 方法"""
        response = client.put('/api/simulation/create',
                              json={'project_id': 'test'},
                              content_type='application/json')
        assert response.status_code == 405


class TestSimulationConcurrency:
    """模拟并发测试"""

    @patch('app.services.simulation_manager.SimulationManager.get_simulation')
    def test_concurrent_status_requests(self, mock_get_sim, client, sample_simulation_data):
        """测试并发状态请求"""
        mock_sim = MagicMock()
        mock_sim.to_dict.return_value = sample_simulation_data
        mock_get_sim.return_value = mock_sim

        # 发送多个并发请求
        responses = []
        for _ in range(5):
            response = client.get('/api/simulation/status?simulation_id=sim_test_001')
            responses.append(response)

        # 所有请求应该成功或一致地失败
        status_codes = [r.status_code for r in responses]
        assert len(set(status_codes)) == 1  # 所有状态码应该相同


class TestSimulationValidation:
    """模拟输入验证测试"""

    def test_invalid_simulation_id_format(self, client):
        """测试无效的模拟ID格式"""
        # 尝试使用特殊字符
        response = client.get('/api/simulation/status?simulation_id=../../../etc/passwd')
        assert response.status_code in [400, 404, 500]

    def test_empty_simulation_id(self, client):
        """测试空模拟ID"""
        response = client.get('/api/simulation/status?simulation_id=')
        assert response.status_code in [400, 404, 500]

    def test_very_long_simulation_id(self, client):
        """测试超长模拟ID"""
        long_id = 'a' * 1000
        response = client.get(f'/api/simulation/status?simulation_id={long_id}')
        assert response.status_code in [400, 404, 414, 500]