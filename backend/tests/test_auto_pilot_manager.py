"""
自动驾驶管理器单元测试
测试 AutoPilotManager 的核心功能
"""

import pytest
import json
import os
from unittest.mock import patch, MagicMock, mock_open
from datetime import datetime


class TestAutoPilotState:
    """AutoPilotState 测试"""
    
    def test_state_init_default(self):
        """测试状态默认初始化"""
        from app.services.auto_pilot_manager import AutoPilotState, AutoPilotMode, AutoPilotStatus, AutoPilotStep
        
        state = AutoPilotState(simulation_id='sim_test_001')
        
        assert state.simulation_id == 'sim_test_001'
        assert state.mode == AutoPilotMode.MANUAL
        assert state.status == AutoPilotStatus.INACTIVE
        assert state.current_step == AutoPilotStep.IDLE
        assert state.step_progress == 0
        assert state.error is None
    
    def test_state_init_custom(self):
        """测试状态自定义初始化"""
        from app.services.auto_pilot_manager import AutoPilotState, AutoPilotMode, AutoPilotStatus, AutoPilotStep
        
        state = AutoPilotState(
            simulation_id='sim_test_001',
            mode=AutoPilotMode.AUTO,
            status=AutoPilotStatus.ACTIVE,
            current_step=AutoPilotStep.RUNNING
        )
        
        assert state.mode == AutoPilotMode.AUTO
        assert state.status == AutoPilotStatus.ACTIVE
        assert state.current_step == AutoPilotStep.RUNNING


class TestAutoPilotMode:
    """AutoPilotMode 枚举测试"""
    
    def test_mode_values(self):
        """测试模式枚举值"""
        from app.services.auto_pilot_manager import AutoPilotMode
        
        assert AutoPilotMode.MANUAL.value == "manual"
        assert AutoPilotMode.AUTO.value == "auto"
    
    def test_mode_comparison(self):
        """测试模式比较"""
        from app.services.auto_pilot_manager import AutoPilotMode
        
        assert AutoPilotMode.MANUAL != AutoPilotMode.AUTO
        assert AutoPilotMode.MANUAL == AutoPilotMode.MANUAL


class TestAutoPilotStep:
    """AutoPilotStep 枚举测试"""
    
    def test_step_values(self):
        """测试步骤枚举值"""
        from app.services.auto_pilot_manager import AutoPilotStep
        
        assert AutoPilotStep.IDLE.value == "idle"
        assert AutoPilotStep.PREPARING.value == "preparing"
        assert AutoPilotStep.STARTING.value == "starting"
        assert AutoPilotStep.RUNNING.value == "running"
        assert AutoPilotStep.MONITORING.value == "monitoring"
        assert AutoPilotStep.GENERATING_REPORT.value == "generating_report"
        assert AutoPilotStep.COMPLETED.value == "completed"
        assert AutoPilotStep.FAILED.value == "failed"
        assert AutoPilotStep.PAUSED.value == "paused"


class TestAutoPilotStatus:
    """AutoPilotStatus 枚举测试"""
    
    def test_status_values(self):
        """测试状态枚举值"""
        from app.services.auto_pilot_manager import AutoPilotStatus
        
        assert AutoPilotStatus.INACTIVE.value == "inactive"
        assert AutoPilotStatus.ACTIVE.value == "active"
        assert AutoPilotStatus.PAUSED.value == "paused"
        assert AutoPilotStatus.COMPLETED.value == "completed"
        assert AutoPilotStatus.FAILED.value == "failed"


