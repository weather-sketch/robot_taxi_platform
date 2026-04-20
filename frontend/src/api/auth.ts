import api from "./client";

export interface LoginParams {
  username: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export interface UserInfo {
  username: string;
  display_name: string;
  role: string;
  is_active: boolean;
}

export const authApi = {
  login: (data: LoginParams) => api.post<TokenResponse>("/auth/login", data),
  getMe: () => api.get<UserInfo>("/auth/me"),
};
