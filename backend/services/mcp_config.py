"""
MCP配置服务
"""
from typing import Optional, List
from tortoise.expressions import Q
from models.mcp_config import McpConfig
from schemas.mcp_config import (
    McpConfigCreate, McpConfigUpdate, McpConfigResponse,
    McpConfigListResponse
)
from utils.crypto import aes_encrypt, aes_decrypt


class McpConfigService:
    """MCP配置服务"""

    async def create_config(self, data: McpConfigCreate) -> McpConfig:
        """创建MCP配置"""
        # 加密API Key
        api_key = data.api_key
        if api_key:
            api_key = aes_encrypt(api_key)

        config = await McpConfig.create(
            service_name=data.service_name,
            service_url=data.service_url,
            api_key=api_key,
            enabled=data.enabled,
            description=data.description
        )
        return config

    async def get_config(self, config_id: int) -> Optional[McpConfig]:
        """获取单个配置"""
        return await McpConfig.get_or_none(id=config_id)

    async def get_config_by_name(self, service_name: str) -> Optional[McpConfig]:
        """根据服务名获取配置"""
        return await McpConfig.get_or_none(service_name=service_name)

    async def get_config_value(self, service_name: str) -> Optional[dict]:
        """获取配置值（自动解密API Key）"""
        config = await McpConfig.get_or_none(service_name=service_name, enabled=True)
        if not config:
            return None

        api_key = None
        if config.api_key:
            api_key = aes_decrypt(config.api_key)

        return {
            "service_name": config.service_name,
            "service_url": config.service_url,
            "api_key": api_key,
            "enabled": config.enabled
        }

    async def get_configs(
        self,
        enabled: Optional[bool] = None,
        keyword: Optional[str] = None,
        page: int = 1,
        page_size: int = 10
    ) -> McpConfigListResponse:
        """获取配置列表"""
        query = McpConfig.all()
        if enabled is not None:
            query = query.filter(enabled=enabled)
        if keyword:
            query = query.filter(
                Q(service_name__icontains=keyword) |
                Q(description__icontains=keyword)
            )

        total = await query.count()
        configs = await query.order_by('service_name').offset((page - 1) * page_size).limit(page_size).all()

        items = []
        for cfg in configs:
            # 不返回原始API Key，只返回是否存在
            items.append(McpConfigResponse(
                id=cfg.id,
                service_name=cfg.service_name,
                service_url=cfg.service_url,
                api_key="******" if cfg.api_key else None,  # 隐藏实际Key
                enabled=cfg.enabled,
                description=cfg.description,
                created_at=cfg.created_at,
                updated_at=cfg.updated_at
            ))

        return McpConfigListResponse(total=total, items=items)

    async def get_all_enabled_configs(self) -> List[dict]:
        """获取所有启用的配置（用于内部调用）"""
        configs = await McpConfig.filter(enabled=True).all()
        result = []
        for cfg in configs:
            api_key = None
            if cfg.api_key:
                api_key = aes_decrypt(cfg.api_key)
            result.append({
                "service_name": cfg.service_name,
                "service_url": cfg.service_url,
                "api_key": api_key
            })
        return result

    async def update_config(self, config_id: int, data: McpConfigUpdate) -> Optional[McpConfig]:
        """更新配置"""
        config = await McpConfig.get_or_none(id=config_id)
        if not config:
            return None

        update_data = data.dict(exclude_unset=True)

        # 处理API Key加密
        if 'api_key' in update_data and update_data['api_key']:
            update_data['api_key'] = aes_encrypt(update_data['api_key'])

        if update_data:
            await McpConfig.filter(id=config_id).update(**update_data)

        return await McpConfig.get_or_none(id=config_id)

    async def delete_config(self, config_id: int) -> bool:
        """删除配置"""
        config = await McpConfig.get_or_none(id=config_id)
        if not config:
            return False

        await config.delete()
        return True

    async def get_decrypted_api_key(self, service_name: str) -> Optional[str]:
        """获取解密后的API Key"""
        config = await McpConfig.get_or_none(service_name=service_name, enabled=True)
        if not config or not config.api_key:
            return None
        return aes_decrypt(config.api_key)


# 单例
mcp_config_service = McpConfigService()