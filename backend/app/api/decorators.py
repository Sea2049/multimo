"""
API 请求验证装饰器模块

提供统一的请求验证、参数清理和错误处理装饰器，
减少各个路由文件中重复的验证代码。

使用示例:
    @validate_request(
        required=['simulation_id'],
        validators={'simulation_id': validate_graph_id},
        sanitizers={'simulation_id': lambda x: sanitize_string(x, max_length=100)}
    )
    def get_simulation(simulation_id: str):
        # simulation_id 已经过验证和清理
        pass
"""

from functools import wraps
from typing import Dict, List, Callable, Any, Optional
from flask import request, jsonify

from . import get_error_response, ErrorCode
from ..utils.validators import (
    ValidationResult,
    validate_graph_id,
    validate_no_sql_injection,
    sanitize_string,
    sanitize_dict
)
from ..utils.logger import get_logger

logger = get_logger(__name__)


def validate_request(
    required: List[str] = None,
    validators: Dict[str, Callable] = None,
    sanitizers: Dict[str, Callable] = None,
    check_sql_injection: bool = True
):
    """
    请求验证装饰器
    
    统一处理请求参数的验证、清理和错误响应，减少重复代码。
    
    Args:
        required: 必填字段列表（从 URL 参数或 JSON body 中获取）
        validators: 字段验证函数映射 {field_name: validator_function}
                   验证函数应返回 ValidationResult
        sanitizers: 字段清理函数映射 {field_name: sanitizer_function}
                   清理函数应返回清理后的值
        check_sql_injection: 是否检查 SQL 注入（默认 True）
    
    Returns:
        装饰器函数
    
    Example:
        @simulation_bp.route('/<simulation_id>/status')
        @validate_request(
            required=['simulation_id'],
            validators={'simulation_id': validate_graph_id}
        )
        def get_status(simulation_id: str):
            # simulation_id 已验证
            pass
    """
    required = required or []
    validators = validators or {}
    sanitizers = sanitizers or {}
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            errors = []
            
            # 收集所有参数（URL 参数 + JSON body）
            params = dict(kwargs)
            
            # 如果是 POST/PUT 请求，合并 JSON body
            if request.method in ['POST', 'PUT', 'PATCH']:
                try:
                    json_data = request.get_json(silent=True) or {}
                    if isinstance(json_data, dict):
                        params.update(json_data)
                except Exception:
                    pass
            
            # 1. 检查必填字段
            for field in required:
                value = params.get(field) or kwargs.get(field)
                if value is None or value == '':
                    errors.append(f"{field} 是必填字段")
            
            if errors:
                return jsonify(get_error_response(
                    error="; ".join(errors),
                    status_code=400,
                    error_code=ErrorCode.INVALID_INPUT
                )), 400
            
            # 2. 执行字段验证
            for field, validator in validators.items():
                value = params.get(field) or kwargs.get(field)
                if value is not None:
                    try:
                        result = validator(value, field)
                        if isinstance(result, ValidationResult) and not result.is_valid:
                            errors.extend(result.get_error_messages())
                    except Exception as e:
                        logger.warning(f"验证字段 {field} 时出错: {e}")
                        errors.append(f"{field} 验证失败")
            
            if errors:
                return jsonify(get_error_response(
                    error="; ".join(errors),
                    status_code=400,
                    error_code=ErrorCode.VALIDATION_ERROR
                )), 400
            
            # 3. 检查 SQL 注入
            if check_sql_injection:
                # 检查 JSON body
                if request.method in ['POST', 'PUT', 'PATCH']:
                    json_data = request.get_json(silent=True)
                    if json_data:
                        sql_result = validate_no_sql_injection(json_data, "request_data")
                        if not sql_result.is_valid:
                            return jsonify(get_error_response(
                                error="请求包含非法字符",
                                status_code=400,
                                error_code=ErrorCode.VALIDATION_ERROR
                            )), 400
            
            # 4. 清理字段值并更新 kwargs
            for field, sanitizer in sanitizers.items():
                if field in kwargs:
                    try:
                        kwargs[field] = sanitizer(kwargs[field])
                    except Exception as e:
                        logger.warning(f"清理字段 {field} 时出错: {e}")
            
            return func(*args, **kwargs)
        
        return wrapper
    return decorator


def validate_json_body(
    required: List[str] = None,
    schema: Dict[str, Dict] = None,
    check_sql_injection: bool = True
):
    """
    JSON Body 验证装饰器
    
    专门用于验证 POST/PUT 请求的 JSON body。
    
    Args:
        required: 必填字段列表
        schema: 字段验证 schema
        check_sql_injection: 是否检查 SQL 注入
    
    Returns:
        装饰器函数
    
    Example:
        @simulation_bp.route('/create', methods=['POST'])
        @validate_json_body(required=['name', 'graph_id'])
        def create_simulation():
            data = request.get_json()
            # data 已验证
            pass
    """
    required = required or []
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 获取 JSON body
            data = request.get_json(silent=True)
            
            if data is None:
                return jsonify(get_error_response(
                    error="请求体不能为空或必须是有效的 JSON",
                    status_code=400,
                    error_code=ErrorCode.INVALID_INPUT
                )), 400
            
            if not isinstance(data, dict):
                return jsonify(get_error_response(
                    error="请求体必须是 JSON 对象",
                    status_code=400,
                    error_code=ErrorCode.INVALID_INPUT
                )), 400
            
            # 检查必填字段
            missing = [f for f in required if f not in data or data[f] is None or data[f] == '']
            if missing:
                return jsonify(get_error_response(
                    error=f"缺少必填字段: {', '.join(missing)}",
                    status_code=400,
                    error_code=ErrorCode.INVALID_INPUT
                )), 400
            
            # 检查 SQL 注入
            if check_sql_injection:
                sql_result = validate_no_sql_injection(data, "request_data")
                if not sql_result.is_valid:
                    return jsonify(get_error_response(
                        error="请求包含非法字符",
                        status_code=400,
                        error_code=ErrorCode.VALIDATION_ERROR
                    )), 400
            
            return func(*args, **kwargs)
        
        return wrapper
    return decorator


