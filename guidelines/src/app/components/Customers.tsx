import { useState } from 'react';
import { Plus, Search, Edit2, Trash2, X, User } from 'lucide-react';
import type { Customer, Order } from '../types';

interface Props {
  customers: Customer[];
  orders: Order[];
  onAdd: (d: Omit<Customer,'id'>) => void;
  onEdit: (c: Customer) => void;
  onDelete: (id: string) => void;
}

const EMPTY: Omit<Customer,'id'> = {
  firstName:'', lastName:'', phone:'', address:'', totalOrders:0, totalSpent:0, discount:0, addedDate: new Date().toISOString().slice(0,10),
};

export function Customers({ customers, orders, onAdd, onEdit, onDelete }: Props) {
  const [search, setSearch] = useState('');
  const [modal, setModal] = useState<'add'|'edit'|'delete'|'view'|null>(null);
  const [selected, setSelected] = useState<Customer|null>(null);
  const [form, setForm] = useState<Omit<Customer,'id'>>(EMPTY);

  const filtered = customers.filter(c =>
    `${c.firstName} ${c.lastName}`.toLowerCase().includes(search.toLowerCase()) ||
    c.phone.includes(search)
  );

  const openAdd = () => { setForm(EMPTY); setModal('add'); };
  const openEdit = (c: Customer) => { setSelected(c); setForm({...c}); setModal('edit'); };
  const openDelete = (c: Customer) => { setSelected(c); setModal('delete'); };
  const openView = (c: Customer) => { setSelected(c); setModal('view'); };
  const close = () => { setModal(null); setSelected(null); };

  const handleSave = () => {
    if (!form.firstName || !form.phone) return;
    if (modal === 'add') onAdd(form);
    else if (modal === 'edit' && selected) onEdit({ ...form, id: selected.id });
    close();
  };

  const customerOrders = (id: string) => orders.filter(o => o.customerId === id);

  return (
    <div className="space-y-4">
      <div className="flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
          <input value={search} onChange={e=>setSearch(e.target.value)} placeholder="Mijoz qidirish..."
            className="w-full pl-9 pr-4 py-2.5 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-violet-500" />
        </div>
        <button onClick={openAdd} className="flex items-center gap-2 px-4 py-2.5 bg-violet-600 hover:bg-violet-700 text-white rounded-xl text-sm font-medium transition-colors shrink-0">
          <Plus className="w-4 h-4" /> Mijoz qo'shish
        </button>
      </div>

      <div className="grid grid-cols-3 gap-3">
        {[
          { label: 'Jami mijozlar', value: customers.length },
          { label: 'Faol (≥1 xarid)', value: customers.filter(c=>c.totalOrders>0).length },
          { label: "Chegirmali", value: customers.filter(c=>c.discount>0).length },
        ].map(s => (
          <div key={s.label} className="bg-white rounded-2xl border border-slate-100 p-4 text-center">
            <p className="text-2xl font-bold text-slate-800">{s.value}</p>
            <p className="text-xs text-slate-400 mt-0.5">{s.label}</p>
          </div>
        ))}
      </div>

      <div className="bg-white rounded-2xl border border-slate-100 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-slate-100 bg-slate-50/50">
                {['Mijoz','Telefon','Xaridlar','Jami xarid','Chegirma',''].map(h=>(
                  <th key={h} className="px-4 py-3 text-left text-xs font-semibold text-slate-500">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-50">
              {filtered.map(c => (
                <tr key={c.id} className="hover:bg-slate-50/50 transition-colors cursor-pointer" onClick={()=>openView(c)}>
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 rounded-full bg-gradient-to-br from-violet-400 to-blue-500 flex items-center justify-center text-white text-sm font-bold shrink-0">
                        {c.firstName[0]}
                      </div>
                      <div>
                        <p className="text-sm font-medium text-slate-800">{c.firstName} {c.lastName}</p>
                        {c.address && <p className="text-xs text-slate-400">{c.address}</p>}
                      </div>
                    </div>
                  </td>
                  <td className="px-4 py-3 text-sm text-slate-600">{c.phone}</td>
                  <td className="px-4 py-3 text-sm text-slate-700 font-medium">{c.totalOrders} ta</td>
                  <td className="px-4 py-3 text-sm font-bold text-slate-800">{c.totalSpent.toLocaleString()} so'm</td>
                  <td className="px-4 py-3">
                    {c.discount > 0 ? (
                      <span className="text-xs px-2 py-0.5 bg-emerald-100 text-emerald-700 rounded-full font-medium">{c.discount}%</span>
                    ) : <span className="text-xs text-slate-400">—</span>}
                  </td>
                  <td className="px-4 py-3" onClick={e=>e.stopPropagation()}>
                    <div className="flex items-center gap-1">
                      <button onClick={()=>openEdit(c)} className="p-1.5 rounded-lg hover:bg-slate-100 text-slate-500 hover:text-blue-600 transition-colors">
                        <Edit2 className="w-4 h-4" />
                      </button>
                      <button onClick={()=>openDelete(c)} className="p-1.5 rounded-lg hover:bg-red-50 text-slate-500 hover:text-red-600 transition-colors">
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
              {filtered.length === 0 && (
                <tr><td colSpan={6} className="px-4 py-12 text-center text-slate-400 text-sm">Mijoz topilmadi</td></tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Add/Edit */}
      {(modal === 'add' || modal === 'edit') && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40">
          <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md">
            <div className="flex items-center justify-between px-6 py-4 border-b border-slate-100">
              <h2 className="font-bold text-slate-800">{modal==='add'?"Mijoz qo'shish":'Tahrirlash'}</h2>
              <button onClick={close} className="p-2 rounded-xl hover:bg-slate-100 text-slate-400"><X className="w-4 h-4" /></button>
            </div>
            <div className="p-6 space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-xs font-semibold text-slate-600 block mb-1.5">Ism *</label>
                  <input value={form.firstName} onChange={e=>setForm(f=>({...f,firstName:e.target.value}))}
                    className="w-full px-3 py-2.5 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-violet-500" />
                </div>
                <div>
                  <label className="text-xs font-semibold text-slate-600 block mb-1.5">Familiya</label>
                  <input value={form.lastName} onChange={e=>setForm(f=>({...f,lastName:e.target.value}))}
                    className="w-full px-3 py-2.5 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-violet-500" />
                </div>
                <div className="col-span-2">
                  <label className="text-xs font-semibold text-slate-600 block mb-1.5">Telefon *</label>
                  <input value={form.phone} onChange={e=>setForm(f=>({...f,phone:e.target.value}))} placeholder="+998901234567"
                    className="w-full px-3 py-2.5 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-violet-500" />
                </div>
                <div className="col-span-2">
                  <label className="text-xs font-semibold text-slate-600 block mb-1.5">Manzil</label>
                  <input value={form.address||''} onChange={e=>setForm(f=>({...f,address:e.target.value}))}
                    className="w-full px-3 py-2.5 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-violet-500" />
                </div>
                <div>
                  <label className="text-xs font-semibold text-slate-600 block mb-1.5">Chegirma (%)</label>
                  <input type="number" min={0} max={100} value={form.discount||''} onChange={e=>setForm(f=>({...f,discount:+e.target.value}))}
                    className="w-full px-3 py-2.5 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-violet-500" />
                </div>
              </div>
            </div>
            <div className="flex gap-3 px-6 pb-6">
              <button onClick={close} className="flex-1 px-4 py-2.5 rounded-xl border border-slate-200 text-sm font-medium text-slate-600 hover:bg-slate-50 transition-colors">Bekor</button>
              <button onClick={handleSave} className="flex-1 px-4 py-2.5 rounded-xl bg-violet-600 hover:bg-violet-700 text-white text-sm font-medium transition-colors">Saqlash</button>
            </div>
          </div>
        </div>
      )}

      {/* View */}
      {modal === 'view' && selected && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40">
          <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md max-h-[80vh] overflow-y-auto">
            <div className="flex items-center justify-between px-6 py-4 border-b border-slate-100">
              <h2 className="font-bold text-slate-800">Mijoz ma'lumotlari</h2>
              <button onClick={close} className="p-2 rounded-xl hover:bg-slate-100 text-slate-400"><X className="w-4 h-4" /></button>
            </div>
            <div className="p-6 space-y-4">
              <div className="flex items-center gap-4">
                <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-violet-400 to-blue-500 flex items-center justify-center text-white text-2xl font-bold">
                  {selected.firstName[0]}
                </div>
                <div>
                  <p className="text-lg font-bold text-slate-800">{selected.firstName} {selected.lastName}</p>
                  <p className="text-sm text-slate-500">{selected.phone}</p>
                </div>
              </div>
              <div className="grid grid-cols-2 gap-3">
                {[
                  { label: "Jami xaridlar", value: `${selected.totalOrders} ta` },
                  { label: "Jami summa", value: `${selected.totalSpent.toLocaleString()} so'm` },
                  { label: "Chegirma", value: selected.discount ? `${selected.discount}%` : 'Yo\'q' },
                  { label: "Ro'yxatga olingan", value: selected.addedDate },
                ].map(i => (
                  <div key={i.label} className="bg-slate-50 rounded-xl p-3">
                    <p className="text-xs text-slate-400">{i.label}</p>
                    <p className="text-sm font-semibold text-slate-800 mt-0.5">{i.value}</p>
                  </div>
                ))}
              </div>
              <div>
                <p className="text-xs font-semibold text-slate-500 mb-2">So'nggi xaridlar</p>
                {customerOrders(selected.id).slice(0,3).map(o => (
                  <div key={o.id} className="flex justify-between items-center py-2 border-b border-slate-50 last:border-0">
                    <div>
                      <p className="text-xs font-medium text-slate-700">{o.items.map(i=>i.productName).join(', ')}</p>
                      <p className="text-xs text-slate-400">{o.date}</p>
                    </div>
                    <p className="text-xs font-bold text-slate-800">{o.total.toLocaleString()} so'm</p>
                  </div>
                ))}
                {customerOrders(selected.id).length === 0 && <p className="text-xs text-slate-400">Xaridlar yo'q</p>}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Delete */}
      {modal === 'delete' && selected && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40">
          <div className="bg-white rounded-2xl shadow-2xl w-full max-w-sm p-6 space-y-4">
            <div className="w-12 h-12 bg-red-100 rounded-2xl flex items-center justify-center mx-auto">
              <Trash2 className="w-6 h-6 text-red-600" />
            </div>
            <div className="text-center">
              <h2 className="font-bold text-slate-800">Mijozni o'chirish</h2>
              <p className="text-sm text-slate-500 mt-1">"{selected.firstName} {selected.lastName}" mijozini o'chirishni tasdiqlaysizmi?</p>
            </div>
            <div className="flex gap-3">
              <button onClick={close} className="flex-1 px-4 py-2.5 rounded-xl border border-slate-200 text-sm font-medium text-slate-600 hover:bg-slate-50 transition-colors">Bekor</button>
              <button onClick={()=>{onDelete(selected.id);close();}} className="flex-1 px-4 py-2.5 rounded-xl bg-red-600 hover:bg-red-700 text-white text-sm font-medium transition-colors">O'chirish</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