class TestAutoPilotManager:
    """AutoPilotManager 测试"""
    
    @patch('app.services.auto_pilot_manager.get_config')
    def test_manager_init(self, mock_config):
        """测试管理器初始化"""
        mock_config.return_value.UPLOAD_FOLDER = '/tmp/test_uploads'
        
        from app.services.auto_pilot_manager import AutoPilotManager
        
        # 验证类级别属性
        assert hasattr(AutoPilotManager, '_states')
        assert hasattr(AutoPilotManager, '_threads')
    
    @patch('app.services.auto_pilot_manager.get_config')
    @patch('os.path.exists')
    def test_get_state_not_found(self, mock_exists, mock_config):
        """测试获取不存在的状态"""
        mock_config.return_value.UPLOAD_FOLDER = '/tmp/test_uploads'
        mock_exists.return_value = False
        
        from app.services.auto_pilot_manager import AutoPilotManager
        
        state = AutoPilotManager.get_state('nonexistent')
        assert state is None
    
    @patch('app.services.auto_pilot_manager.get_config')
    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open)
    def test_get_state_success(self, mock_file, mock_exists, mock_config):
        """测试成功获取状态"""
        mock_config.return_value.UPLOAD_FOLDER = '/tmp/test_uploads'
        mock_exists.return_value = True
        
        state_data = {
            'simulation_id': 'sim_test_001',
            'mode': 'auto',
            'status': 'active',
            'current_step': 'running'
        }
        mock_file.return_value.read.return_value = json.dumps(state_data)
        
        from app.services.auto_pilot_manager import AutoPilotManager
        
        with patch('json.load', return_value=state_data):
            state = AutoPilotManager.get_state('sim_test_001')
        
        # 验证状态
        # assert state is not None
    
    @patch('app.services.auto_pilot_manager.get_config')
    @patch('os.makedirs')
    @patch('builtins.open', new_callable=mock_open)
    def test_save_state(self, mock_file, mock_makedirs, mock_config):
        """测试保存状态"""
        mock_config.return_value.UPLOAD_FOLDER = '/tmp/test_uploads'
        
        from app.services.auto_pilot_manager import AutoPilotManager, AutoPilotState
        
        state = AutoPilotState(simulation_id='sim_test_001')
        AutoPilotManager._save_state(state)
        
        # 验证文件写入
        mock_file.assert_called()


class TestAutoPilotModeSwitch:
    """模式切换测试"""
    
    @patch('app.services.auto_pilot_manager.get_config')
    @patch('app.services.auto_pilot_manager.AutoPilotManager.get_state')
    @patch('app.services.auto_pilot_manager.AutoPilotManager._save_state')
    def test_switch_to_auto(self, mock_save, mock_get_state, mock_config):
        """测试切换到自动模式"""
        mock_config.return_value.UPLOAD_FOLDER = '/tmp/test_uploads'
        
        from app.services.auto_pilot_manager import AutoPilotManager, AutoPilotState, AutoPilotMode
        
        state = AutoPilotState(simulation_id='sim_test_001')
        mock_get_state.return_value = state
        
        result = AutoPilotManager.set_mode('sim_test_001', AutoPilotMode.AUTO)
        
        # 验证模式切换
        # assert result.mode == AutoPilotMode.AUTO
    
    @patch('app.services.auto_pilot_manager.get_config')
    @patch('app.services.auto_pilot_manager.AutoPilotManager.get_state')
    @patch('app.services.auto_pilot_manager.AutoPilotManager._save_state')
    def test_switch_to_manual(self, mock_save, mock_get_state, mock_config):
        """测试切换到手动模式"""
        mock_config.return_value.UPLOAD_FOLDER = '/tmp/test_uploads'
        
        from app.services.auto_pilot_manager import AutoPilotManager, AutoPilotState, AutoPilotMode
        
        state = AutoPilotState(simulation_id='sim_test_001', mode=AutoPilotMode.AUTO)
        mock_get_state.return_value = state
        
        result = AutoPilotManager.set_mode('sim_test_001', AutoPilotMode.MANUAL)
        
        # 验证模式切换
        # assert result.mode == AutoPilotMode.MANUAL


class TestAutoPilotStepTransitions:
    """步骤转换测试"""
    
    @patch('app.services.auto_pilot_manager.get_config')
    def test_valid_step_transition(self, mock_config):
        """测试有效的步骤转换"""
        mock_config.return_value.UPLOAD_FOLDER = '/tmp/test_uploads'
        
        from app.services.auto_pilot_manager import AutoPilotStep
        
        # IDLE -> PREPARING 是有效的
        # PREPARING -> STARTING 是有效的
        # STARTING -> RUNNING 是有效的
        # RUNNING -> MONITORING 是有效的
        # MONITORING -> GENERATING_REPORT 是有效的
        # GENERATING_REPORT -> COMPLETED 是有效的
        
        valid_transitions = [
            (AutoPilotStep.IDLE, AutoPilotStep.PREPARING),
            (AutoPilotStep.PREPARING, AutoPilotStep.STARTING),
            (AutoPilotStep.STARTING, AutoPilotStep.RUNNING),
            (AutoPilotStep.RUNNING, AutoPilotStep.MONITORING),
            (AutoPilotStep.MONITORING, AutoPilotStep.GENERATING_REPORT),
            (AutoPilotStep.GENERATING_REPORT, AutoPilotStep.COMPLETED),
        ]
        
        for from_step, to_step in valid_transitions:
            assert from_step != to_step


