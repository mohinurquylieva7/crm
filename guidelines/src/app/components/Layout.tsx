import { useState, useEffect } from 'react';
import { useLanguage } from '../context/LanguageContext';

const UZ_DAYS = ['Yakshanba', 'Dushanba', 'Seshanba', 'Chorshanba', 'Payshanba', 'Juma', 'Shanba'];
const UZ_MONTHS = ['Yanvar', 'Fevral', 'Mart', 'Aprel', 'May', 'Iyun', 'Iyul', 'Avgust', 'Sentabr', 'Oktabr', 'Noyabr', 'Dekabr'];

function formatTodayUz(): string {
  const d = new Date();
  return `${d.getDate()} ${UZ_MONTHS[d.getMonth()]}, ${d.getFullYear()} · ${UZ_DAYS[d.getDay()]}`;
}
import {
  LayoutDashboard, Users, ShoppingBag, ShoppingCart,
  FileBarChart, Settings, Bell, ChevronDown,
  Menu, X, LogOut, ChevronRight, Package,
} from 'lucide-react';
import type { Notification } from '../types';
import { useAuth } from '../context/AuthContext';

type PageKey = 'dashboard' | 'products' | 'customers' | 'sales' | 'reports' | 'settings';

interface LayoutProps {
  currentPage: PageKey;
  onNavigate: (page: PageKey) => void;
  notifications: Notification[];
  children: React.ReactNode;
}

const NAV_KEYS: { key: PageKey; tKey: any; icon: any }[] = [
  { key: 'dashboard', tKey: 'dashboard', icon: LayoutDashboard },
  { key: 'products',  tKey: 'products',  icon: ShoppingBag },
  { key: 'customers', tKey: 'customers', icon: Users },
  { key: 'sales',     tKey: 'sales',     icon: ShoppingCart },
  { key: 'reports',   tKey: 'reports',   icon: FileBarChart },
  { key: 'settings',  tKey: 'settings',  icon: Settings },
];

