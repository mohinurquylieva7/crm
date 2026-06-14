import { useState } from 'react';
import { Save, Building, Phone, MapPin, Globe, Percent, CheckCircle, CreditCard } from 'lucide-react';
import type { StoreSettings } from '../types';
import { useLanguage } from '../context/LanguageContext';
import type { Lang } from '../i18n/translations';

interface Props { settings: StoreSettings; onSave: (s: StoreSettings) => void; }

const planConfig = {
  free: { label: 'Bepul', color: 'bg-slate-100 text-slate-600', price: '0' },
  starter: { label: 'Starter', color: 'bg-blue-100 text-blue-700', price: '99,000' },
  pro: { label: 'Pro', color: 'bg-violet-100 text-violet-700', price: '299,000' },
  enterprise: { label: 'Enterprise', color: 'bg-amber-100 text-amber-700', price: 'Kelishuv' },
};

export function Settings({ settings, onSave }: Props) {
  const [form, setForm] = useState({ ...settings });
  const [saved, setSaved] = useState(false);
  const [section, setSection] = useState('general');
  const { t, setLang } = useLanguage();

  const sections = [
    { key: 'general', label: t('general'), icon: Building },
    { key: 'notifications', label: t('notificationsSettings'), icon: Phone },
    { key: 'subscription', label: t('subscription'), icon: CreditCard },
  ];

  const handleSave = () => {
    onSave(form);
    if (form.language === 'uz' || form.language === 'ru' || form.language === 'en') {
      setLang(form.language as Lang);
    }
    setSaved(true);
    setTimeout(() => setSaved(false), 3000);
  };

  return (
    <div className="flex flex-col lg:flex-row gap-4 lg:gap-6">
      {/* Nav */}
      <div className="lg:w-48 shrink-0">
        <div className="flex lg:hidden gap-1 overflow-x-auto pb-1 bg-white rounded-2xl border border-slate-100 p-1">
          {sections.map(s => {
            const Icon = s.icon;
            return (
              <button key={s.key} onClick={() => setSection(s.key)}
                className={`flex items-center gap-1.5 px-3 py-2 rounded-xl text-xs font-medium whitespace-nowrap transition-colors shrink-0 ${section===s.key?'bg-violet-600 text-white':'text-slate-600 hover:bg-slate-50'}`}>
                <Icon className="w-3.5 h-3.5" />{s.label}
              </button>
            );
          })}
        </div>
        <div className="hidden lg:block bg-white rounded-2xl border border-slate-100 overflow-hidden">
          {sections.map(s => {
            const Icon = s.icon;
            return (
              <button key={s.key} onClick={() => setSection(s.key)}
                className={`w-full flex items-center gap-3 px-4 py-3 text-sm font-medium transition-colors border-b border-slate-50 last:border-0 ${section===s.key?'bg-violet-50 text-violet-600':'text-slate-600 hover:bg-slate-50'}`}>
                <Icon className="w-4 h-4 shrink-0" />{s.label}
              </button>
            );
          })}
        </div>
      </div>

      <div className="flex-1 space-y-5">
        {section === 'general' && (
          <div className="bg-white rounded-2xl border border-slate-100 p-6 space-y-5">
            <div>
              <h3 className="font-bold text-slate-800 mb-1">Do'kon ma'lumotlari</h3>
              <p className="text-xs text-slate-400">Asosiy ma'lumotlarni yangilang</p>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="sm:col-span-2">
                <label className="text-xs font-semibold text-slate-600 block mb-1.5">Do'kon nomi</label>
                <div className="relative">
                  <Building className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                  <input value={form.name} onChange={e=>setForm(f=>({...f,name:e.target.value}))}
                    className="w-full pl-9 pr-4 py-2.5 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-violet-500" />
                </div>
              </div>
              <div>
                <label className="text-xs font-semibold text-slate-600 block mb-1.5">{t('phone')}</label>
                <div className="relative">
                  <Phone className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                  <input value={form.phone} onChange={e=>setForm(f=>({...f,phone:e.target.value}))}
                    className="w-full pl-9 pr-4 py-2.5 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-violet-500" />
                </div>
              </div>
              <div>
                <label className="text-xs font-semibold text-slate-600 block mb-1.5">{t('language')}</label>
                <div className="relative">
                  <Globe className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                  <select value={form.language} onChange={e=>setForm(f=>({...f,language:e.target.value as any}))}
                    className="w-full pl-9 pr-4 py-2.5 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-violet-500 bg-white">
                    <option value="uz">O'zbekcha</option>
                    <option value="ru">Русский</option>
                    <option value="en">English</option>
                  </select>
                </div>
              </div>
              <div className="sm:col-span-2">
                <label className="text-xs font-semibold text-slate-600 block mb-1.5">{t('address')}</label>
                <div className="relative">
                  <MapPin className="absolute left-3 top-3 w-4 h-4 text-slate-400" />
                  <textarea value={form.address} onChange={e=>setForm(f=>({...f,address:e.target.value}))}
                    className="w-full pl-9 pr-4 py-2.5 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-violet-500 resize-none" rows={2} />
                </div>
              </div>
              <div>
                <label className="text-xs font-semibold text-slate-600 block mb-1.5">{t('currency')}</label>
                <select value={form.currency} onChange={e=>setForm(f=>({...f,currency:e.target.value}))}
                  className="w-full px-3 py-2.5 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-violet-500 bg-white">
                  <option value="UZS">UZS — So'm</option>
                  <option value="USD">USD — Dollar</option>
                  <option value="RUB">RUB — Rubl</option>
                </select>
              </div>
              <div>
                <label className="text-xs font-semibold text-slate-600 block mb-1.5">Soliq (%)</label>
                <div className="relative">
                  <Percent className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                  <input type="number" min={0} max={100} value={form.taxPercent} onChange={e=>setForm(f=>({...f,taxPercent:+e.target.value}))}
                    className="w-full pl-9 pr-4 py-2.5 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-violet-500" />
                </div>
              </div>
              <div className="sm:col-span-2">
                <label className="text-xs font-semibold text-slate-600 block mb-1.5">Chek pastki matni</label>
                <input value={form.receiptFooter} onChange={e=>setForm(f=>({...f,receiptFooter:e.target.value}))}
                  className="w-full px-3 py-2.5 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-violet-500" />
              </div>
            </div>
          </div>
        )}

        {section === 'notifications' && (
          <div className="bg-white rounded-2xl border border-slate-100 p-6 space-y-4">
            <div>
              <h3 className="font-bold text-slate-800 mb-1">Bildirishnomalar</h3>
              <p className="text-xs text-slate-400">Qaysi hodisalar uchun bildirishnoma olish kerakligi</p>
            </div>
            {[
              { label: "Stok kamligi ogohlantirishi", desc: "Mahsulot minimal miqdordan kamaysa" },
              { label: "Yangi buyurtma", desc: "Har yangi sotuv qo'shilganda" },
              { label: "Oylik hisobot", desc: "Har oy oxirida avtomatik hisobot" },
              { label: "Katta chegirma", desc: "20%dan yuqori chegirma berilganda" },
            ].map((item, i) => (
              <div key={i} className="flex items-center justify-between p-4 rounded-xl border border-slate-100 hover:bg-slate-50">
                <div>
                  <p className="text-sm font-medium text-slate-800">{item.label}</p>
                  <p className="text-xs text-slate-400 mt-0.5">{item.desc}</p>
                </div>
                <div className="relative w-10 h-5 rounded-full cursor-pointer bg-violet-600">
                  <div className="absolute top-0.5 w-4 h-4 bg-white rounded-full shadow translate-x-5" />
                </div>
              </div>
            ))}
          </div>
        )}

        {section === 'subscription' && (
          <div className="bg-white rounded-2xl border border-slate-100 p-6 space-y-5">
            <div>
              <h3 className="font-bold text-slate-800 mb-1">Obuna rejasi</h3>
              <p className="text-xs text-slate-400">Joriy obuna holati</p>
            </div>
            <div className="bg-violet-50 rounded-2xl p-4 flex items-center gap-4">
              <div className="w-12 h-12 rounded-xl bg-violet-600 flex items-center justify-center">
                <CreditCard className="w-6 h-6 text-white" />
              </div>
              <div>
                <p className="font-bold text-slate-800">Pro rejasi faol</p>
                <p className="text-sm text-slate-500 mt-0.5">Amal qilish muddati: {settings.subscriptionExpiry}</p>
              </div>
              <span className="ml-auto text-xs px-3 py-1 bg-violet-100 text-violet-700 rounded-full font-medium">Faol</span>
            </div>
            <div className="grid grid-cols-2 gap-3">
              {Object.entries(planConfig).map(([key, plan]) => (
                <div key={key} className={`rounded-2xl border-2 p-4 cursor-pointer ${settings.subscriptionPlan===key?'border-violet-500 bg-violet-50':'border-slate-100 hover:border-slate-200'}`}>
                  <div className="flex justify-between items-start mb-2">
                    <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${plan.color}`}>{plan.label}</span>
                    {settings.subscriptionPlan===key&&<CheckCircle className="w-4 h-4 text-violet-500" />}
                  </div>
                  <p className="text-xl font-bold text-slate-800">{plan.price}</p>
                  <p className="text-xs text-slate-400">so'm/oy</p>
                </div>
              ))}
            </div>
          </div>
        )}

        <div className="flex justify-end">
          <button onClick={handleSave} className={`flex items-center gap-2 px-6 py-2.5 rounded-xl text-sm font-medium transition-all ${saved?'bg-emerald-500 text-white':'bg-violet-600 hover:bg-violet-700 text-white'}`}>
            {saved?<><CheckCircle className="w-4 h-4" /> Saqlandi!</>:<><Save className="w-4 h-4" /> {t('save')}</>}
          </button>
        </div>
      </div>
    </div>
  );
}