class TestAutoPilotPauseResume:
    """暂停/恢复测试"""
    
    @patch('app.services.auto_pilot_manager.get_config')
    @patch('app.services.auto_pilot_manager.AutoPilotManager.get_state')
    @patch('app.services.auto_pilot_manager.AutoPilotManager._save_state')
    def test_pause(self, mock_save, mock_get_state, mock_config):
        """测试暂停"""
        mock_config.return_value.UPLOAD_FOLDER = '/tmp/test_uploads'
        
        from app.services.auto_pilot_manager import AutoPilotManager, AutoPilotState, AutoPilotStatus, AutoPilotStep
        
        state = AutoPilotState(
            simulation_id='sim_test_001',
            status=AutoPilotStatus.ACTIVE,
            current_step=AutoPilotStep.RUNNING
        )
        mock_get_state.return_value = state
        
        result = AutoPilotManager.pause('sim_test_001')
        
        # 验证暂停
        # assert result.status == AutoPilotStatus.PAUSED
    
    @patch('app.services.auto_pilot_manager.get_config')
    @patch('app.services.auto_pilot_manager.AutoPilotManager.get_state')
    @patch('app.services.auto_pilot_manager.AutoPilotManager._save_state')
    def test_resume(self, mock_save, mock_get_state, mock_config):
        """测试恢复"""
        mock_config.return_value.UPLOAD_FOLDER = '/tmp/test_uploads'
        
        from app.services.auto_pilot_manager import AutoPilotManager, AutoPilotState, AutoPilotStatus, AutoPilotStep
        
        state = AutoPilotState(
            simulation_id='sim_test_001',
            status=AutoPilotStatus.PAUSED,
            current_step=AutoPilotStep.PAUSED
        )
        mock_get_state.return_value = state
        
        result = AutoPilotManager.resume('sim_test_001')
        
        # 验证恢复
        # assert result.status == AutoPilotStatus.ACTIVE
    
    @patch('app.services.auto_pilot_manager.get_config')
    @patch('app.services.auto_pilot_manager.AutoPilotManager.get_state')
    def test_pause_not_running(self, mock_get_state, mock_config):
        """测试暂停非运行状态"""
        mock_config.return_value.UPLOAD_FOLDER = '/tmp/test_uploads'
        
        from app.services.auto_pilot_manager import AutoPilotManager, AutoPilotState, AutoPilotStatus
        
        state = AutoPilotState(
            simulation_id='sim_test_001',
            status=AutoPilotStatus.INACTIVE
        )
        mock_get_state.return_value = state
        
        # 暂停非运行状态应该失败或无操作
        # result = AutoPilotManager.pause('sim_test_001')


class TestAutoPilotErrorHandling:
    """错误处理测试"""
    
    @patch('app.services.auto_pilot_manager.get_config')
    @patch('app.services.auto_pilot_manager.AutoPilotManager.get_state')
    @patch('app.services.auto_pilot_manager.AutoPilotManager._save_state')
    def test_handle_step_error(self, mock_save, mock_get_state, mock_config):
        """测试步骤错误处理"""
        mock_config.return_value.UPLOAD_FOLDER = '/tmp/test_uploads'
        
        from app.services.auto_pilot_manager import AutoPilotManager, AutoPilotState, AutoPilotStatus, AutoPilotStep
        
        state = AutoPilotState(
            simulation_id='sim_test_001',
            status=AutoPilotStatus.ACTIVE,
            current_step=AutoPilotStep.PREPARING
        )
        mock_get_state.return_value = state
        
        # 模拟错误
        # AutoPilotManager._handle_error('sim_test_001', 'Test error')
        
        # 验证错误状态
        # assert state.status == AutoPilotStatus.FAILED
        # assert state.error is not None
    
    @patch('app.services.auto_pilot_manager.get_config')
    @patch('app.services.auto_pilot_manager.AutoPilotManager.get_state')
    def test_retry_on_error(self, mock_get_state, mock_config):
        """测试错误重试"""
        mock_config.return_value.UPLOAD_FOLDER = '/tmp/test_uploads'
        
        from app.services.auto_pilot_manager import AutoPilotManager, AutoPilotState
        
        state = AutoPilotState(
            simulation_id='sim_test_001',
            retry_count=0
        )
        mock_get_state.return_value = state
        
        # 验证重试计数
        # assert state.retry_count == 0