def validate_path_param(
    param_name: str,
    validator: Callable = None,
    sanitizer: Callable = None,
    error_message: str = None
):
    """
    路径参数验证装饰器
    
    用于验证单个 URL 路径参数。
    
    Args:
        param_name: 参数名称
        validator: 验证函数，返回 ValidationResult
        sanitizer: 清理函数，返回清理后的值
        error_message: 自定义错误消息
    
    Returns:
        装饰器函数
    
    Example:
        @simulation_bp.route('/<simulation_id>')
        @validate_path_param('simulation_id', validator=validate_graph_id)
        def get_simulation(simulation_id: str):
            pass
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            value = kwargs.get(param_name)
            
            # 检查是否存在
            if value is None or value == '':
                msg = error_message or f"{param_name} 是必填参数"
                return jsonify(get_error_response(
                    error=msg,
                    status_code=400,
                    error_code=ErrorCode.INVALID_INPUT
                )), 400
            
            # 验证
            if validator:
                try:
                    result = validator(value, param_name)
                    if isinstance(result, ValidationResult) and not result.is_valid:
                        msg = error_message or result.get_error_messages()[0]
                        return jsonify(get_error_response(
                            error=msg,
                            status_code=400,
                            error_code=ErrorCode.VALIDATION_ERROR
                        )), 400
                except Exception as e:
                    logger.warning(f"验证参数 {param_name} 时出错: {e}")
            
            # 清理
            if sanitizer:
                try:
                    kwargs[param_name] = sanitizer(value)
                except Exception as e:
                    logger.warning(f"清理参数 {param_name} 时出错: {e}")
            
            return func(*args, **kwargs)
        
        return wrapper
    return decorator


def require_resource(
    resource_getter: Callable,
    resource_name: str = "资源",
    id_param: str = None
):
    """
    资源存在性验证装饰器
    
    验证请求的资源是否存在，不存在则返回 404。
    
    Args:
        resource_getter: 获取资源的函数，接受 ID 参数，返回资源或 None
        resource_name: 资源名称（用于错误消息）
        id_param: ID 参数名（从 kwargs 获取）
    
    Returns:
        装饰器函数
    
    Example:
        @simulation_bp.route('/<simulation_id>')
        @require_resource(
            resource_getter=lambda id: SimulationManager().get_simulation(id),
            resource_name="模拟",
            id_param="simulation_id"
        )
        def get_simulation(simulation_id: str):
            # 资源一定存在
            pass
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 获取资源 ID
            resource_id = kwargs.get(id_param) if id_param else None
            
            if resource_id is None and args:
                resource_id = args[0]
            
            if resource_id is None:
                return jsonify(get_error_response(
                    error=f"请提供{resource_name} ID",
                    status_code=400,
                    error_code=ErrorCode.INVALID_INPUT
                )), 400
            
            # 获取资源
            try:
                resource = resource_getter(resource_id)
                if resource is None:
                    return jsonify(get_error_response(
                        error=f"{resource_name}不存在: {resource_id}",
                        status_code=404,
                        error_code=ErrorCode.RESOURCE_NOT_FOUND
                    )), 404
            except Exception as e:
                logger.error(f"获取{resource_name}时出错: {e}")
                return jsonify(get_error_response(
                    error=f"获取{resource_name}失败",
                    status_code=500,
                    error_code=ErrorCode.INTERNAL_ERROR
                )), 500
            
            return func(*args, **kwargs)
        
        return wrapper
    return decorator


# ============== 常用验证器快捷方式 ==============

def validate_simulation_id(func: Callable) -> Callable:
    """
    模拟 ID 验证装饰器（快捷方式）
    
    等同于:
        @validate_path_param('simulation_id', validator=validate_graph_id,
                            sanitizer=lambda x: sanitize_string(x, max_length=100))
    """
    return validate_path_param(
        'simulation_id',
        validator=validate_graph_id,
        sanitizer=lambda x: sanitize_string(x, max_length=100)
    )(func)


def validate_graph_id_param(func: Callable) -> Callable:
    """
    图谱 ID 验证装饰器（快捷方式）
    """
    return validate_path_param(
        'graph_id',
        validator=validate_graph_id,
        sanitizer=lambda x: sanitize_string(x, max_length=100)
    )(func)


def validate_project_id(func: Callable) -> Callable:
    """
    项目 ID 验证装饰器（快捷方式）
    """
    return validate_path_param(
        'project_id',
        validator=validate_graph_id,
        sanitizer=lambda x: sanitize_string(x, max_length=100)
    )(func)


def validate_report_id(func: Callable) -> Callable:
    """
    报告 ID 验证装饰器（快捷方式）
    """
    return validate_path_param(
        'report_id',
        validator=validate_graph_id,
        sanitizer=lambda x: sanitize_string(x, max_length=100)
    )(func)
