"""
Skills管理API
提供Skills列表、详情查询接口
"""
from fastapi import APIRouter
from core.response import success_response
from skills import skill_service

router = APIRouter(prefix="/api/v1/skills", tags=["Skills管理"])


@router.get("", summary="获取所有技能列表")
async def list_skills():
    """
    获取所有可用的Skills列表

    Returns:
        Skills列表，包含名称、描述、触发关键词等
    """
    skills = skill_service.list_skills()
    return success_response({
        "skills": skills,
        "total": len(skills)
    })


@router.get("/{name}", summary="获取技能详情")
async def get_skill_detail(name: str):
    """
    获取指定Skill的详细信息

    Args:
        name: Skill名称

    Returns:
        Skill详细信息
    """
    skill = skill_service.get_skill(name)
    if not skill:
        return success_response({"error": "Skill不存在"}, code=404)

    return success_response(skill.to_dict())


@router.post("/match", summary="匹配技能")
async def match_skill(message: str):
    """
    根据消息内容匹配Skill

    Args:
        message: 用户消息

    Returns:
        匹配的Skill信息，无匹配返回null
    """
    skill = skill_service.match_skill(message)
    if skill:
        return success_response({
            "matched": True,
            "skill": skill.to_dict()
        })
    else:
        return success_response({
            "matched": False,
            "skill": None
        })