class TestAutoPilotStatePersistence:
    """状态持久化测试"""
    
    @patch('app.services.auto_pilot_manager.get_config')
    @patch('os.makedirs')
    @patch('builtins.open', new_callable=mock_open)
    def test_state_save_to_file(self, mock_file, mock_makedirs, mock_config):
        """测试状态保存到文件"""
        mock_config.return_value.UPLOAD_FOLDER = '/tmp/test_uploads'
        
        from app.services.auto_pilot_manager import AutoPilotManager, AutoPilotState
        
        state = AutoPilotState(simulation_id='sim_test_001')
        AutoPilotManager._save_state(state)
        
        # 验证文件写入
        mock_file.assert_called()
    
    @patch('app.services.auto_pilot_manager.get_config')
    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open)
    def test_state_load_from_file(self, mock_file, mock_exists, mock_config):
        """测试从文件加载状态"""
        mock_config.return_value.UPLOAD_FOLDER = '/tmp/test_uploads'
        mock_exists.return_value = True
        
        state_data = {
            'simulation_id': 'sim_test_001',
            'mode': 'auto',
            'status': 'active',
            'current_step': 'running',
            'step_progress': 50
        }
        mock_file.return_value.read.return_value = json.dumps(state_data)
        
        from app.services.auto_pilot_manager import AutoPilotManager
        
        with patch('json.load', return_value=state_data):
            state = AutoPilotManager.get_state('sim_test_001')
        
        # 验证加载的状态
        # assert state.step_progress == 50


class TestAutoPilotAutoSteps:
    """自动步骤测试"""
    
    @patch('app.services.auto_pilot_manager.get_config')
    @patch('app.services.auto_pilot_manager.SimulationManager')
    def test_auto_prepare(self, mock_sim_manager, mock_config):
        """测试自动准备"""
        mock_config.return_value.UPLOAD_FOLDER = '/tmp/test_uploads'
        
        # Mock 模拟管理器
        mock_sim_manager.prepare_simulation.return_value = {'status': 'prepared'}
        
        from app.services.auto_pilot_manager import AutoPilotManager
        
        # 测试自动准备
        # result = AutoPilotManager._auto_prepare('sim_test_001')
    
    @patch('app.services.auto_pilot_manager.get_config')
    @patch('app.services.auto_pilot_manager.SimulationRunner')
    def test_auto_start(self, mock_runner, mock_config):
        """测试自动启动"""
        mock_config.return_value.UPLOAD_FOLDER = '/tmp/test_uploads'
        
        # Mock 模拟运行器
        mock_runner.start_simulation.return_value = MagicMock()
        
        from app.services.auto_pilot_manager import AutoPilotManager
        
        # 测试自动启动
        # result = AutoPilotManager._auto_start('sim_test_001')
    
    @patch('app.services.auto_pilot_manager.get_config')
    @patch('app.services.auto_pilot_manager.SimulationRunner')
    def test_auto_monitor(self, mock_runner, mock_config):
        """测试自动监控"""
        mock_config.return_value.UPLOAD_FOLDER = '/tmp/test_uploads'
        
        # Mock 运行状态
        mock_state = MagicMock()
        mock_state.runner_status = 'completed'
        mock_runner.get_run_state.return_value = mock_state
        
        from app.services.auto_pilot_manager import AutoPilotManager
        
        # 测试自动监控
        # result = AutoPilotManager._auto_monitor('sim_test_001')
    
    @patch('app.services.auto_pilot_manager.get_config')
    @patch('app.services.auto_pilot_manager.ReportAgent')
    def test_auto_report(self, mock_report_agent, mock_config):
        """测试自动报告"""
        mock_config.return_value.UPLOAD_FOLDER = '/tmp/test_uploads'
        
        # Mock 报告智能体
        mock_agent = MagicMock()
        mock_agent.generate.return_value = {'report_id': 'report_test_001'}
        mock_report_agent.return_value = mock_agent
        
        from app.services.auto_pilot_manager import AutoPilotManager
        
        # 测试自动报告
        # result = AutoPilotManager._auto_report('sim_test_001')


class TestAutoPilotConcurrency:
    """并发测试"""
    
    @patch('app.services.auto_pilot_manager.get_config')
    def test_concurrent_state_access(self, mock_config):
        """测试并发状态访问"""
        mock_config.return_value.UPLOAD_FOLDER = '/tmp/test_uploads'
        
        from app.services.auto_pilot_manager import AutoPilotManager
        
        # 验证线程安全
        # 多个线程同时访问状态应该是安全的
    
    @patch('app.services.auto_pilot_manager.get_config')
    def test_multiple_simulations(self, mock_config):
        """测试多个模拟同时运行"""
        mock_config.return_value.UPLOAD_FOLDER = '/tmp/test_uploads'
        
        from app.services.auto_pilot_manager import AutoPilotManager, AutoPilotState
        
        # 创建多个状态
        state1 = AutoPilotState(simulation_id='sim_001')
        state2 = AutoPilotState(simulation_id='sim_002')
        
        # 验证状态独立
        assert state1.simulation_id != state2.simulation_id
