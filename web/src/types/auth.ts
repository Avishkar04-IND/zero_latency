export interface LoginRequest {
  email: string;
  password: string;
}

export interface BackendTokenResponse {
  access_token: string;
  token_type: string;
  user_id: number;
  name: string;
  email: string;
  role: string;
  organization_id?: number | null;
  organization_name?: string | null;
}

export interface AuthenticatedUser {
  id: number;
  name: string;
  email: string;
  role: string;
  organization_id?: number | null;
  organization_name?: string | null;
  branch_name?: string | null;
  is_active?: boolean;
}

export interface AuthState {
  user: AuthenticatedUser | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}
