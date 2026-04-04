"""
验证码API路由
"""
import random
import string
from io import BytesIO
from datetime import datetime, timedelta
from fastapi import APIRouter
from PIL import Image, ImageDraw, ImageFont
from core.response import success_response, error_response
from models.sys_config import SysConfig

router = APIRouter(prefix="/api/v1/captcha", tags=["验证码"])

# 验证码缓存（简单实现，生产环境应使用Redis）
_captcha_cache: dict = {}


def generate_captcha_text(length: int = 4) -> str:
    """生成验证码文本"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))


def create_captcha_image(text: str, width: int = 120, height: int = 40) -> bytes:
    """创建验证码图片"""
    # 创建图片
    image = Image.new('RGB', (width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(image)

    # 使用默认字体
    try:
        font = ImageFont.truetype("arial.ttf", 28)
    except:
        font = ImageFont.load_default()

    # 绘制干扰线
    for _ in range(5):
        x1 = random.randint(0, width)
        y1 = random.randint(0, height)
        x2 = random.randint(0, width)
        y2 = random.randint(0, height)
        draw.line([(x1, y1), (x2, y2)], fill=random.randint(100, 200), width=1)

    # 绘制干扰点
    for _ in range(50):
        x = random.randint(0, width)
        y = random.randint(0, height)
        draw.point((x, y), fill=random.randint(100, 200))

    # 绘制文字
    text_width = len(text) * 25
    text_x = (width - text_width) // 2
    text_y = (height - 30) // 2

    for i, char in enumerate(text):
        # 每个字符随机颜色和位置偏移
        color = random.randint(0, 100)
        offset_y = random.randint(-5, 5)
        draw.text((text_x + i * 25, text_y + offset_y), char, fill=color, font=font)

    # 转换为字节
    buffer = BytesIO()
    image.save(buffer, format='PNG')
    return buffer.getvalue()


@router.get("", response_model=None)
async def get_captcha():
    """获取验证码"""
    # 生成验证码
    captcha_id = ''.join(random.choices(string.ascii_letters + string.digits, k=32))
    captcha_text = generate_captcha_text(4)

    # 缓存验证码（5分钟有效）
    _captcha_cache[captcha_id] = {
        "text": captcha_text.lower(),
        "expires": datetime.utcnow() + timedelta(minutes=5)
    }

    # 清理过期缓存
    expired_keys = [k for k, v in _captcha_cache.items() if v["expires"] < datetime.utcnow()]
    for k in expired_keys:
        del _captcha_cache[k]

    # 生成图片
    image_bytes = create_captcha_image(captcha_text)

    # Base64编码
    import base64
    image_base64 = base64.b64encode(image_bytes).decode('utf-8')

    return success_response({
        "captcha_id": captcha_id,
        "image": f"data:image/png;base64,{image_base64}"
    })


@router.post("/verify", response_model=None)
async def verify_captcha(captcha_id: str, captcha_code: str):
    """验证验证码"""
    # 检查验证码是否存在
    if captcha_id not in _captcha_cache:
        return error_response("验证码已过期", 400)

    cached = _captcha_cache[captcha_id]

    # 检查是否过期
    if cached["expires"] < datetime.utcnow():
        del _captcha_cache[captcha_id]
        return error_response("验证码已过期", 400)

    # 验证码不区分大小写
    if cached["text"] != captcha_code.lower():
        return error_response("验证码错误", 400)

    # 验证成功后删除
    del _captcha_cache[captcha_id]

    return success_response(message="验证成功")


def verify_captcha_internal(captcha_id: str, captcha_code: str) -> bool:
    """内部验证函数（供登录接口使用）"""
    if captcha_id not in _captcha_cache:
        return False

    cached = _captcha_cache[captcha_id]

    if cached["expires"] < datetime.utcnow():
        del _captcha_cache[captcha_id]
        return False

    if cached["text"] != captcha_code.lower():
        return False

    del _captcha_cache[captcha_id]
    return True