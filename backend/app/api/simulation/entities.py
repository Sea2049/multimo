"""
实体相关 API 路由模块

提供图谱实体的读取、查询和过滤功能。

路由:
    GET /entities/<graph_id>                    - 获取图谱中的所有实体
    GET /entities/<graph_id>/<entity_uuid>      - 获取单个实体详情
    GET /entities/<graph_id>/by-type/<type>     - 获取指定类型的所有实体
"""

from flask import request, jsonify

from .. import simulation_bp, get_error_response, make_error_response, ErrorCode
from ...config_new import get_config
from ...services.zep_entity_reader import ZepEntityReader
from ...utils.logger import get_logger

logger = get_logger('multimo.api.simulation.entities')


@simulation_bp.route('/entities/<graph_id>', methods=['GET'])
def get_graph_entities(graph_id: str):
    """
    获取图谱中的所有实体（已过滤）
    
    只返回符合预定义实体类型的节点（Labels不只是Entity的节点）
    
    Args:
        graph_id: 图谱ID
    
    Query参数:
        entity_types: 逗号分隔的实体类型列表（可选，用于进一步过滤）
        enrich: 是否获取相关边信息（默认true）
    
    Returns:
        实体列表及相关统计信息
    """
    try:
        config = get_config()
        if not config.LLM_API_KEY:
            return jsonify(get_error_response(
                error="LLM_API_KEY未配置",
                status_code=500,
                error_code=ErrorCode.CONFIGURATION_ERROR,
                recovery_suggestion="请联系管理员配置 LLM_API_KEY 环境变量"
            )), 500
        
        # 解析查询参数
        entity_types_str = request.args.get('entity_types', '')
        entity_types = [t.strip() for t in entity_types_str.split(',') if t.strip()] if entity_types_str else None
        enrich = request.args.get('enrich', 'true').lower() == 'true'
        
        logger.info(f"获取图谱实体: graph_id={graph_id}, entity_types={entity_types}, enrich={enrich}")
        
        # 调用服务获取实体
        reader = ZepEntityReader()
        result = reader.filter_defined_entities(
            graph_id=graph_id,
            defined_entity_types=entity_types,
            enrich_with_edges=enrich
        )
        
        return jsonify({
            "success": True,
            "data": result.to_dict()
        })
        
    except Exception as e:
        logger.error(f"获取图谱实体失败: {str(e)}")
        return jsonify(make_error_response(e, 500, ErrorCode.INTERNAL_ERROR)), 500


@simulation_bp.route('/entities/<graph_id>/<entity_uuid>', methods=['GET'])
def get_entity_detail(graph_id: str, entity_uuid: str):
    """
    获取单个实体的详细信息
    
    Args:
        graph_id: 图谱ID
        entity_uuid: 实体UUID
    
    Returns:
        实体详细信息，包含上下文关系
    """
    try:
        config = get_config()
        if not config.LLM_API_KEY:
            return jsonify({
                "success": False,
                "error": "LLM_API_KEY未配置"
            }), 500
        
        reader = ZepEntityReader()
        entity = reader.get_entity_with_context(graph_id, entity_uuid)
        
        if not entity:
            return jsonify({
                "success": False,
                "error": f"实体不存在: {entity_uuid}"
            }), 404
        
        return jsonify({
            "success": True,
            "data": entity.to_dict()
        })
        
    except Exception as e:
        logger.error(f"获取实体详情失败: {str(e)}")
        return jsonify(make_error_response(e, 500, ErrorCode.INTERNAL_ERROR)), 500


@simulation_bp.route('/entities/<graph_id>/by-type/<entity_type>', methods=['GET'])
def get_entities_by_type(graph_id: str, entity_type: str):
    """
    获取指定类型的所有实体
    
    Args:
        graph_id: 图谱ID
        entity_type: 实体类型
    
    Query参数:
        enrich: 是否获取相关边信息（默认true）
    
    Returns:
        指定类型的实体列表
    """
    try:
        config = get_config()
        if not config.LLM_API_KEY:
            return jsonify({
                "success": False,
                "error": "LLM_API_KEY未配置"
            }), 500
        
        enrich = request.args.get('enrich', 'true').lower() == 'true'
        
        reader = ZepEntityReader()
        entities = reader.get_entities_by_type(
            graph_id=graph_id,
            entity_type=entity_type,
            enrich_with_edges=enrich
        )
        
        return jsonify({
            "success": True,
            "data": {
                "entity_type": entity_type,
                "count": len(entities),
                "entities": [e.to_dict() for e in entities]
            }
        })
        
    except Exception as e:
        logger.error(f"获取实体失败: {str(e)}")
        return jsonify(make_error_response(e, 500, ErrorCode.INTERNAL_ERROR)), 500
