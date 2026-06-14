import { useState } from 'react';
import { Plus, Search, X, ShoppingCart, Trash2, CheckCircle, Clock, XCircle } from 'lucide-react';
import type { Order, OrderItem, Product, Customer, PaymentMethod, OrderStatus } from '../types';

interface Props {
  orders: Order[];
  products: Product[];
  customers: Customer[];
  onAdd: (o: Omit<Order,'id'>) => void;
}

const statusCfg: Record<OrderStatus,{label:string;color:string;icon:any}> = {
  completed: { label: 'Bajarildi', color: 'bg-emerald-100 text-emerald-700', icon: CheckCircle },
  pending: { label: 'Kutilmoqda', color: 'bg-amber-100 text-amber-700', icon: Clock },
  cancelled: { label: 'Bekor', color: 'bg-red-100 text-red-700', icon: XCircle },
  refunded: { label: 'Qaytarildi', color: 'bg-slate-100 text-slate-600', icon: XCircle },
};
const methodLabel: Record<PaymentMethod,string> = { cash: "Naqd", card: "Karta", transfer: "O'tkazma" };

export function Sales({ orders, products, customers, onAdd }: Props) {
  const [search, setSearch] = useState('');
  const [showNew, setShowNew] = useState(false);

  // New sale state
  const [custSearch, setCustSearch] = useState('');
  const [selectedCust, setSelectedCust] = useState<Customer|null>(null);
  const [guestName, setGuestName] = useState('');
  const [items, setItems] = useState<OrderItem[]>([]);
  const [addProd, setAddProd] = useState<Product|null>(null);
  const [addSize, setAddSize] = useState('');
  const [addColor, setAddColor] = useState('');
  const [addQty, setAddQty] = useState(1);
  const [prodSearch, setProdSearch] = useState('');
  const [method, setMethod] = useState<PaymentMethod>('cash');
  const [extraDiscount, setExtraDiscount] = useState(0);
  const [paid, setPaid] = useState(0);

  const filtered = orders.filter(o =>
    o.customerName.toLowerCase().includes(search.toLowerCase()) ||
    o.id.toLowerCase().includes(search.toLowerCase())
  );

  const subtotal = items.reduce((s,i)=>s+i.unitPrice*i.qty,0);
  const itemDisc = items.reduce((s,i)=>s+i.unitPrice*i.qty*(i.discount/100),0);
  const total = Math.round(subtotal - itemDisc - (subtotal-itemDisc)*(extraDiscount/100));
  const change = Math.max(0, paid - total);

  const custBase = selectedCust ? selectedCust.discount : 0;

  const addItem = () => {
    if (!addProd || !addSize || !addColor || addQty < 1) return;
    const existing = items.findIndex(i=>i.productId===addProd.id&&i.size===addSize&&i.color===addColor);
    if (existing>=0) {
      setItems(prev=>prev.map((it,idx)=>idx===existing?{...it,qty:it.qty+addQty}:it));
    } else {
      setItems(prev=>[...prev,{productId:addProd.id,productName:addProd.name,size:addSize,color:addColor,qty:addQty,unitPrice:addProd.sellPrice,discount:custBase}]);
    }
    setAddProd(null); setAddSize(''); setAddColor(''); setAddQty(1); setProdSearch('');
  };

  const removeItem = (idx:number) => setItems(prev=>prev.filter((_,i)=>i!==idx));

  const handleSubmit = () => {
    if (items.length===0) return;
    const cName = selectedCust ? `${selectedCust.firstName} ${selectedCust.lastName}` : (guestName||"Noma'lum");
    onAdd({
      customerId: selectedCust?.id, customerName: cName,
      items, subtotal, discount: itemDisc+((subtotal-itemDisc)*(extraDiscount/100)),
      total, paid: paid||total, change,
      method, status: 'completed',
      date: new Date().toISOString().slice(0,10),
      sellerId:'u1',
    });
    setShowNew(false); setItems([]); setSelectedCust(null); setGuestName(''); setExtraDiscount(0); setPaid(0); setMethod('cash');
  };

  const filteredProds = products.filter(p=>p.status!=='out_of_stock'&&p.name.toLowerCase().includes(prodSearch.toLowerCase()));
  const filteredCusts = customers.filter(c=>`${c.firstName} ${c.lastName}`.toLowerCase().includes(custSearch.toLowerCase())||c.phone.includes(custSearch));

  return (
    <div className="space-y-4">
      <div className="flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
          <input value={search} onChange={e=>setSearch(e.target.value)} placeholder="Buyurtma qidirish..."
            className="w-full pl-9 pr-4 py-2.5 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-violet-500" />
        </div>
        <button onClick={()=>setShowNew(true)} className="flex items-center gap-2 px-4 py-2.5 bg-violet-600 hover:bg-violet-700 text-white rounded-xl text-sm font-medium transition-colors shrink-0">
          <Plus className="w-4 h-4" /> Yangi sotuv
        </button>
      </div>

      {/* Summary */}
      <div className="grid grid-cols-3 gap-3">
        {[
          { label: "Bugungi sotuv", value: orders.filter(o=>o.date===new Date().toISOString().slice(0,10)&&o.status==='completed').length + ' ta' },
          { label: "Jami buyurtmalar", value: orders.length + ' ta' },
          { label: "Jami daromad", value: orders.filter(o=>o.status==='completed').reduce((s,o)=>s+o.total,0).toLocaleString() + " so'm" },
        ].map(s=>(
          <div key={s.label} className="bg-white rounded-2xl border border-slate-100 p-4 text-center">
            <p className="text-lg font-bold text-slate-800">{s.value}</p>
            <p className="text-xs text-slate-400 mt-0.5">{s.label}</p>
          </div>
        ))}
      </div>

      {/* Orders list */}
      <div className="bg-white rounded-2xl border border-slate-100 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-slate-100 bg-slate-50/50">
                {['Buyurtma #','Mijoz','Mahsulotlar','Jami','To\'lov','Holat','Sana'].map(h=>(
                  <th key={h} className="px-4 py-3 text-left text-xs font-semibold text-slate-500">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-50">
              {filtered.map(o=>{
                const cfg = statusCfg[o.status];
                const Icon = cfg.icon;
                return (
                  <tr key={o.id} className="hover:bg-slate-50/50 transition-colors">
                    <td className="px-4 py-3 text-sm font-mono text-slate-600">#{o.id}</td>
                    <td className="px-4 py-3 text-sm font-medium text-slate-800">{o.customerName}</td>
                    <td className="px-4 py-3 text-xs text-slate-500 max-w-[180px]">
                      {o.items.map(i=>`${i.productName} (${i.size}, ${i.qty})`).join('; ')}
                    </td>
                    <td className="px-4 py-3 text-sm font-bold text-slate-800">{o.total.toLocaleString()}</td>
                    <td className="px-4 py-3 text-xs text-slate-600">{methodLabel[o.method]}</td>
                    <td className="px-4 py-3">
                      <span className={`flex items-center gap-1 text-xs px-2 py-0.5 rounded-full font-medium w-fit ${cfg.color}`}>
                        <Icon className="w-3 h-3" />{cfg.label}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-xs text-slate-400">{o.date}</td>
                  </tr>
                );
              })}
              {filtered.length===0&&(
                <tr><td colSpan={7} className="px-4 py-12 text-center text-slate-400 text-sm">Buyurtma topilmadi</td></tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* New sale modal */}
      {showNew && (
        <div className="fixed inset-0 z-50 flex items-start justify-center p-4 bg-black/40 overflow-y-auto">
          <div className="bg-white rounded-2xl shadow-2xl w-full max-w-2xl my-4">
            <div className="flex items-center justify-between px-6 py-4 border-b border-slate-100">
              <div className="flex items-center gap-2">
                <ShoppingCart className="w-5 h-5 text-violet-600" />
                <h2 className="font-bold text-slate-800">Yangi sotuv</h2>
              </div>
              <button onClick={()=>setShowNew(false)} className="p-2 rounded-xl hover:bg-slate-100 text-slate-400"><X className="w-4 h-4" /></button>
            </div>
            <div className="p-6 space-y-5">
              {/* Customer */}
              <div>
                <label className="text-xs font-semibold text-slate-600 block mb-2">Mijoz (ixtiyoriy)</label>
                {selectedCust ? (
                  <div className="flex items-center gap-3 p-3 rounded-xl bg-violet-50 border border-violet-200">
                    <div className="w-8 h-8 rounded-full bg-violet-600 flex items-center justify-center text-white text-sm font-bold">{selectedCust.firstName[0]}</div>
                    <div className="flex-1">
                      <p className="text-sm font-medium text-slate-800">{selectedCust.firstName} {selectedCust.lastName}</p>
                      <p className="text-xs text-slate-400">{selectedCust.phone} · {selectedCust.discount}% chegirma</p>
                    </div>
                    <button onClick={()=>setSelectedCust(null)} className="text-slate-400 hover:text-slate-600"><X className="w-4 h-4"/></button>
                  </div>
                ) : (
                  <div className="space-y-2">
                    <input value={custSearch} onChange={e=>setCustSearch(e.target.value)} placeholder="Mijoz qidirish..."
                      className="w-full px-3 py-2.5 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-violet-500" />
                    {custSearch && (
                      <div className="border border-slate-200 rounded-xl overflow-hidden max-h-32 overflow-y-auto">
                        {filteredCusts.slice(0,5).map(c=>(
                          <button key={c.id} onClick={()=>{setSelectedCust(c);setCustSearch('');}} className="w-full flex items-center gap-2 px-3 py-2 hover:bg-slate-50 text-left transition-colors">
                            <span className="text-sm text-slate-700">{c.firstName} {c.lastName}</span>
                            <span className="text-xs text-slate-400 ml-auto">{c.phone}</span>
                          </button>
                        ))}
                        {filteredCusts.length===0&&<p className="px-3 py-2 text-xs text-slate-400">Topilmadi</p>}
                      </div>
                    )}
                    <input value={guestName} onChange={e=>setGuestName(e.target.value)} placeholder="Yoki mehmon ismi..."
                      className="w-full px-3 py-2.5 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-violet-500" />
                  </div>
                )}
              </div>

              {/* Product picker */}
              <div className="border border-slate-200 rounded-xl p-4 space-y-3">
                <p className="text-xs font-semibold text-slate-600">Mahsulot qo'shish</p>
                <input value={prodSearch} onChange={e=>setProdSearch(e.target.value)} placeholder="Mahsulot qidirish..."
                  className="w-full px-3 py-2 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-violet-500" />
                {prodSearch && !addProd && (
                  <div className="border border-slate-200 rounded-xl overflow-hidden max-h-36 overflow-y-auto">
                    {filteredProds.slice(0,6).map(p=>(
                      <button key={p.id} onClick={()=>{setAddProd(p);setAddSize(p.sizes[0]||'');setAddColor(p.colors[0]||'');setProdSearch(p.name);}}
                        className="w-full flex items-center gap-2 px-3 py-2 hover:bg-slate-50 text-left transition-colors">
                        <div className="flex-1">
                          <p className="text-sm text-slate-700">{p.name}</p>
                          <p className="text-xs text-slate-400">{p.stock} ta · {p.sellPrice.toLocaleString()} so'm</p>
                        </div>
                      </button>
                    ))}
                    {filteredProds.length===0&&<p className="px-3 py-2 text-xs text-slate-400">Topilmadi</p>}
                  </div>
                )}
                {addProd && (
                  <div className="grid grid-cols-4 gap-2 items-end">
                    <div>
                      <p className="text-xs text-slate-500 mb-1">O'lcham</p>
                      <select value={addSize} onChange={e=>setAddSize(e.target.value)} className="w-full px-2 py-2 rounded-lg border border-slate-200 text-sm bg-white">
                        {addProd.sizes.map(s=><option key={s}>{s}</option>)}
                      </select>
                    </div>
                    <div>
                      <p className="text-xs text-slate-500 mb-1">Rang</p>
                      <select value={addColor} onChange={e=>setAddColor(e.target.value)} className="w-full px-2 py-2 rounded-lg border border-slate-200 text-sm bg-white">
                        {addProd.colors.map(c=><option key={c}>{c}</option>)}
                      </select>
                    </div>
                    <div>
                      <p className="text-xs text-slate-500 mb-1">Soni</p>
                      <input type="number" min={1} value={addQty} onChange={e=>setAddQty(+e.target.value)} className="w-full px-2 py-2 rounded-lg border border-slate-200 text-sm" />
                    </div>
                    <button onClick={addItem} className="px-3 py-2 bg-violet-600 hover:bg-violet-700 text-white rounded-lg text-sm font-medium transition-colors">+Qo'sh</button>
                  </div>
                )}
              </div>

              {/* Cart */}
              {items.length > 0 && (
                <div className="space-y-2">
                  <p className="text-xs font-semibold text-slate-600">Savatcha ({items.length} mahsulot)</p>
                  {items.map((it,idx)=>(
                    <div key={idx} className="flex items-center gap-3 p-3 bg-slate-50 rounded-xl">
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-slate-800 truncate">{it.productName}</p>
                        <p className="text-xs text-slate-400">{it.size} · {it.color} · {it.qty} ta</p>
                      </div>
                      <p className="text-sm font-bold text-slate-800 shrink-0">{(it.unitPrice*it.qty).toLocaleString()}</p>
                      <button onClick={()=>removeItem(idx)} className="text-slate-400 hover:text-red-500 shrink-0"><Trash2 className="w-4 h-4"/></button>
                    </div>
                  ))}
                </div>
              )}

              {/* Payment */}
              <div className="border border-slate-200 rounded-xl p-4 space-y-3">
                <p className="text-xs font-semibold text-slate-600">To'lov</p>
                <div className="grid grid-cols-3 gap-2">
                  {(['cash','card','transfer'] as PaymentMethod[]).map(m=>(
                    <button key={m} onClick={()=>setMethod(m)} className={`py-2 rounded-xl text-sm font-medium transition-colors ${method===m?'bg-violet-600 text-white':'bg-slate-100 text-slate-600 hover:bg-slate-200'}`}>
                      {methodLabel[m]}
                    </button>
                  ))}
                </div>
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="text-xs text-slate-500 block mb-1">Qo'shimcha chegirma (%)</label>
                    <input type="number" min={0} max={100} value={extraDiscount||''} onChange={e=>setExtraDiscount(+e.target.value)}
                      className="w-full px-3 py-2 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-violet-500" />
                  </div>
                  <div>
                    <label className="text-xs text-slate-500 block mb-1">Qabul qilingan (so'm)</label>
                    <input type="number" value={paid||''} onChange={e=>setPaid(+e.target.value)}
                      className="w-full px-3 py-2 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-violet-500" />
                  </div>
                </div>
                <div className="bg-slate-50 rounded-xl p-3 space-y-1">
                  <div className="flex justify-between text-sm"><span className="text-slate-500">Jami:</span><span className="font-bold text-slate-800">{total.toLocaleString()} so'm</span></div>
                  {paid > 0 && <div className="flex justify-between text-sm"><span className="text-slate-500">Qaytim:</span><span className={`font-bold ${change>0?'text-emerald-600':'text-slate-800'}`}>{change.toLocaleString()} so'm</span></div>}
                </div>
              </div>
            </div>
            <div className="flex gap-3 px-6 pb-6">
              <button onClick={()=>setShowNew(false)} className="flex-1 px-4 py-2.5 rounded-xl border border-slate-200 text-sm font-medium text-slate-600 hover:bg-slate-50 transition-colors">Bekor</button>
              <button onClick={handleSubmit} disabled={items.length===0} className="flex-1 px-4 py-2.5 rounded-xl bg-violet-600 hover:bg-violet-700 disabled:opacity-50 disabled:cursor-not-allowed text-white text-sm font-medium transition-colors">
                Sotuvni yakunlash · {total.toLocaleString()} so'm
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
