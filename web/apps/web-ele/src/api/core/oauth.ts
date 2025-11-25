import { requestClient } from '#/api/request';

export namespace OAuthApi {
  /** OAuth 提供商类型 */
  export type OAuthProvider = 'gitee' | 'github' | 'qq' | 'google' | 'wechat' | 'microsoft' | 'dingtalk' | 'feishu';

  /** OAuth 回调参数 */
  export interface OAuthCallbackParams {
    code: string;
    state?: string;
  }

  /** OAuth 登录返回值 */
  export interface OAuthLoginResult {
    access_token: string;
    refresh_token: string;
    expire: number;
    user_info: {
      avatar?: string;
      email?: string;
      id: string;
      is_superuser: boolean;
      name: string;
      user_type: number;
      username: string;
    };
  }

  /** 授权 URL 返回值 */
  export interface AuthorizeUrlResult {
    authorize_url: string;
  }

  // 兼容旧接口
  export type GiteeCallbackParams = OAuthCallbackParams;
}

/**
 * 获取 OAuth 授权 URL (通用接口)
 * @param provider OAuth 提供商 (gitee/github)
 * @param state 状态参数
 */
export async function getOAuthAuthorizeUrlApi(
  provider: OAuthApi.OAuthProvider,
  state?: string,
) {
  const params = state ? { state } : {};
  return requestClient.get<OAuthApi.AuthorizeUrlResult>(
    `/api/core/oauth/${provider}/authorize`,
    { params },
  );
}

/**
 * OAuth 回调处理 (通用接口)
 * @param provider OAuth 提供商 (gitee/github)
 * @param data 回调数据
 */
export async function oauthCallbackApi(
  provider: OAuthApi.OAuthProvider,
  data: OAuthApi.OAuthCallbackParams,
) {
  return requestClient.post<OAuthApi.OAuthLoginResult>(
    `/api/core/oauth/${provider}/callback`,
    data,
  );
}

/**
 * 获取 Gitee 授权 URL (兼容旧接口)
 */
export async function getGiteeAuthorizeUrlApi(state?: string) {
  return getOAuthAuthorizeUrlApi('gitee', state);
}

/**
 * Gitee OAuth 回调处理 (兼容旧接口)
 */
export async function giteeOAuthCallbackApi(
  data: OAuthApi.GiteeCallbackParams,
) {
  return oauthCallbackApi('gitee', data);
}

/**
 * 获取 GitHub 授权 URL
 */
export async function getGitHubAuthorizeUrlApi(state?: string) {
  return getOAuthAuthorizeUrlApi('github', state);
}

/**
 * GitHub OAuth 回调处理
 */
export async function gitHubOAuthCallbackApi(
  data: OAuthApi.OAuthCallbackParams,
) {
  return oauthCallbackApi('github', data);
}

/**
 * 获取 QQ 授权 URL
 */
export async function getQQAuthorizeUrlApi(state?: string) {
  return getOAuthAuthorizeUrlApi('qq', state);
}

/**
 * QQ OAuth 回调处理
 */
export async function qqOAuthCallbackApi(data: OAuthApi.OAuthCallbackParams) {
  return oauthCallbackApi('qq', data);
}

/**
 * 获取 Google 授权 URL
 */
export async function getGoogleAuthorizeUrlApi(state?: string) {
  return getOAuthAuthorizeUrlApi('google', state);
}

/**
 * Google OAuth 回调处理
 */
export async function googleOAuthCallbackApi(
  data: OAuthApi.OAuthCallbackParams,
) {
  return oauthCallbackApi('google', data);
}

/**
 * 获取微信授权 URL
 */
export async function getWeChatAuthorizeUrlApi(state?: string) {
  return getOAuthAuthorizeUrlApi('wechat', state);
}

/**
 * 微信 OAuth 回调处理
 */
export async function wechatOAuthCallbackApi(
  data: OAuthApi.OAuthCallbackParams,
) {
  return oauthCallbackApi('wechat', data);
}

/**
 * 获取微软授权 URL
 */
export async function getMicrosoftAuthorizeUrlApi(state?: string) {
  return getOAuthAuthorizeUrlApi('microsoft', state);
}

/**
 * 微软 OAuth 回调处理
 */
export async function microsoftOAuthCallbackApi(
  data: OAuthApi.OAuthCallbackParams,
) {
  return oauthCallbackApi('microsoft', data);
}

/**
 * 获取钉钉授权 URL
 */
export async function getDingTalkAuthorizeUrlApi(state?: string) {
  return getOAuthAuthorizeUrlApi('dingtalk', state);
}

/**
 * 钉钉 OAuth 回调处理
 */
export async function dingtalkOAuthCallbackApi(
  data: OAuthApi.OAuthCallbackParams,
) {
  return oauthCallbackApi('dingtalk', data);
}

/**
 * 获取飞书授权 URL
 */
export async function getFeishuAuthorizeUrlApi(state?: string) {
  return getOAuthAuthorizeUrlApi('feishu', state);
}

/**
 * 飞书 OAuth 回调处理
 */
export async function feishuOAuthCallbackApi(
  data: OAuthApi.OAuthCallbackParams,
) {
  return oauthCallbackApi('feishu', data);
}