export function Layout({ currentPage, onNavigate, notifications, children }: LayoutProps) {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [mobileSidebarOpen, setMobileSidebarOpen] = useState(false);
  const [notifOpen, setNotifOpen] = useState(false);
  const [profileOpen, setProfileOpen] = useState(false);
  const { logout, user } = useAuth();
  const { t } = useLanguage();

  const unreadCount = notifications.filter(n => !n.read).length;

  // Close mobile sidebar on resize to desktop
  useEffect(() => {
    const onResize = () => {
      if (window.innerWidth >= 1024) setMobileSidebarOpen(false);
    };
    window.addEventListener('resize', onResize);
    return () => window.removeEventListener('resize', onResize);
  }, []);

  const handleNavigate = (page: PageKey) => {
    onNavigate(page);
    setMobileSidebarOpen(false);
  };

  const navItems = NAV_KEYS.map(n => ({ ...n, label: t(n.tKey) }));

  const SidebarContent = ({ mobile = false }: { mobile?: boolean }) => (
    <>
      {/* Logo */}
      <div className="flex items-center h-16 px-4 border-b border-slate-700 shrink-0">
        <div className="flex items-center gap-3 overflow-hidden">
          <div className="flex items-center justify-center w-9 h-9 rounded-xl bg-violet-500 shrink-0 shadow-lg">
            <Package className="w-5 h-5 text-white" />
          </div>
          {(mobile || sidebarOpen) && (
            <div className="overflow-hidden">
              <p className="text-white font-bold text-sm leading-tight truncate">Reteake CRM</p>
              <p className="text-violet-400 text-xs truncate">Kiyim sotuv tizimi</p>
            </div>
          )}
        </div>
        {mobile && (
          <button
            onClick={() => setMobileSidebarOpen(false)}
            className="ml-auto w-8 h-8 flex items-center justify-center rounded-xl bg-white/10 hover:bg-white/20 text-white transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        )}
      </div>

      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto py-4 px-2 space-y-1">
        {navItems.map(item => {
          const Icon = item.icon;
          const isActive = currentPage === item.key;
          return (
            <button
              key={item.key}
              onClick={() => handleNavigate(item.key)}
              className={`
                w-full flex items-center gap-3 px-3 py-2.5 rounded-xl transition-all duration-150 group relative
                ${isActive
                  ? 'bg-blue-600 text-white shadow-lg shadow-blue-900/30'
                  : 'text-slate-400 hover:text-white hover:bg-slate-700/60'
                }
              `}
              title={!mobile && !sidebarOpen ? item.label : undefined}
            >
              <Icon className={`w-5 h-5 shrink-0 ${isActive ? 'text-white' : 'text-slate-400 group-hover:text-blue-400'}`} />
              {(mobile || sidebarOpen) && (
                <span className="text-sm font-medium truncate">{item.label}</span>
              )}
              {isActive && (mobile || sidebarOpen) && (
                <ChevronRight className="w-4 h-4 ml-auto text-blue-200" />
              )}
              {!mobile && !sidebarOpen && isActive && (
                <span className="absolute left-full ml-2 px-2 py-1 bg-blue-600 text-white text-xs rounded-md whitespace-nowrap opacity-0 group-hover:opacity-100 pointer-events-none">
                  {item.label}
                </span>
              )}
            </button>
          );
        })}
      </nav>

      {/* Bottom toggle (desktop only) */}
      {!mobile && (
        <div className="p-3 border-t border-slate-700 shrink-0">
          <button
            onClick={() => setSidebarOpen(v => !v)}
            className="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-slate-400 hover:text-white hover:bg-slate-700/60 transition-all"
          >
            <Menu className="w-5 h-5 shrink-0" />
            {sidebarOpen && <span className="text-sm">{t('collapse')}</span>}
          </button>
        </div>
      )}
    </>
  );

  return (
    <div className="flex h-screen bg-slate-50 overflow-hidden">
      {/* Desktop Sidebar */}
      <aside
        className={`
          hidden lg:flex flex-col bg-gradient-to-b from-slate-900 to-slate-800
          transition-all duration-300 ease-in-out shrink-0
          ${sidebarOpen ? 'w-64' : 'w-16'}
          border-r border-slate-700 z-30 shadow-xl
        `}
      >
        <SidebarContent />
      </aside>

      {/* Mobile Sidebar Overlay */}
      {mobileSidebarOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/50 lg:hidden"
          onClick={() => setMobileSidebarOpen(false)}
        />
      )}

      {/* Mobile Sidebar Drawer */}
      <aside
        className={`
          fixed top-0 left-0 h-full w-72 z-50 flex flex-col
          bg-gradient-to-b from-slate-900 to-slate-800
          border-r border-slate-700 shadow-2xl
          transition-transform duration-300 ease-in-out
          lg:hidden
          ${mobileSidebarOpen ? 'translate-x-0' : '-translate-x-full'}
        `}
      >
        <SidebarContent mobile />
      </aside>

      {/* Main content */}
      <div className="flex flex-col flex-1 overflow-hidden min-w-0">
        {/* Header */}
        <header className="h-16 bg-white border-b border-slate-200 flex items-center px-4 sm:px-6 gap-3 shrink-0 shadow-sm z-20">
          {/* Mobile menu button */}
          <button
            onClick={() => setMobileSidebarOpen(true)}
            className="lg:hidden flex items-center justify-center w-9 h-9 rounded-xl bg-slate-100 hover:bg-slate-200 transition-colors text-slate-600"
          >
            <Menu className="w-5 h-5" />
          </button>

          <div className="flex-1 min-w-0">
            <h2 className="text-slate-800 font-semibold text-sm sm:text-base truncate">
              {navItems.find(n => n.key === currentPage)?.label ?? ''}
            </h2>
            <p className="text-slate-400 text-xs hidden sm:block">{formatTodayUz()}</p>
          </div>

          <div className="flex items-center gap-2 sm:gap-3">
            {/* Notifications */}
            <div className="relative">
              <button
                onClick={() => { setNotifOpen(v => !v); setProfileOpen(false); }}
                className="relative flex items-center justify-center w-9 h-9 rounded-xl bg-slate-100 hover:bg-slate-200 transition-colors text-slate-600"
              >
                <Bell className="w-5 h-5" />
                {unreadCount > 0 && (
                  <span className="absolute -top-1 -right-1 flex items-center justify-center w-4 h-4 bg-red-500 text-white text-[10px] font-bold rounded-full">
                    {unreadCount}
                  </span>
                )}
              </button>

              {notifOpen && (
                <div className="absolute right-0 top-12 w-72 sm:w-80 bg-white rounded-2xl shadow-2xl border border-slate-200 z-50 overflow-hidden">
                  <div className="flex items-center justify-between px-4 py-3 border-b border-slate-100">
                    <span className="font-semibold text-slate-800">{t('notifications')}</span>
                    <span className="text-xs bg-red-100 text-red-600 px-2 py-0.5 rounded-full font-medium">{unreadCount} {t('newNotif')}</span>
                  </div>
                  <div className="max-h-72 overflow-y-auto divide-y divide-slate-50">
                    {notifications.map(n => (
                      <div key={n.id} className={`px-4 py-3 hover:bg-slate-50 transition-colors ${!n.read ? 'bg-blue-50/50' : ''}`}>
                        <div className="flex items-start gap-3">
                          <span className={`mt-0.5 w-2 h-2 rounded-full shrink-0 ${
                            n.type === 'success' ? 'bg-emerald-500' :
                            n.type === 'warning' ? 'bg-amber-500' :
                            n.type === 'error' ? 'bg-red-500' : 'bg-blue-500'
                          }`} />
                          <div className="min-w-0">
                            <p className="text-sm font-medium text-slate-800">{n.title}</p>
                            <p className="text-xs text-slate-500 mt-0.5">{n.message}</p>
                            <p className="text-xs text-slate-400 mt-1">{n.date}</p>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                  <div className="px-4 py-2 border-t border-slate-100 text-center">
                    <button className="text-xs text-blue-600 hover:underline font-medium">{t('viewAll')}</button>
                  </div>
                </div>
              )}
            </div>

            {/* Profile */}
            <div className="relative">
              <button
                onClick={() => { setProfileOpen(v => !v); setNotifOpen(false); }}
                className="flex items-center gap-2 px-2 sm:px-3 py-1.5 rounded-xl hover:bg-slate-100 transition-colors"
              >
                <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-violet-600 flex items-center justify-center text-white font-bold text-sm shrink-0">
                  {user?.fullName?.[0]?.toUpperCase() ?? 'A'}
                </div>
                <div className="hidden sm:block text-left">
                  <p className="text-sm font-medium text-slate-800 leading-tight">{user?.fullName ?? 'Admin'}</p>
                  <p className="text-xs text-slate-400 leading-tight capitalize">{user?.role ?? 'admin'}</p>
                </div>
                <ChevronDown className="w-4 h-4 text-slate-400 hidden sm:block" />
              </button>

              {profileOpen && (
                <div className="absolute right-0 top-12 w-52 bg-white rounded-2xl shadow-2xl border border-slate-200 z-50 overflow-hidden">
                  <div className="px-4 py-3 border-b border-slate-100">
                    <p className="font-semibold text-slate-800">{user?.fullName ?? 'Admin'}</p>
                    <p className="text-xs text-slate-500">{user?.email}</p>
                  </div>
                  <div className="p-2">
                    <button
                      onClick={() => { onNavigate('settings'); setProfileOpen(false); }}
                      className="w-full flex items-center gap-2 px-3 py-2 rounded-lg text-sm text-slate-700 hover:bg-slate-100 transition-colors"
                    >
                      <Settings className="w-4 h-4" /> {t('settings')}
                    </button>
                    <button
                      onClick={logout}
                      className="w-full flex items-center gap-2 px-3 py-2 rounded-lg text-sm text-red-600 hover:bg-red-50 transition-colors"
                    >
                      <LogOut className="w-4 h-4" /> {t('logout')}
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        </header>

        {/* Page Content */}
        <main className="flex-1 overflow-y-auto p-4 sm:p-6">
          {children}
        </main>
      </div>

      {/* Click outside to close dropdowns */}
      {(notifOpen || profileOpen) && (
        <div
          className="fixed inset-0 z-40"
          onClick={() => { setNotifOpen(false); setProfileOpen(false); }}
        />
      )}
    </div>
  );
}
