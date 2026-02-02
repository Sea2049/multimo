"""
邀请码管理 API

提供邀请码的创建、查看、更新、删除等管理功能。
所有接口都需要管理员权限。
"""

import secrets
import string
from datetime import datetime
from flask import request, jsonify, g

from app.api import api_v1_bp, get_response, get_error_response, ErrorCode
from app.api.decorators import require_admin, validate_json_body
from app.config_new import get_config
from app.storage.database import SQLiteStorage
from app.utils.logger import get_logger

logger = get_logger(__name__)


def _generate_invitation_code(length: int = 8) -> str:
    """生成随机邀请码
    
    Args:
        length: 邀请码长度，默认 8 位
        
    Returns:
        8 位大写字母数字组合的邀请码
    """
    # 使用大写字母和数字，排除容易混淆的字符（0, O, I, 1）
    alphabet = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def _get_storage() -> SQLiteStorage:
    """获取数据库存储实例"""
    config = get_config()
    return SQLiteStorage(config.TASKS_DATABASE_PATH)


@api_v1_bp.route("/invitations", methods=["GET"])
@require_admin
def list_invitations():
    """列出所有邀请码
    
    Query Parameters:
        include_inactive: 是否包含已禁用的邀请码（默认 true）
        limit: 返回数量限制（默认 100）
    
    Response:
        {
            "success": true,
            "data": {
                "invitations": [...]
            }
        }
    """
    try:
        include_inactive = request.args.get("include_inactive", "true").lower() == "true"
        limit = min(int(request.args.get("limit", 100)), 500)
        
        storage = _get_storage()
        invitations = storage.list_invitation_codes(
            include_inactive=include_inactive,
            limit=limit
        )
        
        # 格式化返回数据
        result = []
        for inv in invitations:
            result.append({
                "id": inv["id"],
                "code": inv["code"],
                "created_by": inv["created_by"],
                "max_uses": inv["max_uses"],
                "used_count": inv["used_count"],
                "expires_at": inv["expires_at"],
                "is_active": bool(inv["is_active"]),
                "note": inv["note"],
                "created_at": inv["created_at"]
            })
        
        return jsonify(get_response({
            "invitations": result,
            "total": len(result)
        })), 200
        
    except Exception as e:
        logger.error(f"列出邀请码异常: {e}", exc_info=True)
        return jsonify(get_error_response(
            error="获取邀请码列表失败",
            status_code=500,
            error_code=ErrorCode.INTERNAL_ERROR
        )), 500


@api_v1_bp.route("/invitations", methods=["POST"])
@require_admin
def create_invitation():
    """创建新邀请码
    
    Request Body:
        {
            "max_uses": 使用次数上限（可选，默认 1）,
            "expires_at": 过期时间（可选，ISO 格式）,
            "note": 备注（可选）,
            "code": 自定义邀请码（可选，不提供则自动生成）
        }
    
    Response:
        {
            "success": true,
            "data": {
                "invitation": {...}
            }
        }
    """
    try:
        data = request.get_json() or {}
        
        max_uses = data.get("max_uses", 1)
        expires_at = data.get("expires_at")
        note = data.get("note", "")
        custom_code = data.get("code", "").strip().upper()
        
        # 验证参数
        if max_uses < 1:
            return jsonify(get_error_response(
                error="使用次数上限必须大于 0",
                status_code=400,
                error_code=ErrorCode.VALIDATION_ERROR
            )), 400
        
        # 验证过期时间格式
        if expires_at:
            try:
                datetime.fromisoformat(expires_at.replace("Z", "+00:00"))
            except ValueError:
                return jsonify(get_error_response(
                    error="过期时间格式错误，请使用 ISO 格式",
                    status_code=400,
                    error_code=ErrorCode.VALIDATION_ERROR
                )), 400
        
        storage = _get_storage()
        config = get_config()
        
        # 生成或验证邀请码
        if custom_code:
            # 检查自定义邀请码是否已存在
            if storage.get_invitation_code(custom_code):
                return jsonify(get_error_response(
                    error="邀请码已存在",
                    status_code=400,
                    error_code=ErrorCode.CONFLICT
                )), 400
            code = custom_code
        else:
            # 生成唯一邀请码
            max_attempts = 10
            for _ in range(max_attempts):
                code = _generate_invitation_code(config.INVITATION_CODE_LENGTH)
                if not storage.get_invitation_code(code):
                    break
            else:
                return jsonify(get_error_response(
                    error="生成邀请码失败，请重试",
                    status_code=500,
                    error_code=ErrorCode.INTERNAL_ERROR
                )), 500
        
        # 创建邀请码
        user = g.current_user
        code_id = storage.create_invitation_code(
            code=code,
            created_by=user["id"],
            max_uses=max_uses,
            expires_at=expires_at,
            note=note
        )
        
        if not code_id:
            return jsonify(get_error_response(
                error="创建邀请码失败",
                status_code=500,
                error_code=ErrorCode.INTERNAL_ERROR
            )), 500
        
        # 获取创建的邀请码
        invitation = storage.get_invitation_code_by_id(code_id)
        
        logger.info(f"邀请码创建成功: code={code}, created_by={user['id']}, max_uses={max_uses}")
        
        return jsonify(get_response({
            "invitation": {
                "id": invitation["id"],
                "code": invitation["code"],
                "created_by": invitation["created_by"],
                "max_uses": invitation["max_uses"],
                "used_count": invitation["used_count"],
                "expires_at": invitation["expires_at"],
                "is_active": bool(invitation["is_active"]),
                "note": invitation["note"],
                "created_at": invitation["created_at"]
            }
        }, message="邀请码创建成功")), 201
        
    except Exception as e:
        logger.error(f"创建邀请码异常: {e}", exc_info=True)
        return jsonify(get_error_response(
            error="创建邀请码失败",
            status_code=500,
            error_code=ErrorCode.INTERNAL_ERROR
        )), 500


