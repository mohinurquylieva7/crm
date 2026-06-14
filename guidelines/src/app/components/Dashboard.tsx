import { ShoppingCart, Users, Package, TrendingUp, AlertTriangle, ArrowRight, CheckCircle, Clock } from 'lucide-react';
import type { Product, Customer, Order } from '../types';
import type { PageKey } from '../App';

interface Props {
  products: Product[];
  customers: Customer[];
  orders: Order[];
  onNavigate: (p: PageKey) => void;
}

function fmt(n: number) {
  return n.toLocaleString('uz-UZ') + " so'm";
}

export function Dashboard({ products, customers, orders, onNavigate }: Props) {
  const today = new Date().toISOString().slice(0, 10);
  const todayOrders = orders.filter(o => o.date === today && o.status === 'completed');
  const todayRevenue = todayOrders.reduce((s, o) => s + o.total, 0);
  const todayProfit = todayOrders.reduce((s, o) => {
    const cost = o.items.reduce((c, i) => {
      const p = products.find(pr => pr.id === i.productId);
      return c + (p ? p.buyPrice * i.qty : 0);
    }, 0);
    return s + (o.total - cost);
  }, 0);
  const lowStock = products.filter(p => p.stock > 0 && p.stock <= p.minStock);
  const outOfStock = products.filter(p => p.stock === 0);
  const totalRevenue = orders.filter(o => o.status === 'completed').reduce((s, o) => s + o.total, 0);

  const recentOrders = [...orders].sort((a, b) => b.date.localeCompare(a.date)).slice(0, 5);

  const stats = [
    { label: "Bugungi sotuv", value: fmt(todayRevenue), sub: `${todayOrders.length} ta buyurtma`, icon: ShoppingCart, color: 'bg-blue-50 text-blue-600', iconBg: 'bg-blue-100' },
    { label: "Bugungi foyda", value: fmt(todayProfit), sub: "Xarid narxidan yuqori", icon: TrendingUp, color: 'bg-emerald-50 text-emerald-600', iconBg: 'bg-emerald-100' },
    { label: "Jami mijozlar", value: customers.length.toString(), sub: `Faol: ${customers.filter(c=>c.totalOrders>0).length}`, icon: Users, color: 'bg-violet-50 text-violet-600', iconBg: 'bg-violet-100' },
    { label: "Jami mahsulotlar", value: products.filter(p=>p.status!=='out_of_stock').length.toString(), sub: `Tugagan: ${outOfStock.length}`, icon: Package, color: 'bg-amber-50 text-amber-600', iconBg: 'bg-amber-100' },
  ];

  return (
    <div className="space-y-6">
      {/* Stats */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {stats.map((s, i) => {
          const Icon = s.icon;
          return (
            <div key={i} className="bg-white rounded-2xl border border-slate-100 p-4 sm:p-5">
              <div className="flex items-start justify-between mb-3">
                <div className={`w-10 h-10 rounded-xl ${s.iconBg} flex items-center justify-center`}>
                  <Icon className={`w-5 h-5 ${s.color.split(' ')[1]}`} />
                </div>
              </div>
              <p className="text-2xl font-bold text-slate-800 leading-tight">{s.value}</p>
              <p className="text-xs text-slate-400 mt-1">{s.label}</p>
              <p className="text-xs text-slate-500 mt-0.5">{s.sub}</p>
            </div>
          );
        })}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Recent orders */}
        <div className="lg:col-span-2 bg-white rounded-2xl border border-slate-100 p-5">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-bold text-slate-800">So'nggi buyurtmalar</h3>
            <button onClick={() => onNavigate('sales')} className="text-xs text-blue-600 flex items-center gap-1 hover:underline">
              Barchasi <ArrowRight className="w-3 h-3" />
            </button>
          </div>
          <div className="space-y-2">
            {recentOrders.map(o => (
              <div key={o.id} className="flex items-center gap-3 p-3 rounded-xl hover:bg-slate-50 transition-colors">
                <div className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 ${
                  o.status === 'completed' ? 'bg-emerald-100' : o.status === 'pending' ? 'bg-amber-100' : 'bg-red-100'
                }`}>
                  {o.status === 'completed' ? <CheckCircle className="w-4 h-4 text-emerald-600" /> :
                   o.status === 'pending' ? <Clock className="w-4 h-4 text-amber-600" /> :
                   <AlertTriangle className="w-4 h-4 text-red-600" />}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-slate-800 truncate">{o.customerName}</p>
                  <p className="text-xs text-slate-400">{o.items.length} mahsulot · {o.date}</p>
                </div>
                <div className="text-right shrink-0">
                  <p className="text-sm font-bold text-slate-800">{o.total.toLocaleString()}</p>
                  <p className="text-xs text-slate-400">so'm</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Alerts */}
        <div className="space-y-4">
          {/* Low stock */}
          <div className="bg-white rounded-2xl border border-slate-100 p-5">
            <div className="flex items-center justify-between mb-3">
              <h3 className="font-bold text-slate-800 text-sm">Stok ogohlantirish</h3>
              <button onClick={() => onNavigate('products')} className="text-xs text-blue-600 hover:underline">Ko'rish</button>
            </div>
            {lowStock.length === 0 && outOfStock.length === 0 ? (
              <p className="text-xs text-slate-400">Barcha mahsulotlar yetarli</p>
            ) : (
              <div className="space-y-2">
                {outOfStock.map(p => (
                  <div key={p.id} className="flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-red-500 shrink-0" />
                    <span className="text-xs text-slate-700 truncate flex-1">{p.name}</span>
                    <span className="text-xs text-red-600 font-medium shrink-0">0 ta</span>
                  </div>
                ))}
                {lowStock.map(p => (
                  <div key={p.id} className="flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-amber-500 shrink-0" />
                    <span className="text-xs text-slate-700 truncate flex-1">{p.name}</span>
                    <span className="text-xs text-amber-600 font-medium shrink-0">{p.stock} ta</span>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Top customers */}
          <div className="bg-white rounded-2xl border border-slate-100 p-5">
            <div className="flex items-center justify-between mb-3">
              <h3 className="font-bold text-slate-800 text-sm">Top mijozlar</h3>
              <button onClick={() => onNavigate('customers')} className="text-xs text-blue-600 hover:underline">Ko'rish</button>
            </div>
            <div className="space-y-2">
              {[...customers].sort((a,b)=>b.totalSpent-a.totalSpent).slice(0,4).map(c => (
                <div key={c.id} className="flex items-center gap-2">
                  <div className="w-7 h-7 rounded-full bg-gradient-to-br from-violet-400 to-blue-500 flex items-center justify-center text-white text-xs font-bold shrink-0">
                    {c.firstName[0]}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-xs font-medium text-slate-700 truncate">{c.firstName} {c.lastName}</p>
                    <p className="text-xs text-slate-400">{c.totalOrders} buyurtma</p>
                  </div>
                  <span className="text-xs font-bold text-slate-700 shrink-0">{(c.totalSpent/1000).toFixed(0)}k</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
