"""
系统配置业务逻辑服务
"""
from typing import Optional, Dict, Any
from tortoise.expressions import Q
from models.sys_config import SysConfig
from schemas.config import (
    SysConfigCreate, SysConfigUpdate, SysConfigResponse,
    SysConfigListResponse, SysConfigPaginatedResponse, PublicConfigResponse
)
from utils.crypto import aes_encrypt, aes_decrypt


class SysConfigService:
    """系统配置服务"""

    async def create_config(self, data: SysConfigCreate) -> SysConfig:
        """创建系统配置"""
        # 加密处理
        value = data.value
        if data.data_type == "encrypted" and value:
            value = aes_encrypt(value)

        config = await SysConfig.create(
            key=data.key,
            value=value,
            category=data.category,
            data_type=data.data_type,
            access_type=data.access_type,
            description=data.description
        )
        return config

    async def get_config(self, config_id: int) -> Optional[SysConfig]:
        """获取单个配置"""
        return await SysConfig.get_or_none(id=config_id)

    async def get_config_by_key(self, key: str) -> Optional[SysConfig]:
        """根据键获取配置"""
        return await SysConfig.get_or_none(key=key)

    async def get_config_value(self, key: str) -> Optional[str]:
        """获取配置值（自动解密）"""
        config = await SysConfig.get_or_none(key=key)
        if not config:
            return None

        if config.data_type == "encrypted" and config.value:
            return aes_decrypt(config.value)
        return config.value

    async def get_configs(
        self,
        category: Optional[str] = None,
        access_type: Optional[str] = None,
        keyword: Optional[str] = None,
        page: int = 1,
        page_size: int = 10,
        is_admin: bool = False
    ) -> SysConfigPaginatedResponse:
        """获取配置列表"""
        query = SysConfig.all()
        if category:
            query = query.filter(category=category)
        if access_type:
            query = query.filter(access_type=access_type)
        if keyword:
            query = query.filter(Q(key__icontains=keyword) | Q(description__icontains=keyword))

        total = await query.count()
        configs = await query.order_by('category', 'key').offset((page - 1) * page_size).limit(page_size).all()

        items = []
        for cfg in configs:
            # 私有配置非管理员不返回value
            value = cfg.value if (is_admin or cfg.access_type == "public") else None

            items.append(SysConfigListResponse(
                id=cfg.id,
                key=cfg.key,
                value=value,
                category=cfg.category,
                data_type=cfg.data_type,
                access_type=cfg.access_type,
                description=cfg.description,
                created_at=cfg.created_at
            ))

        return SysConfigPaginatedResponse(
            total=total,
            page=page,
            page_size=page_size,
            items=items
        )

    async def get_public_configs(self) -> Dict[str, Any]:
        """获取所有公开配置（无需认证）"""
        configs = await SysConfig.filter(
            access_type="public",
            data_type="plain"  # 公开配置仅返回明文配置
        ).all()

        return {cfg.key: cfg.value for cfg in configs}

    async def get_configs_by_category(
        self,
        category: str,
        is_admin: bool = False
    ) -> list:
        """按类别获取配置"""
        configs = await SysConfig.filter(category=category).order_by('key').all()

        result = []
        for cfg in configs:
            # 处理加密值
            decrypted_value = None
            if is_admin and cfg.data_type == "encrypted" and cfg.value:
                decrypted_value = aes_decrypt(cfg.value)

            # 私有配置非管理员不返回value
            value = cfg.value if (is_admin or cfg.access_type == "public") else None

            result.append({
                "id": cfg.id,
                "key": cfg.key,
                "value": value,
                "category": cfg.category,
                "data_type": cfg.data_type,
                "access_type": cfg.access_type,
                "description": cfg.description,
                "decrypted_value": decrypted_value,
                "created_at": cfg.created_at.isoformat(),
                "updated_at": cfg.updated_at.isoformat()
            })

        return result

    async def update_config(self, key: str, data: SysConfigUpdate) -> Optional[SysConfig]:
        """更新配置"""
        config = await SysConfig.get_or_none(key=key)
        if not config:
            return None

        update_data = data.dict(exclude_unset=True)

        # 处理加密
        if 'value' in update_data:
            # 根据当前或新的data_type决定是否加密
            new_data_type = update_data.get('data_type', config.data_type)
            if new_data_type == "encrypted" and update_data['value']:
                update_data['value'] = aes_encrypt(update_data['value'])

        if update_data:
            await SysConfig.filter(key=key).update(**update_data)

        return await SysConfig.get(key=key)

    async def delete_config(self, key: str) -> bool:
        """删除配置"""
        config = await SysConfig.get_or_none(key=key)
        if not config:
            return False

        await config.delete()
        return True

    async def batch_update(self, configs: Dict[str, str]) -> bool:
        """批量更新配置值"""
        for key, value in configs.items():
            config = await SysConfig.get_or_none(key=key)
            if config:
                if config.data_type == "encrypted":
                    value = aes_encrypt(value)
                await SysConfig.filter(key=key).update(value=value)
        return True