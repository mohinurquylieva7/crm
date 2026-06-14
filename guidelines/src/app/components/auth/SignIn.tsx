import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { Eye, EyeOff, Loader2, ArrowRight, AlertCircle, Mail, Lock } from 'lucide-react';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { cn } from '../ui/utils';
import { useAuth } from '../../context/AuthContext';
import { AuthLayout } from './AuthLayout';

interface SignInForm {
  email: string;
  password: string;
  remember: boolean;
}

interface SignInProps {
  onNavigateToSignUp: () => void;
}

export function SignIn({ onNavigateToSignUp }: SignInProps) {
  const { login } = useAuth();
  const [showPassword, setShowPassword] = useState(false);
  const [serverError, setServerError] = useState('');
  const [isSuccess, setIsSuccess] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
    setValue,
  } = useForm<SignInForm>({
    defaultValues: { email: '', password: '', remember: true },
  });

  const onSubmit = async (data: SignInForm) => {
    setServerError('');
    try {
      await login(data.email, data.password, data.remember);
      setIsSuccess(true);
    } catch (err) {
      setServerError(err instanceof Error ? err.message : 'Xatolik yuz berdi');
    }
  };

  const fillDemo = (email: string, password: string) => {
    setValue('email', email);
    setValue('password', password);
  };

  return (
    <AuthLayout>
      <div
        className="animate-in fade-in slide-in-from-bottom-4 duration-500"
        style={{ animationFillMode: 'both' }}
      >
        {/* Header */}
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-slate-900 mb-1">Xush kelibsiz!</h2>
          <p className="text-slate-500 text-sm">Akkauntingizga kiring</p>
        </div>

        {/* Server error */}
        {serverError && (
          <div className="flex items-start gap-3 p-3.5 mb-5 rounded-xl bg-red-50 border border-red-200 text-red-700 text-sm animate-in fade-in duration-200">
            <AlertCircle className="w-4 h-4 mt-0.5 shrink-0" />
            <span>{serverError}</span>
          </div>
        )}

        {/* Success */}
        {isSuccess && (
          <div className="flex items-center gap-3 p-3.5 mb-5 rounded-xl bg-green-50 border border-green-200 text-green-700 text-sm animate-in fade-in duration-200">
            <span className="text-green-500">✓</span>
            <span>Muvaffaqiyatli kirdingiz! Yo'naltirilmoqda...</span>
          </div>
        )}

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4" noValidate>
          {/* Email */}
          <div className="space-y-1.5">
            <Label htmlFor="signin-email" className="text-slate-700 font-medium">
              Email manzil
            </Label>
            <div className="relative">
              <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400 pointer-events-none" />
              <Input
                id="signin-email"
                type="email"
                placeholder="admin@fashion.uz"
                autoComplete="email"
                className={cn(
                  'pl-10 h-11 text-sm border-slate-200 bg-slate-50 focus:bg-white transition-colors',
                  errors.email && 'border-red-400 bg-red-50 focus:border-red-400',
                )}
                {...register('email', {
                  required: 'Email kiritish majburiy',
                  pattern: {
                    value: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
                    message: "To'g'ri email manzil kiriting",
                  },
                })}
              />
            </div>
            {errors.email && (
              <p className="text-xs text-red-500 flex items-center gap-1">
                <AlertCircle className="w-3 h-3" />
                {errors.email.message}
              </p>
            )}
          </div>

          {/* Password */}
          <div className="space-y-1.5">
            <div className="flex items-center justify-between">
              <Label htmlFor="signin-password" className="text-slate-700 font-medium">
                Parol
              </Label>
              <button
                type="button"
                className="text-xs text-violet-600 hover:text-violet-700 font-medium transition-colors"
              >
                Parolni unutdingizmi?
              </button>
            </div>
            <div className="relative">
              <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400 pointer-events-none" />
              <Input
                id="signin-password"
                type={showPassword ? 'text' : 'password'}
                placeholder="••••••••"
                autoComplete="current-password"
                className={cn(
                  'pl-10 pr-11 h-11 text-sm border-slate-200 bg-slate-50 focus:bg-white transition-colors',
                  errors.password && 'border-red-400 bg-red-50 focus:border-red-400',
                )}
                {...register('password', {
                  required: 'Parol kiritish majburiy',
                  minLength: { value: 6, message: "Parol kamida 6 ta belgi bo'lishi kerak" },
                })}
              />
              <button
                type="button"
                onClick={() => setShowPassword(v => !v)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 transition-colors"
              >
                {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
            </div>
            {errors.password && (
              <p className="text-xs text-red-500 flex items-center gap-1">
                <AlertCircle className="w-3 h-3" />
                {errors.password.message}
              </p>
            )}
          </div>

          {/* Remember me */}
          <div className="flex items-center gap-2.5">
            <input
              id="signin-remember"
              type="checkbox"
              className="w-4 h-4 rounded border-slate-300 text-violet-600 accent-violet-600 cursor-pointer"
              {...register('remember')}
            />
            <Label htmlFor="signin-remember" className="text-slate-600 text-sm font-normal cursor-pointer">
              Meni eslab qol
            </Label>
          </div>

          {/* Submit */}
          <Button
            type="submit"
            className="w-full h-11 bg-violet-600 hover:bg-violet-700 text-white font-medium rounded-xl shadow-sm shadow-blue-500/20 transition-all duration-200 mt-2"
            disabled={isSubmitting || isSuccess}
          >
            {isSubmitting ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                Kirilmoqda...
              </>
            ) : (
              <>
                Kirish
                <ArrowRight className="w-4 h-4" />
              </>
            )}
          </Button>
        </form>

        {/* Divider */}
        <div className="flex items-center gap-3 my-6">
          <div className="flex-1 h-px bg-slate-100" />
          <span className="text-slate-400 text-xs">yoki demo bilan kiring</span>
          <div className="flex-1 h-px bg-slate-100" />
        </div>

        {/* Demo accounts */}
        <div className="grid grid-cols-2 gap-2 mb-6">
          <button
            type="button"
            onClick={() => fillDemo('admin@fashion.uz', 'Admin1234!')}
            className="flex flex-col items-start p-3 rounded-xl border border-slate-200 hover:border-violet-300 hover:bg-violet-50 transition-all duration-200 text-left group"
          >
            <span className="text-xs font-semibold text-slate-700 group-hover:text-violet-700">Admin</span>
            <span className="text-xs text-slate-400 mt-0.5">admin@fashion.uz</span>
          </button>
          <button
            type="button"
            onClick={() => fillDemo('seller@fashion.uz', 'Seller1234!')}
            className="flex flex-col items-start p-3 rounded-xl border border-slate-200 hover:border-violet-300 hover:bg-violet-50 transition-all duration-200 text-left group"
          >
            <span className="text-xs font-semibold text-slate-700 group-hover:text-violet-700">Sotuvchi</span>
            <span className="text-xs text-slate-400 mt-0.5">seller@fashion.uz</span>
          </button>
        </div>

        {/* Sign up link */}
        <p className="text-center text-sm text-slate-500">
          Akkauntingiz yo'qmi?{' '}
          <button
            type="button"
            onClick={onNavigateToSignUp}
            className="text-violet-600 hover:text-violet-700 font-semibold transition-colors"
          >
            Ro'yxatdan o'ting
          </button>
        </p>
      </div>
    </AuthLayout>
  );
}
