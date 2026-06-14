import { useState } from 'react';
import { useForm } from 'react-hook-form';
import {
  Eye, EyeOff, Loader2, ArrowRight, AlertCircle,
  Mail, Lock, User, Phone, Building2, CheckCircle2,
} from 'lucide-react';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { cn } from '../ui/utils';
import { useAuth, type RegisterData } from '../../context/AuthContext';
import { AuthLayout } from './AuthLayout';

interface SignUpForm extends RegisterData {
  confirmPassword: string;
  agreeTerms: boolean;
}

interface SignUpProps {
  onNavigateToSignIn: () => void;
}

function PasswordStrength({ password }: { password: string }) {
  const checks = [
    { label: '8+ belgi', ok: password.length >= 8 },
    { label: 'Katta harf', ok: /[A-Z]/.test(password) },
    { label: 'Kichik harf', ok: /[a-z]/.test(password) },
    { label: 'Raqam', ok: /\d/.test(password) },
  ];
  const score = checks.filter(c => c.ok).length;
  const colors = ['bg-slate-200', 'bg-red-400', 'bg-orange-400', 'bg-yellow-400', 'bg-green-500'];
  const labels = ['', 'Zaif', "O'rtacha", 'Yaxshi', 'Kuchli'];

  if (!password) return null;

  return (
    <div className="mt-2 space-y-2">
      <div className="flex gap-1">
        {[0, 1, 2, 3].map(i => (
          <div
            key={i}
            className={cn(
              'h-1 flex-1 rounded-full transition-all duration-300',
              i < score ? colors[score] : 'bg-slate-100',
            )}
          />
        ))}
      </div>
      <div className="flex items-center justify-between">
        <div className="flex gap-3 flex-wrap">
          {checks.map(({ label, ok }) => (
            <span
              key={label}
              className={cn(
                'text-xs flex items-center gap-1 transition-colors',
                ok ? 'text-green-600' : 'text-slate-400',
              )}
            >
              <CheckCircle2 className={cn('w-3 h-3', ok ? 'text-green-500' : 'text-slate-300')} />
              {label}
            </span>
          ))}
        </div>
        {score > 0 && (
          <span className={cn('text-xs font-medium', score >= 3 ? 'text-green-600' : 'text-orange-500')}>
            {labels[score]}
          </span>
        )}
      </div>
    </div>
  );
}

