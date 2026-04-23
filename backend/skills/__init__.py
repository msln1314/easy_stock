"""
Skills系统

提供可扩展的技能定义和发现机制
让AI交易助手根据不同场景激活不同的技能
"""
from .base_skill import BaseSkill, parse_skill_file, discover_skills
from .skill_service import SkillService, skill_service

__all__ = [
    "BaseSkill",
    "parse_skill_file",
    "discover_skills",
    "SkillService",
    "skill_service",
]