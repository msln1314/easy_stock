/**
 * 验证码API
 */
import request from '@/utils/request'

export interface CaptchaResponse {
  captcha_id: string
  image: string
}

/**
 * 获取验证码
 */
export function getCaptcha() {
  return request.get<any, { code: number; data: CaptchaResponse }>('/v1/captcha')
}

/**
 * 验证验证码
 */
export function verifyCaptcha(captchaId: string, captchaCode: string) {
  return request.post<any, { code: number; message: string }>('/v1/captcha/verify', {
    captcha_id: captchaId,
    captcha_code: captchaCode
  })
}