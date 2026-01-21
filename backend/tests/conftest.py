"""
Pytest 配置文件
提供测试所需的 fixtures 和配置
"""

import sys
import os
import json
import pytest
from unittest.mock import MagicMock, patch

# 将 backend 目录添加到 sys.path，以便可以导入 app 模块
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


# ============== Flask 测试 Fixtures ==============

@pytest.fixture
def app():
    """
    创建测试用 Flask 应用实例

    配置测试环境，禁用 CSRF 保护，使用测试数据库
    通过 mock 配置来避免外部依赖初始化失败
    """
    # 设置测试环境变量
    os.environ['FLASK_ENV'] = 'testing'
    os.environ['TESTING'] = 'true'

    # 设置测试所需的配置（避免 LLM_API_KEY 缺失导致的初始化失败）
    os.environ['LLM_API_KEY'] = 'test_api_key_for_testing'
    os.environ['LLM_BASE_URL'] = 'https://api.test.com/v1'
    os.environ['LLM_MODEL_NAME'] = 'gpt-4o-mini'

    # 使用 patch 禁用限流和认证，避免初始化失败
    with patch('app.config_new.get_config') as mock_get_config:
        mock_config = MagicMock()
        mock_config.DEBUG = True
        mock_config.TESTING = True
        mock_config.LLM_API_KEY = 'test_api_key_for_testing'
        mock_config.LLM_BASE_URL = 'https://api.test.com/v1'
        mock_config.LLM_MODEL_NAME = 'gpt-4o-mini'
        mock_config.LLM_TEMPERATURE = 0.7
        mock_config.LLM_MAX_TOKENS = 2000
        mock_config.LLM_TIMEOUT = 300
        mock_config.SECRET_KEY = 'test-secret-key'
        mock_config.JSON_AS_ASCII = False
        mock_config.MAX_UPLOAD_SIZE = 50 * 1024 * 1024
        mock_config.UPLOAD_FOLDER = '/tmp/test_uploads'
        mock_config.ALLOWED_EXTENSIONS = {'pdf', 'md', 'txt', 'markdown'}
        mock_config.DEFAULT_CHUNK_SIZE = 500
        mock_config.DEFAULT_CHUNK_OVERLAP = 50
        mock_config.RATE_LIMIT_ENABLED = False  # 禁用限流
        mock_config.SECURITY_HEADERS_ENABLED = False  # 禁用安全头中间件
        mock_config.API_KEY_ENABLED = False  # 禁用 API Key 认证
        mock_config.SIGNATURE_ENABLED = False  # 禁用签名验证

        # Flask 配置
        mock_config.get_flask_config.return_value = {
            'SECRET_KEY': 'test-secret-key',
            'DEBUG': True,
            'JSON_AS_ASCII': False,
            'MAX_CONTENT_LENGTH': 50 * 1024 * 1024,
            'UPLOAD_FOLDER': '/tmp/test_uploads',
            'SESSION_COOKIE_SECURE': False,
            'SESSION_COOKIE_HTTPONLY': True,
            'SESSION_COOKIE_SAMESITE': 'Lax'
        }

        # CORS 配置
        mock_config.get_cors_config.return_value = {
            'origins': ['http://localhost:3000'],
            'allow_credentials': True,
            'max_age': 3600,
            'methods': ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
            'headers': ['Content-Type', 'Authorization', 'X-API-Key']
        }

        # 限流配置
        mock_config.get_rate_limit_config.return_value = {
            'enabled': False,
            'storage': 'memory',
            'redis_url': None,
            'strategy': 'moving-window',
            'default': '200/hour',
            'upload': '5/minute',
            'query': '100/minute',
            'llm': '10/hour',
            'simulation': '3/hour'
        }

        # 安全头配置
        mock_config.get_security_headers.return_value = {}

        # 配置验证
        mock_config.validate_required_fields.return_value = []

        mock_get_config.return_value = mock_config

        from app import create_app

        # 创建应用实例
        test_app = create_app()
        test_app.config.update({
            'TESTING': True,
            'WTF_CSRF_ENABLED': False,
        })

        yield test_app


