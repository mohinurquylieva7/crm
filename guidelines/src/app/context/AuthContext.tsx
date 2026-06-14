import { createContext, useContext, useState, useCallback, type ReactNode } from 'react';
import type { UserRole } from '../types';

export interface AuthUser {
  id: string;
  email: string;
  fullName: string;
  role: UserRole;
  avatar?: string;
  centerName?: string;
}

interface AuthState {
  user: AuthUser | null;
  accessToken: string | null;
  isAuthenticated: boolean;
}

interface AuthContextValue extends AuthState {
  login: (email: string, password: string, remember: boolean) => Promise<void>;
  register: (data: RegisterData) => Promise<void>;
  logout: () => void;
}

export interface RegisterData {
  fullName: string;
  email: string;
  password: string;
  centerName: string;
  phone: string;
}

const AuthContext = createContext<AuthContextValue | null>(null);

const AUTH_KEY   = 'educrm_auth';
const USERS_KEY  = 'educrm_users';

// Builtin demo users (never persisted — always available)
const BUILTIN_USERS: Array<AuthUser & { password: string }> = [
  {
    id: 'u1',
    email: 'admin@fashion.uz',
    password: 'Admin1234!',
    fullName: 'Sardor Toshmatov',
    role: 'admin',
    centerName: 'Reteake CRM',
    avatar: undefined,
  },
  {
    id: 'u2',
    email: 'seller@fashion.uz',
    password: 'Seller1234!',
    fullName: 'Malika Yusupova',
    role: 'seller',
    centerName: 'Reteake CRM',
    avatar: undefined,
  },
];

// Load registered users from localStorage (persists across refreshes)
function loadRegisteredUsers(): Array<AuthUser & { password: string }> {
  try {
    const raw = localStorage.getItem(USERS_KEY);
    if (raw) return JSON.parse(raw);
  } catch { /* ignore */ }
  return [];
}

function saveRegisteredUsers(users: Array<AuthUser & { password: string }>) {
  localStorage.setItem(USERS_KEY, JSON.stringify(users));
}

function getAllUsers() {
  return [...BUILTIN_USERS, ...loadRegisteredUsers()];
}

function loadStoredAuth(): AuthState {
  for (const store of [localStorage, sessionStorage]) {
    try {
      const raw = store.getItem(AUTH_KEY);
      if (raw) {
        const parsed = JSON.parse(raw);
        if (parsed?.user && parsed?.accessToken) {
          return { user: parsed.user, accessToken: parsed.accessToken, isAuthenticated: true };
        }
      }
    } catch { /* ignore */ }
  }
  return { user: null, accessToken: null, isAuthenticated: false };
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<AuthState>(loadStoredAuth);

  const login = useCallback(async (email: string, password: string, remember: boolean) => {
    await new Promise(r => setTimeout(r, 800));

    const all = getAllUsers();
    const found = all.find(u => u.email.toLowerCase() === email.toLowerCase() && u.password === password);
    if (!found) {
      throw new Error("Email yoki parol noto'g'ri");
    }

    const { password: _, ...user } = found;
    const accessToken = `mock_token_${user.id}_${Date.now()}`;
    const next: AuthState = { user, accessToken, isAuthenticated: true };
    setState(next);

    const store = remember ? localStorage : sessionStorage;
    // Clear the other store to avoid stale sessions
    (remember ? sessionStorage : localStorage).removeItem(AUTH_KEY);
    store.setItem(AUTH_KEY, JSON.stringify(next));
  }, []);

  const register = useCallback(async (data: RegisterData) => {
    await new Promise(r => setTimeout(r, 1000));

    const all = getAllUsers();
    if (all.find(u => u.email.toLowerCase() === data.email.toLowerCase())) {
      throw new Error("Bu email allaqachon ro'yxatdan o'tgan");
    }

    const newUser: AuthUser = {
      id: `u_${Date.now()}`,
      email: data.email,
      fullName: data.fullName,
      role: 'admin',
      centerName: data.centerName,
    };

    // Persist registered user so they can re-login after page refresh
    const registered = loadRegisteredUsers();
    registered.push({ ...newUser, password: data.password });
    saveRegisteredUsers(registered);

    const accessToken = `mock_token_${newUser.id}_${Date.now()}`;
    const next: AuthState = { user: newUser, accessToken, isAuthenticated: true };
    setState(next);
    localStorage.setItem(AUTH_KEY, JSON.stringify(next));
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem(AUTH_KEY);
    sessionStorage.removeItem(AUTH_KEY);
    setState({ user: null, accessToken: null, isAuthenticated: false });
    // Hard redirect ensures clean state even if React re-render is blocked
    window.location.href = window.location.origin;
  }, []);

  return (
    <AuthContext.Provider value={{ ...state, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used inside <AuthProvider>');
  return ctx;
}
