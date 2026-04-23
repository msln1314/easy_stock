-- 添加用户 API Key 字段
ALTER TABLE t_user ADD COLUMN IF NOT EXISTS api_key VARCHAR(64) NULL UNIQUE COMMENT 'API Key(用于接口认证)';

-- 为现有用户生成 API Key（可选）
-- UPDATE t_user SET api_key = MD5(RAND()) WHERE api_key IS NULL;