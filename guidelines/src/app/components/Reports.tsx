import { TrendingUp, ShoppingCart, Users, Package } from 'lucide-react';
import type { Order, Product, Customer } from '../types';

interface Props { orders: Order[]; products: Product[]; customers: Customer[]; }

export function Reports({ orders, products, customers }: Props) {
  const completed = orders.filter(o=>o.status==='completed');
  const totalRevenue = completed.reduce((s,o)=>s+o.total,0);
  const totalCost = completed.reduce((s,o)=>{
    return s + o.items.reduce((c,i)=>{
      const p = products.find(pr=>pr.id===i.productId);
      return c+(p?p.buyPrice*i.qty:0);
    },0);
  },0);
  const totalProfit = totalRevenue - totalCost;

  // Sales by method
  const byMethod = { cash:0, card:0, transfer:0 };
  completed.forEach(o=>{ byMethod[o.method] += o.total; });

  // Top products
  const prodSales: Record<string,{name:string;qty:number;revenue:number}> = {};
  completed.forEach(o=>o.items.forEach(i=>{
    if (!prodSales[i.productId]) prodSales[i.productId]={name:i.productName,qty:0,revenue:0};
    prodSales[i.productId].qty+=i.qty;
    prodSales[i.productId].revenue+=i.unitPrice*i.qty;
  }));
  const topProds = Object.values(prodSales).sort((a,b)=>b.revenue-a.revenue).slice(0,5);

  // By date (last 7 days)
  const days: {date:string;total:number}[] = [];
  for(let i=6;i>=0;i--){
    const d = new Date(); d.setDate(d.getDate()-i);
    const ds = d.toISOString().slice(0,10);
    const t = completed.filter(o=>o.date===ds).reduce((s,o)=>s+o.total,0);
    days.push({date:ds.slice(5),total:t});
  }
  const maxDay = Math.max(...days.map(d=>d.total),1);

  // Categories
  const catSales: Record<string,number> = {};
  completed.forEach(o=>o.items.forEach(i=>{
    const p = products.find(pr=>pr.id===i.productId);
    if(p){ catSales[p.category]=(catSales[p.category]||0)+i.unitPrice*i.qty; }
  }));
  const cats = Object.entries(catSales).sort((a,b)=>b[1]-a[1]);
  const maxCat = Math.max(...cats.map(c=>c[1]),1);

  return (
    <div className="space-y-5">
      {/* KPIs */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {[
          { label:'Jami daromad', value:`${(totalRevenue/1000000).toFixed(2)} mln`, sub: `${completed.length} ta sotuv`, icon: TrendingUp, color:'text-blue-600', bg:'bg-blue-100' },
          { label:'Sof foyda', value:`${(totalProfit/1000000).toFixed(2)} mln`, sub:`Margin: ${totalRevenue?Math.round(totalProfit/totalRevenue*100):0}%`, icon: TrendingUp, color:'text-emerald-600', bg:'bg-emerald-100' },
          { label:'Sotuvlar soni', value:completed.length.toString(), sub:`O'rtacha: ${completed.length?Math.round(totalRevenue/completed.length).toLocaleString():0} so'm`, icon: ShoppingCart, color:'text-violet-600', bg:'bg-violet-100' },
          { label:'Faol mijozlar', value:customers.filter(c=>c.totalOrders>0).length.toString(), sub:`Jami: ${customers.length}`, icon: Users, color:'text-amber-600', bg:'bg-amber-100' },
        ].map((s,i)=>{
          const Icon = s.icon;
          return (
            <div key={i} className="bg-white rounded-2xl border border-slate-100 p-5">
              <div className={`w-9 h-9 rounded-xl ${s.bg} flex items-center justify-center mb-3`}>
                <Icon className={`w-4 h-4 ${s.color}`} />
              </div>
              <p className="text-xl font-bold text-slate-800">{s.value}</p>
              <p className="text-xs text-slate-400 mt-0.5">{s.label}</p>
              <p className="text-xs text-slate-500 mt-0.5">{s.sub}</p>
            </div>
          );
        })}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        {/* Daily chart */}
        <div className="bg-white rounded-2xl border border-slate-100 p-5">
          <h3 className="font-bold text-slate-800 mb-4">So'nggi 7 kun</h3>
          <div className="flex items-end gap-2 h-32">
            {days.map(d=>(
              <div key={d.date} className="flex-1 flex flex-col items-center gap-1">
                <div className="w-full bg-violet-100 rounded-t-lg relative" style={{height:`${Math.max(4,(d.total/maxDay)*100)}%`}}>
                  <div className="absolute inset-0 bg-violet-500 rounded-t-lg opacity-80" />
                </div>
                <p className="text-xs text-slate-400 leading-tight">{d.date}</p>
                <p className="text-xs text-slate-600 font-medium">{d.total>0?(d.total/1000).toFixed(0)+'k':'-'}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Top products */}
        <div className="bg-white rounded-2xl border border-slate-100 p-5">
          <h3 className="font-bold text-slate-800 mb-4">Top mahsulotlar</h3>
          <div className="space-y-3">
            {topProds.map((p,i)=>(
              <div key={p.name} className="flex items-center gap-3">
                <span className="text-xs font-bold text-slate-400 w-4 shrink-0">{i+1}</span>
                <div className="flex-1 min-w-0">
                  <div className="flex justify-between items-center mb-0.5">
                    <p className="text-xs font-medium text-slate-700 truncate">{p.name}</p>
                    <p className="text-xs text-slate-500 shrink-0 ml-2">{p.qty} ta</p>
                  </div>
                  <div className="w-full bg-slate-100 rounded-full h-1.5">
                    <div className="bg-violet-500 h-1.5 rounded-full" style={{width:`${(p.revenue/topProds[0].revenue)*100}%`}} />
                  </div>
                </div>
                <p className="text-xs font-bold text-slate-700 shrink-0">{(p.revenue/1000).toFixed(0)}k</p>
              </div>
            ))}
            {topProds.length===0&&<p className="text-sm text-slate-400">Ma'lumot yo'q</p>}
          </div>
        </div>

        {/* Payment methods */}
        <div className="bg-white rounded-2xl border border-slate-100 p-5">
          <h3 className="font-bold text-slate-800 mb-4">To'lov usullari</h3>
          <div className="space-y-3">
            {[{key:'cash',label:"Naqd"},{key:'card',label:"Karta"},{key:'transfer',label:"O'tkazma"}].map(m=>{
              const val = byMethod[m.key as keyof typeof byMethod];
              const pct = totalRevenue ? Math.round(val/totalRevenue*100) : 0;
              return (
                <div key={m.key} className="flex items-center gap-3">
                  <p className="text-xs font-medium text-slate-600 w-16 shrink-0">{m.label}</p>
                  <div className="flex-1 bg-slate-100 rounded-full h-2">
                    <div className="bg-blue-500 h-2 rounded-full" style={{width:`${pct}%`}} />
                  </div>
                  <p className="text-xs text-slate-600 w-8 text-right shrink-0">{pct}%</p>
                  <p className="text-xs font-bold text-slate-700 w-16 text-right shrink-0">{(val/1000).toFixed(0)}k</p>
                </div>
              );
            })}
          </div>
        </div>

        {/* Categories */}
        <div className="bg-white rounded-2xl border border-slate-100 p-5">
          <h3 className="font-bold text-slate-800 mb-4">Kategoriyalar bo'yicha</h3>
          <div className="space-y-3">
            {cats.slice(0,5).map(([cat,val])=>(
              <div key={cat} className="flex items-center gap-3">
                <p className="text-xs font-medium text-slate-600 w-20 shrink-0 truncate">{cat}</p>
                <div className="flex-1 bg-slate-100 rounded-full h-2">
                  <div className="bg-emerald-500 h-2 rounded-full" style={{width:`${(val/maxCat)*100}%`}} />
                </div>
                <p className="text-xs font-bold text-slate-700 w-16 text-right shrink-0">{(val/1000).toFixed(0)}k</p>
              </div>
            ))}
            {cats.length===0&&<p className="text-sm text-slate-400">Ma'lumot yo'q</p>}
          </div>
        </div>
      </div>
    </div>
  );
}