@api_v1_bp.route("/invitations/<int:code_id>", methods=["GET"])
@require_admin
def get_invitation(code_id: int):
    """获取单个邀请码详情
    
    Response:
        {
            "success": true,
            "data": {
                "invitation": {...}
            }
        }
    """
    try:
        storage = _get_storage()
        invitation = storage.get_invitation_code_by_id(code_id)
        
        if not invitation:
            return jsonify(get_error_response(
                error="邀请码不存在",
                status_code=404,
                error_code=ErrorCode.RESOURCE_NOT_FOUND
            )), 404
        
        return jsonify(get_response({
            "invitation": {
                "id": invitation["id"],
                "code": invitation["code"],
                "created_by": invitation["created_by"],
                "max_uses": invitation["max_uses"],
                "used_count": invitation["used_count"],
                "expires_at": invitation["expires_at"],
                "is_active": bool(invitation["is_active"]),
                "note": invitation["note"],
                "created_at": invitation["created_at"]
            }
        })), 200
        
    except Exception as e:
        logger.error(f"获取邀请码异常: {e}", exc_info=True)
        return jsonify(get_error_response(
            error="获取邀请码失败",
            status_code=500,
            error_code=ErrorCode.INTERNAL_ERROR
        )), 500


@api_v1_bp.route("/invitations/<int:code_id>", methods=["PUT"])
@require_admin
def update_invitation(code_id: int):
    """更新邀请码
    
    Request Body:
        {
            "max_uses": 使用次数上限（可选）,
            "expires_at": 过期时间（可选）,
            "is_active": 是否启用（可选）,
            "note": 备注（可选）
        }
    
    Response:
        {
            "success": true,
            "data": {
                "invitation": {...}
            }
        }
    """
    try:
        storage = _get_storage()
        invitation = storage.get_invitation_code_by_id(code_id)
        
        if not invitation:
            return jsonify(get_error_response(
                error="邀请码不存在",
                status_code=404,
                error_code=ErrorCode.RESOURCE_NOT_FOUND
            )), 404
        
        data = request.get_json() or {}
        
        # 构建更新字段
        update_fields = {}
        
        if "max_uses" in data:
            max_uses = data["max_uses"]
            if max_uses < 1:
                return jsonify(get_error_response(
                    error="使用次数上限必须大于 0",
                    status_code=400,
                    error_code=ErrorCode.VALIDATION_ERROR
                )), 400
            update_fields["max_uses"] = max_uses
        
        if "expires_at" in data:
            expires_at = data["expires_at"]
            if expires_at:
                try:
                    datetime.fromisoformat(expires_at.replace("Z", "+00:00"))
                except ValueError:
                    return jsonify(get_error_response(
                        error="过期时间格式错误",
                        status_code=400,
                        error_code=ErrorCode.VALIDATION_ERROR
                    )), 400
            update_fields["expires_at"] = expires_at
        
        if "is_active" in data:
            update_fields["is_active"] = 1 if data["is_active"] else 0
        
        if "note" in data:
            update_fields["note"] = data["note"]
        
        if not update_fields:
            return jsonify(get_error_response(
                error="没有要更新的字段",
                status_code=400,
                error_code=ErrorCode.INVALID_INPUT
            )), 400
        
        # 执行更新
        if not storage.update_invitation_code(code_id, **update_fields):
            return jsonify(get_error_response(
                error="更新邀请码失败",
                status_code=500,
                error_code=ErrorCode.INTERNAL_ERROR
            )), 500
        
        # 获取更新后的邀请码
        invitation = storage.get_invitation_code_by_id(code_id)
        
        logger.info(f"邀请码更新成功: code_id={code_id}, fields={list(update_fields.keys())}")
        
        return jsonify(get_response({
            "invitation": {
                "id": invitation["id"],
                "code": invitation["code"],
                "created_by": invitation["created_by"],
                "max_uses": invitation["max_uses"],
                "used_count": invitation["used_count"],
                "expires_at": invitation["expires_at"],
                "is_active": bool(invitation["is_active"]),
                "note": invitation["note"],
                "created_at": invitation["created_at"]
            }
        }, message="邀请码更新成功")), 200
        
    except Exception as e:
        logger.error(f"更新邀请码异常: {e}", exc_info=True)
        return jsonify(get_error_response(
            error="更新邀请码失败",
            status_code=500,
            error_code=ErrorCode.INTERNAL_ERROR
        )), 500


@api_v1_bp.route("/invitations/<int:code_id>", methods=["DELETE"])
@require_admin
def delete_invitation(code_id: int):
    """删除邀请码
    
    Response:
        {
            "success": true,
            "message": "邀请码已删除"
        }
    """
    try:
        storage = _get_storage()
        invitation = storage.get_invitation_code_by_id(code_id)
        
        if not invitation:
            return jsonify(get_error_response(
                error="邀请码不存在",
                status_code=404,
                error_code=ErrorCode.RESOURCE_NOT_FOUND
            )), 404
        
        if not storage.delete_invitation_code(code_id):
            return jsonify(get_error_response(
                error="删除邀请码失败",
                status_code=500,
                error_code=ErrorCode.INTERNAL_ERROR
            )), 500
        
        logger.info(f"邀请码删除成功: code_id={code_id}, code={invitation['code']}")
        
        return jsonify(get_response(None, message="邀请码已删除")), 200
        
    except Exception as e:
        logger.error(f"删除邀请码异常: {e}", exc_info=True)
        return jsonify(get_error_response(
            error="删除邀请码失败",
            status_code=500,
            error_code=ErrorCode.INTERNAL_ERROR
        )), 500