export function SignUp({ onNavigateToSignIn }: SignUpProps) {
  const { register: registerUser } = useAuth();
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);
  const [serverError, setServerError] = useState('');
  const [isSuccess, setIsSuccess] = useState(false);

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors, isSubmitting },
  } = useForm<SignUpForm>({
    defaultValues: {
      fullName: '', email: '', password: '', confirmPassword: '',
      centerName: '', phone: '', agreeTerms: false,
    },
  });

  const passwordValue = watch('password', '');

  const onSubmit = async (data: SignUpForm) => {
    setServerError('');
    try {
      await registerUser({
        fullName: data.fullName,
        email: data.email,
        password: data.password,
        centerName: data.centerName,
        phone: data.phone,
      });
      setIsSuccess(true);
    } catch (err) {
      setServerError(err instanceof Error ? err.message : 'Xatolik yuz berdi');
    }
  };

  return (
    <AuthLayout>
      <div
        className="animate-in fade-in slide-in-from-bottom-4 duration-500"
        style={{ animationFillMode: 'both' }}
      >
        {/* Header */}
        <div className="mb-7">
          <h2 className="text-2xl font-bold text-slate-900 mb-1">Hisob yarating</h2>
          <p className="text-slate-500 text-sm">O'quv markazingizni bepul boshlang</p>
        </div>

        {/* Server error */}
        {serverError && (
          <div className="flex items-start gap-3 p-3.5 mb-4 rounded-xl bg-red-50 border border-red-200 text-red-700 text-sm animate-in fade-in duration-200">
            <AlertCircle className="w-4 h-4 mt-0.5 shrink-0" />
            <span>{serverError}</span>
          </div>
        )}

        {/* Success */}
        {isSuccess && (
          <div className="flex items-center gap-3 p-3.5 mb-4 rounded-xl bg-green-50 border border-green-200 text-green-700 text-sm animate-in fade-in duration-200">
            <CheckCircle2 className="w-4 h-4 text-green-500 shrink-0" />
            <span>Muvaffaqiyatli ro'yxatdan o'tdingiz! Kirmoqdasiz...</span>
          </div>
        )}

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-3.5" noValidate>
          {/* Full name + center name */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div className="space-y-1.5">
              <Label htmlFor="signup-fullname" className="text-slate-700 font-medium text-sm">
                To'liq ism
              </Label>
              <div className="relative">
                <User className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400 pointer-events-none" />
                <Input
                  id="signup-fullname"
                  placeholder="Sardor Toshmatov"
                  autoComplete="name"
                  className={cn(
                    'pl-10 h-11 text-sm border-slate-200 bg-slate-50 focus:bg-white transition-colors',
                    errors.fullName && 'border-red-400 bg-red-50',
                  )}
                  {...register('fullName', {
                    required: "Ism majburiy",
                    minLength: { value: 3, message: 'Kamida 3 ta belgi' },
                  })}
                />
              </div>
              {errors.fullName && (
                <p className="text-xs text-red-500 flex items-center gap-1">
                  <AlertCircle className="w-3 h-3" />
                  {errors.fullName.message}
                </p>
              )}
            </div>

            <div className="space-y-1.5">
              <Label htmlFor="signup-center" className="text-slate-700 font-medium text-sm">
                Markaz nomi
              </Label>
              <div className="relative">
                <Building2 className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400 pointer-events-none" />
                <Input
                  id="signup-center"
                  placeholder="Istiqbol IELTS"
                  className={cn(
                    'pl-10 h-11 text-sm border-slate-200 bg-slate-50 focus:bg-white transition-colors',
                    errors.centerName && 'border-red-400 bg-red-50',
                  )}
                  {...register('centerName', { required: 'Markaz nomi majburiy' })}
                />
              </div>
              {errors.centerName && (
                <p className="text-xs text-red-500 flex items-center gap-1">
                  <AlertCircle className="w-3 h-3" />
                  {errors.centerName.message}
                </p>
              )}
            </div>
          </div>

          {/* Email */}
          <div className="space-y-1.5">
            <Label htmlFor="signup-email" className="text-slate-700 font-medium text-sm">
              Email manzil
            </Label>
            <div className="relative">
              <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400 pointer-events-none" />
              <Input
                id="signup-email"
                type="email"
                placeholder="siz@markaz.uz"
                autoComplete="email"
                className={cn(
                  'pl-10 h-11 text-sm border-slate-200 bg-slate-50 focus:bg-white transition-colors',
                  errors.email && 'border-red-400 bg-red-50',
                )}
                {...register('email', {
                  required: 'Email majburiy',
                  pattern: {
                    value: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
                    message: "To'g'ri email kiriting",
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

          {/* Phone */}
          <div className="space-y-1.5">
            <Label htmlFor="signup-phone" className="text-slate-700 font-medium text-sm">
              Telefon raqam
            </Label>
            <div className="relative">
              <Phone className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400 pointer-events-none" />
              <Input
                id="signup-phone"
                type="tel"
                placeholder="+998 90 123 45 67"
                autoComplete="tel"
                className={cn(
                  'pl-10 h-11 text-sm border-slate-200 bg-slate-50 focus:bg-white transition-colors',
                  errors.phone && 'border-red-400 bg-red-50',
                )}
                {...register('phone', {
                  required: 'Telefon raqam majburiy',
                  pattern: {
                    value: /^[\+\d\s\-()]{9,15}$/,
                    message: "To'g'ri telefon raqam kiriting",
                  },
                })}
              />
            </div>
            {errors.phone && (
              <p className="text-xs text-red-500 flex items-center gap-1">
                <AlertCircle className="w-3 h-3" />
                {errors.phone.message}
              </p>
            )}
          </div>

          {/* Password */}
          <div className="space-y-1.5">
            <Label htmlFor="signup-password" className="text-slate-700 font-medium text-sm">
              Parol
            </Label>
            <div className="relative">
              <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400 pointer-events-none" />
              <Input
                id="signup-password"
                type={showPassword ? 'text' : 'password'}
                placeholder="Kuchli parol yarating"
                autoComplete="new-password"
                className={cn(
                  'pl-10 pr-11 h-11 text-sm border-slate-200 bg-slate-50 focus:bg-white transition-colors',
                  errors.password && 'border-red-400 bg-red-50',
                )}
                {...register('password', {
                  required: 'Parol majburiy',
                  minLength: { value: 8, message: 'Kamida 8 ta belgi' },
                  validate: {
                    hasUpper: v => /[A-Z]/.test(v) || 'Katta harf kerak',
                    hasNumber: v => /\d/.test(v) || 'Raqam kerak',
                  },
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
            {errors.password ? (
              <p className="text-xs text-red-500 flex items-center gap-1">
                <AlertCircle className="w-3 h-3" />
                {errors.password.message}
              </p>
            ) : null}
            <PasswordStrength password={passwordValue} />
          </div>

          {/* Confirm password */}
          <div className="space-y-1.5">
            <Label htmlFor="signup-confirm" className="text-slate-700 font-medium text-sm">
              Parolni tasdiqlang
            </Label>
            <div className="relative">
              <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400 pointer-events-none" />
              <Input
                id="signup-confirm"
                type={showConfirm ? 'text' : 'password'}
                placeholder="Parolni qayta kiriting"
                autoComplete="new-password"
                className={cn(
                  'pl-10 pr-11 h-11 text-sm border-slate-200 bg-slate-50 focus:bg-white transition-colors',
                  errors.confirmPassword && 'border-red-400 bg-red-50',
                )}
                {...register('confirmPassword', {
                  required: 'Parolni tasdiqlang',
                  validate: v => v === passwordValue || 'Parollar mos kelmadi',
                })}
              />
              <button
                type="button"
                onClick={() => setShowConfirm(v => !v)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 transition-colors"
              >
                {showConfirm ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
            </div>
            {errors.confirmPassword && (
              <p className="text-xs text-red-500 flex items-center gap-1">
                <AlertCircle className="w-3 h-3" />
                {errors.confirmPassword.message}
              </p>
            )}
          </div>

          {/* Terms */}
          <div className="space-y-1">
            <div className="flex items-start gap-2.5 pt-1">
              <input
                id="signup-terms"
                type="checkbox"
                className="w-4 h-4 mt-0.5 rounded border-slate-300 accent-blue-600 cursor-pointer shrink-0"
                {...register('agreeTerms', { required: "Shartlarga rozilik majburiy" })}
              />
              <Label htmlFor="signup-terms" className="text-slate-600 text-sm font-normal leading-relaxed cursor-pointer">
                Men{' '}
                <button type="button" className="text-violet-600 hover:underline font-medium">
                  Foydalanish shartlari
                </button>{' '}
                va{' '}
                <button type="button" className="text-violet-600 hover:underline font-medium">
                  Maxfiylik siyosati
                </button>
                ga roziman
              </Label>
            </div>
            {errors.agreeTerms && (
              <p className="text-xs text-red-500 flex items-center gap-1 pl-6">
                <AlertCircle className="w-3 h-3" />
                {errors.agreeTerms.message}
              </p>
            )}
          </div>

          {/* Submit */}
          <Button
            type="submit"
            className="w-full h-11 bg-violet-600 hover:bg-violet-700 text-white font-medium rounded-xl shadow-sm shadow-blue-500/20 transition-all duration-200 mt-1"
            disabled={isSubmitting || isSuccess}
          >
            {isSubmitting ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                Ro'yxatdan o'tilmoqda...
              </>
            ) : (
              <>
                Hisob yaratish
                <ArrowRight className="w-4 h-4" />
              </>
            )}
          </Button>
        </form>

        {/* Sign in link */}
        <p className="text-center text-sm text-slate-500 mt-6">
          Akkauntingiz bormi?{' '}
          <button
            type="button"
            onClick={onNavigateToSignIn}
            className="text-violet-600 hover:text-violet-700 font-semibold transition-colors"
          >
            Kirish
          </button>
        </p>
      </div>
    </AuthLayout>
  );
}
