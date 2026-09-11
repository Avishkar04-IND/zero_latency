import {
  apiClient,
  setStoredToken,
  setStoredUser,
  getStoredToken,
  getStoredUser,
  ApiError,
} from "./client";
import {
  LoginRequest,
  BackendTokenResponse,
  AuthenticatedUser,
} from "@/types/auth";

/**
 * TEMPORARY MOCK AUTHENTICATION HANDLER
 * Used ONLY when NEXT_PUBLIC_MOCK_AUTH === "true" or when backend server is genuinely unreachable.
 * Mimics Member 1's backend contract and seed data exactly.
 */
const IS_MOCK_MODE_ENABLED =
  process.env.NEXT_PUBLIC_MOCK_AUTH === "true" ||
  process.env.NEXT_PUBLIC_USE_MOCK_API === "true";

const MOCK_SEED_USER: AuthenticatedUser = {
  id: 1,
  name: "Dr. Rajiv Sharma",
  email: "admin@pharma.com",
  role: "company_admin",
  organization_id: 1,
  organization_name: "Apex National Pharma",
  branch_name: "Main Packaging Unit - Mumbai",
  is_active: true,
};

export const authService = {
  /**
   * Authenticate admin against backend POST /api/v1/auth/login
   */
  async login(credentials: LoginRequest): Promise<AuthenticatedUser> {
    try {
      const tokenResponse = await apiClient<BackendTokenResponse>("/auth/login", {
        method: "POST",
        body: JSON.stringify({
          email: credentials.email.trim(),
          password: credentials.password,
        }),
      });

      // Save token in client storage
      setStoredToken(tokenResponse.access_token);

      const authenticatedUser: AuthenticatedUser = {
        id: tokenResponse.user_id,
        name: tokenResponse.name,
        email: tokenResponse.email,
        role: tokenResponse.role,
        organization_id: tokenResponse.organization_id,
        organization_name: tokenResponse.organization_name || "Pharmaceutical Partner",
        branch_name: "Plant Unit 01 — Serialization Facility",
        is_active: true,
      };

      setStoredUser(authenticatedUser);
      return authenticatedUser;
    } catch (err: any) {
      // If mock mode is explicitly enabled or server is offline, provide isolated dev fallback
      if (
        (IS_MOCK_MODE_ENABLED || err.status === 0) &&
        credentials.email.toLowerCase() === "admin@pharma.com" &&
        credentials.password === "Admin@12345"
      ) {
        console.warn(
          "[AUTH WARNING] Live backend connection offline. Using isolated development mock aligned with Member 1 seed data."
        );
        const mockToken = `mock-bearer-jwt-${Date.now()}`;
        setStoredToken(mockToken);
        setStoredUser(MOCK_SEED_USER);
        return MOCK_SEED_USER;
      }

      // Re-throw genuine backend or validation error
      throw err;
    }
  },

  /**
   * Fetch authenticated user profile from GET /api/v1/auth/me
   */
  async getMe(): Promise<AuthenticatedUser | null> {
    const token = getStoredToken();
    if (!token) return null;

    try {
      const userResponse = await apiClient<{
        id: number;
        name: string;
        email: string;
        role: string;
        organization_id?: number | null;
        is_active: boolean;
      }>("/auth/me");

      const cachedUser = getStoredUser();

      const authenticatedUser: AuthenticatedUser = {
        id: userResponse.id,
        name: userResponse.name,
        email: userResponse.email,
        role: userResponse.role,
        organization_id: userResponse.organization_id,
        organization_name: cachedUser?.organization_name || "Sun Pharmaceutical Industries Ltd.",
        branch_name: cachedUser?.branch_name || "Plant Unit 01 — Serialization Facility",
        is_active: userResponse.is_active,
      };

      setStoredUser(authenticatedUser);
      return authenticatedUser;
    } catch (err) {
      // Return cached user if offline fallback is active
      const cached = getStoredUser();
      if (cached && (IS_MOCK_MODE_ENABLED || (err as ApiError).status === 0)) {
        return cached;
      }
      return null;
    }
  },

  /**
   * Logout user and clear stored tokens
   */
  async logout(): Promise<void> {
    setStoredToken(null);
    setStoredUser(null);
  },

  /**
   * Check if current session exists in local cache
   */
  getCachedUser(): AuthenticatedUser | null {
    return getStoredUser();
  },

  /**
   * Check if JWT token is stored
   */
  hasToken(): boolean {
    return !!getStoredToken();
  },
};
