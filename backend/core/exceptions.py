"""
异常处理
"""
from fastapi import HTTPException
from core.response import error_response


class AppException(Exception):
    """应用异常基类"""
    def __init__(self, message: str, code: int = 400):
        self.message = message
        self.code = code


class NotFoundException(AppException):
    """资源未找到异常"""
    def __init__(self, message: str = "资源未找到"):
        super().__init__(message, 404)


class ValidationException(AppException):
    """数据验证异常"""
    def __init__(self, message: str = "数据验证失败"):
        super().__init__(message, 400)


class BusinessException(AppException):
    """业务逻辑异常"""
    def __init__(self, message: str):
        super().__init__(message, 400)


async def app_exception_handler(request, exc: AppException):
    """应用异常处理器"""
    return error_response(message=exc.message, code=exc.code)


async def http_exception_handler(request, exc: HTTPException):
    """HTTP异常处理器"""
    return error_response(message=exc.detail, code=exc.status_code)


async def generic_exception_handler(request, exc: Exception):
    """通用异常处理器"""
    return error_response(message="服务器内部错误", code=500)