@pytest.fixture
def client(app):
    """
    创建 Flask 测试客户端
    
    用于发送 HTTP 请求到测试应用
    """
    return app.test_client()


@pytest.fixture
def runner(app):
    """
    创建 Flask CLI 测试运行器
    
    用于测试 CLI 命令
    """
    return app.test_cli_runner()


# ============== Mock Fixtures ==============

@pytest.fixture
def mock_llm_client():
    """
    Mock LLM 客户端
    
    避免在测试中调用真实的 LLM API
    """
    with patch('app.utils.llm_client.LLMClient') as mock:
        mock_instance = MagicMock()
        mock_instance.chat.return_value = "Mock LLM response"
        mock_instance.chat_stream.return_value = iter(["Mock ", "stream ", "response"])
        mock.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def mock_zep_client():
    """
    Mock Zep 客户端
    
    避免在测试中调用真实的 Zep API
    """
    with patch('app.services.zep_tools.ZepToolsService') as mock:
        mock_instance = MagicMock()
        mock_instance.search_edges.return_value = []
        mock_instance.search_nodes.return_value = []
        mock_instance.get_node.return_value = None
        mock.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def mock_openai():
    """
    Mock OpenAI 客户端
    
    避免在测试中调用真实的 OpenAI API
    """
    with patch('openai.OpenAI') as mock:
        mock_instance = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="Mock response"))]
        mock_instance.chat.completions.create.return_value = mock_response
        mock.return_value = mock_instance
        yield mock_instance


# ============== 数据 Fixtures ==============

@pytest.fixture
def sample_project_data():
    """
    示例项目数据
    """
    return {
        "project_id": "proj_test_001",
        "project_name": "测试项目",
        "simulation_requirement": "测试模拟需求描述",
        "status": "created",
        "created_at": "2026-01-21T10:00:00",
        "updated_at": "2026-01-21T10:00:00"
    }


@pytest.fixture
def sample_simulation_data():
    """
    示例模拟数据
    """
    return {
        "simulation_id": "sim_test_001",
        "project_id": "proj_test_001",
        "graph_id": "multimo_test_001",
        "status": "created",
        "config": {
            "time_config": {
                "total_simulation_hours": 24,
                "minutes_per_round": 60
            },
            "platform_config": {
                "twitter": True,
                "reddit": True
            }
        },
        "created_at": "2026-01-21T10:00:00"
    }


@pytest.fixture
def sample_graph_data():
    """
    示例图谱数据
    """
    return {
        "graph_id": "multimo_test_001",
        "entities": [
            {"id": "e1", "name": "实体1", "type": "Person", "properties": {}},
            {"id": "e2", "name": "实体2", "type": "Organization", "properties": {}}
        ],
        "relationships": [
            {"source": "e1", "target": "e2", "type": "WORKS_FOR", "properties": {}}
        ],
        "metadata": {
            "created_at": "2026-01-21T10:00:00",
            "entity_count": 2,
            "relationship_count": 1
        }
    }


@pytest.fixture
def sample_report_data():
    """
    示例报告数据
    """
    return {
        "report_id": "report_test_001",
        "simulation_id": "sim_test_001",
        "title": "测试报告",
        "sections": [
            {"title": "概述", "content": "这是概述内容"},
            {"title": "分析", "content": "这是分析内容"}
        ],
        "status": "completed",
        "created_at": "2026-01-21T10:00:00"
    }


# ============== 文件系统 Fixtures ==============

@pytest.fixture
def temp_upload_dir(tmp_path):
    """
    创建临时上传目录
    """
    upload_dir = tmp_path / "uploads"
    upload_dir.mkdir()
    
    # 创建子目录
    (upload_dir / "projects").mkdir()
    (upload_dir / "simulations").mkdir()
    (upload_dir / "reports").mkdir()
    (upload_dir / "graphs").mkdir()
    
    return upload_dir


