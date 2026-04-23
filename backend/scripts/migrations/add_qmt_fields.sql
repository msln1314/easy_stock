-- 为 t_user 表添加 QMT 账户相关字段
-- 执行时间: 2026-04-17

-- 添加 QMT 账户 ID
ALTER TABLE t_user ADD COLUMN IF NOT EXISTS qmt_account_id VARCHAR(50) NULL COMMENT 'QMT账户ID/账号';

-- 添加 QMT 账户名称
ALTER TABLE t_user ADD COLUMN IF NOT EXISTS qmt_account_name VARCHAR(100) NULL COMMENT 'QMT账户名称';

-- 添加 QMT 客户端路径
ALTER TABLE t_user ADD COLUMN IF NOT EXISTS qmt_client_path VARCHAR(200) NULL COMMENT 'QMT客户端路径';

-- 添加 QMT 会话 ID
ALTER TABLE t_user ADD COLUMN IF NOT EXISTS qmt_session_id INT DEFAULT 123456 COMMENT 'QMT会话ID';

-- 添加 QMT API Key（加密存储）
ALTER TABLE t_user ADD COLUMN IF NOT EXISTS qmt_api_key VARCHAR(100) NULL COMMENT 'QMT API Key(加密存储)';

-- 添加 QMT 启用状态
ALTER TABLE t_user ADD COLUMN IF NOT EXISTS qmt_enabled BOOLEAN DEFAULT FALSE COMMENT '是否启用QMT交易';

-- 创建 MCP 配置表
CREATE TABLE IF NOT EXISTS t_mcp_config (
    id INT PRIMARY KEY AUTO_INCREMENT,
    service_name VARCHAR(50) UNIQUE NOT NULL COMMENT '服务名称',
    service_url VARCHAR(200) NOT NULL COMMENT '服务地址',
    api_key VARCHAR(100) NULL COMMENT 'API Key(加密存储)',
    enabled BOOLEAN DEFAULT TRUE COMMENT '是否启用',
    description VARCHAR(500) NULL COMMENT '描述',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) COMMENT 'MCP服务配置表';

-- 插入默认 qmt-service 配置
INSERT INTO t_mcp_config (service_name, service_url, enabled, description)
VALUES ('qmt-service', 'http://localhost:8009', TRUE, 'QMT量化交易服务')
ON DUPLICATE KEY UPDATE service_url = 'http://localhost:8009';