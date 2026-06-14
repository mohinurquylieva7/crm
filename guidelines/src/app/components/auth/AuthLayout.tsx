import { ShoppingBag, TrendingUp, Package, Users, BarChart3, Star } from 'lucide-react';

const features = [
  { icon: Package, text: "Mahsulot katalogi, o'lcham va rang boshqaruvi" },
  { icon: Users, text: 'Mijozlar bazasi va xarid tarixi' },
  { icon: TrendingUp, text: 'Sotuv va daromad tahlili' },
  { icon: BarChart3, text: 'Real vaqtda hisobotlar va statistika' },
];

const stats = [
  { value: '500+', label: "Do'konlar" },
  { value: '99%', label: 'Mamnuniyat' },
  { value: '10M+', label: 'Sotuvlar' },
];

interface AuthLayoutProps {
  children: React.ReactNode;
}

export function AuthLayout({ children }: AuthLayoutProps) {
  return (
    <div className="min-h-screen flex">
      {/* Left panel */}
      <div className="hidden lg:flex lg:w-[52%] xl:w-[58%] flex-col relative overflow-hidden bg-gradient-to-br from-slate-900 via-violet-950 to-slate-900">
        {/* Decorative blobs */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          <div className="absolute -top-40 -left-40 w-96 h-96 bg-violet-500/20 rounded-full blur-3xl" />
          <div className="absolute top-1/3 -right-20 w-80 h-80 bg-purple-500/15 rounded-full blur-3xl" />
          <div className="absolute -bottom-32 left-1/4 w-72 h-72 bg-violet-600/20 rounded-full blur-3xl" />
          <div
            className="absolute inset-0 opacity-[0.03]"
            style={{
              backgroundImage: 'radial-gradient(circle at 1px 1px, white 1px, transparent 0)',
              backgroundSize: '32px 32px',
            }}
          />
        </div>

        <div className="relative z-10 flex flex-col h-full px-12 py-10">
          {/* Logo */}
          <div className="flex items-center gap-3">
            <div className="flex items-center justify-center w-11 h-11 rounded-2xl bg-violet-500 shadow-lg shadow-violet-500/30">
              <ShoppingBag className="w-6 h-6 text-white" />
            </div>
            <div>
              <p className="text-white font-bold text-lg leading-tight">Reteake CRM</p>
              <p className="text-violet-400 text-xs">Kiyim sotuv boshqaruv tizimi</p>
            </div>
          </div>

          {/* Main content */}
          <div className="flex-1 flex flex-col justify-center mt-8">
            <div className="mb-3">
              <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium bg-violet-500/20 text-violet-300 border border-violet-500/30">
                <Star className="w-3.5 h-3.5" />
                Kiyim do'konlari uchun #1 CRM
              </span>
            </div>

            <h1 className="text-4xl xl:text-5xl font-bold text-white leading-tight mb-4">
              Do'koningizni{' '}
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-violet-400 to-pink-400">
                aqlli boshqaring
              </span>
            </h1>

            <p className="text-slate-400 text-lg leading-relaxed mb-10 max-w-md">
              Mahsulotlar, mijozlar va sotuvlarni bitta platformada kuzating.
              Daromadingizni oshiring, vaqtingizni tejang.
            </p>

            {/* Features */}
            <div className="space-y-4 mb-12">
              {features.map(({ icon: Icon, text }) => (
                <div key={text} className="flex items-center gap-3">
                  <div className="flex items-center justify-center w-8 h-8 rounded-lg bg-violet-500/20 border border-violet-500/30 shrink-0">
                    <Icon className="w-4 h-4 text-violet-400" />
                  </div>
                  <span className="text-slate-300 text-sm">{text}</span>
                </div>
              ))}
            </div>

            {/* Stats */}
            <div className="flex gap-8 pt-8 border-t border-white/10">
              {stats.map(({ value, label }) => (
                <div key={label}>
                  <p className="text-2xl font-bold text-white">{value}</p>
                  <p className="text-slate-400 text-xs mt-0.5">{label}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Footer */}
          <p className="text-slate-600 text-xs">
            © 2025 Reteake CRM. Barcha huquqlar himoyalangan.
          </p>
        </div>
      </div>

      {/* Right panel — form */}
      <div className="flex-1 flex flex-col items-center justify-center bg-white relative overflow-y-auto">
        {/* Mobile logo */}
        <div className="lg:hidden flex items-center gap-2 mb-6 mt-6 px-6">
          <div className="flex items-center justify-center w-9 h-9 rounded-xl bg-violet-500 shrink-0">
            <ShoppingBag className="w-5 h-5 text-white" />
          </div>
          <div>
            <p className="font-bold text-slate-900 text-sm leading-tight">Reteake CRM</p>
            <p className="text-violet-500 text-xs">Kiyim sotuv boshqaruv tizimi</p>
          </div>
        </div>

        <div className="w-full max-w-[420px] px-4 sm:px-6 py-4 sm:py-8">
          {children}
        </div>
      </div>
    </div>
  );
}