@pytest.fixture
def sample_pdf_file(tmp_path):
    """
    创建示例 PDF 文件（实际上是文本文件，用于测试）
    """
    pdf_path = tmp_path / "test.pdf"
    pdf_path.write_bytes(b"%PDF-1.4\nTest PDF content")
    return pdf_path


@pytest.fixture
def sample_markdown_file(tmp_path):
    """
    创建示例 Markdown 文件
    """
    md_path = tmp_path / "test.md"
    md_path.write_text("# Test\n\nThis is test content.", encoding='utf-8')
    return md_path


@pytest.fixture
def sample_txt_file(tmp_path):
    """
    创建示例文本文件
    """
    txt_path = tmp_path / "test.txt"
    txt_path.write_text("This is test content.", encoding='utf-8')
    return txt_path


# ============== 配置 Fixtures ==============

@pytest.fixture
def mock_config():
    """
    Mock 配置对象
    """
    with patch('app.config_new.get_config') as mock:
        mock_config = MagicMock()
        mock_config.DEBUG = True
        mock_config.TESTING = True
        mock_config.UPLOAD_FOLDER = "/tmp/test_uploads"
        mock_config.MAX_CONTENT_LENGTH = 50 * 1024 * 1024
        mock_config.ALLOWED_EXTENSIONS = {'pdf', 'md', 'txt'}
        mock_config.LLM_API_KEY = "test_api_key"
        mock_config.LLM_BASE_URL = "https://api.test.com"
        mock_config.LLM_MODEL = "gpt-4"
        mock_config.ZEP_API_KEY = "test_zep_key"
        mock.return_value = mock_config
        yield mock_config


# ============== 清理 Fixtures ==============

@pytest.fixture(autouse=True)
def cleanup_simulation_runner():
    """
    自动清理 SimulationRunner 的类级别状态
    """
    yield
    
    # 测试后清理
    try:
        from app.services.simulation_runner import SimulationRunner
        SimulationRunner._run_states = {}
        SimulationRunner._processes = {}
        SimulationRunner._action_queues = {}
        SimulationRunner._monitor_threads = {}
        SimulationRunner._stdout_files = {}
        SimulationRunner._stderr_files = {}
        SimulationRunner._graph_memory_enabled = {}
    except ImportError:
        pass


# ============== 辅助函数 ==============

def create_test_project(project_id: str, upload_dir: str) -> dict:
    """
    创建测试项目目录和配置文件
    
    Args:
        project_id: 项目ID
        upload_dir: 上传目录路径
        
    Returns:
        项目配置字典
    """
    project_dir = os.path.join(upload_dir, "projects", project_id)
    os.makedirs(project_dir, exist_ok=True)
    
    project_config = {
        "project_id": project_id,
        "project_name": f"Test Project {project_id}",
        "simulation_requirement": "Test requirement",
        "status": "created",
        "created_at": "2026-01-21T10:00:00"
    }
    
    config_path = os.path.join(project_dir, "project.json")
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(project_config, f, ensure_ascii=False)
    
    return project_config


def create_test_simulation(simulation_id: str, project_id: str, upload_dir: str) -> dict:
    """
    创建测试模拟目录和配置文件
    
    Args:
        simulation_id: 模拟ID
        project_id: 项目ID
        upload_dir: 上传目录路径
        
    Returns:
        模拟配置字典
    """
    sim_dir = os.path.join(upload_dir, "simulations", simulation_id)
    os.makedirs(sim_dir, exist_ok=True)
    
    sim_config = {
        "simulation_id": simulation_id,
        "project_id": project_id,
        "status": "created",
        "created_at": "2026-01-21T10:00:00"
    }
    
    config_path = os.path.join(sim_dir, "state.json")
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(sim_config, f, ensure_ascii=False)
    
    return sim_config
