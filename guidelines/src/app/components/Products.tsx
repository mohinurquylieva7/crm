import { useState } from 'react';
import { Plus, Search, Edit2, Trash2, X, Package, AlertTriangle } from 'lucide-react';
import type { Product, ProductStatus } from '../types';

interface Props {
  products: Product[];
  onAdd: (d: Omit<Product,'id'>) => void;
  onEdit: (p: Product) => void;
  onDelete: (id: string) => void;
}

const CATEGORIES = ["Ko'ylak",'Bluzka','Shim','Kurtka','Futbolka','Palto','Dress','Boshqa'];
const EMPTY: Omit<Product,'id'> = {
  name:'', category: CATEGORIES[0], brand:'', sizes:[], colors:[], buyPrice:0, sellPrice:0, stock:0, minStock:5, status:'active', addedDate: new Date().toISOString().slice(0,10),
};

const statusCfg: Record<ProductStatus,{label:string;color:string}> = {
  active: { label: 'Faol', color: 'bg-emerald-100 text-emerald-700' },
  inactive: { label: 'Nofaol', color: 'bg-slate-100 text-slate-600' },
  out_of_stock: { label: 'Tugagan', color: 'bg-red-100 text-red-700' },
};

export function Products({ products, onAdd, onEdit, onDelete }: Props) {
  const [search, setSearch] = useState('');
  const [catFilter, setCatFilter] = useState('');
  const [modal, setModal] = useState<'add'|'edit'|'delete'|null>(null);
  const [selected, setSelected] = useState<Product|null>(null);
  const [form, setForm] = useState<Omit<Product,'id'>>(EMPTY);
  const [sizeInput, setSizeInput] = useState('');
  const [colorInput, setColorInput] = useState('');

  const filtered = products.filter(p =>
    (p.name.toLowerCase().includes(search.toLowerCase()) || p.brand.toLowerCase().includes(search.toLowerCase())) &&
    (!catFilter || p.category === catFilter)
  );
  const cats = [...new Set(products.map(p=>p.category))];

  const openAdd = () => { setForm(EMPTY); setSizeInput(''); setColorInput(''); setModal('add'); };
  const openEdit = (p: Product) => { setSelected(p); setForm({...p}); setSizeInput(''); setColorInput(''); setModal('edit'); };
  const openDelete = (p: Product) => { setSelected(p); setModal('delete'); };
  const close = () => { setModal(null); setSelected(null); };

  const addTag = (field: 'sizes'|'colors', val: string, setter: (v:string)=>void) => {
    if (!val.trim()) return;
    setForm(f => ({ ...f, [field]: f[field].includes(val.trim()) ? f[field] : [...f[field], val.trim()] }));
    setter('');
  };
  const removeTag = (field: 'sizes'|'colors', val: string) => {
    setForm(f => ({ ...f, [field]: f[field].filter(v => v !== val) }));
  };

  const handleSave = () => {
    if (!form.name || !form.sellPrice) return;
    if (modal === 'add') onAdd(form);
    else if (modal === 'edit' && selected) onEdit({ ...form, id: selected.id });
    close();
  };

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
          <input value={search} onChange={e=>setSearch(e.target.value)} placeholder="Mahsulot qidirish..."
            className="w-full pl-9 pr-4 py-2.5 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-violet-500" />
        </div>
        <select value={catFilter} onChange={e=>setCatFilter(e.target.value)}
          className="px-3 py-2.5 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-violet-500 bg-white">
          <option value="">Barcha kategoriyalar</option>
          {cats.map(c => <option key={c}>{c}</option>)}
        </select>
        <button onClick={openAdd} className="flex items-center gap-2 px-4 py-2.5 bg-violet-600 hover:bg-violet-700 text-white rounded-xl text-sm font-medium transition-colors shrink-0">
          <Plus className="w-4 h-4" /> Mahsulot qo'shish
        </button>
      </div>

      {/* Stats row */}
      <div className="grid grid-cols-3 gap-3">
        {[
          { label: "Jami", value: products.length, color: 'text-slate-700' },
          { label: "Kam qolgan", value: products.filter(p=>p.stock>0&&p.stock<=p.minStock).length, color: 'text-amber-600' },
          { label: "Tugagan", value: products.filter(p=>p.stock===0).length, color: 'text-red-600' },
        ].map(s => (
          <div key={s.label} className="bg-white rounded-2xl border border-slate-100 p-4 text-center">
            <p className={`text-2xl font-bold ${s.color}`}>{s.value}</p>
            <p className="text-xs text-slate-400 mt-0.5">{s.label}</p>
          </div>
        ))}
      </div>

      {/* Table */}
      <div className="bg-white rounded-2xl border border-slate-100 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-slate-100 bg-slate-50/50">
                {['Mahsulot','Kategoriya','Narx','Xarid narxi','Stok','Holat',''].map(h => (
                  <th key={h} className="px-4 py-3 text-left text-xs font-semibold text-slate-500">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-50">
              {filtered.map(p => (
                <tr key={p.id} className="hover:bg-slate-50/50 transition-colors">
                  <td className="px-4 py-3">
                    <div>
                      <p className="text-sm font-medium text-slate-800">{p.name}</p>
                      <p className="text-xs text-slate-400">{p.brand} · {p.sizes.join(', ')}</p>
                    </div>
                  </td>
                  <td className="px-4 py-3 text-sm text-slate-600">{p.category}</td>
                  <td className="px-4 py-3 text-sm font-semibold text-slate-800">{p.sellPrice.toLocaleString()}</td>
                  <td className="px-4 py-3 text-sm text-slate-500">{p.buyPrice.toLocaleString()}</td>
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-1.5">
                      {p.stock <= p.minStock && p.stock > 0 && <AlertTriangle className="w-3.5 h-3.5 text-amber-500" />}
                      <span className={`text-sm font-medium ${p.stock === 0 ? 'text-red-600' : p.stock <= p.minStock ? 'text-amber-600' : 'text-slate-700'}`}>
                        {p.stock} ta
                      </span>
                    </div>
                  </td>
                  <td className="px-4 py-3">
                    <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${statusCfg[p.status].color}`}>
                      {statusCfg[p.status].label}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-1">
                      <button onClick={() => openEdit(p)} className="p-1.5 rounded-lg hover:bg-slate-100 text-slate-500 hover:text-blue-600 transition-colors">
                        <Edit2 className="w-4 h-4" />
                      </button>
                      <button onClick={() => openDelete(p)} className="p-1.5 rounded-lg hover:bg-red-50 text-slate-500 hover:text-red-600 transition-colors">
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
              {filtered.length === 0 && (
                <tr><td colSpan={7} className="px-4 py-12 text-center text-slate-400 text-sm">Mahsulot topilmadi</td></tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Add/Edit Modal */}
      {(modal === 'add' || modal === 'edit') && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40">
          <div className="bg-white rounded-2xl shadow-2xl w-full max-w-lg max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between px-6 py-4 border-b border-slate-100">
              <h2 className="font-bold text-slate-800">{modal === 'add' ? "Mahsulot qo'shish" : 'Tahrirlash'}</h2>
              <button onClick={close} className="p-2 rounded-xl hover:bg-slate-100 text-slate-400 transition-colors"><X className="w-4 h-4" /></button>
            </div>
            <div className="p-6 space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="col-span-2">
                  <label className="text-xs font-semibold text-slate-600 block mb-1.5">Mahsulot nomi *</label>
                  <input value={form.name} onChange={e=>setForm(f=>({...f,name:e.target.value}))}
                    className="w-full px-3 py-2.5 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-violet-500" />
                </div>
                <div>
                  <label className="text-xs font-semibold text-slate-600 block mb-1.5">Kategoriya</label>
                  <select value={form.category} onChange={e=>setForm(f=>({...f,category:e.target.value}))}
                    className="w-full px-3 py-2.5 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-violet-500 bg-white">
                    {CATEGORIES.map(c=><option key={c}>{c}</option>)}
                  </select>
                </div>
                <div>
                  <label className="text-xs font-semibold text-slate-600 block mb-1.5">Brend</label>
                  <input value={form.brand} onChange={e=>setForm(f=>({...f,brand:e.target.value}))}
                    className="w-full px-3 py-2.5 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-violet-500" />
                </div>
                <div>
                  <label className="text-xs font-semibold text-slate-600 block mb-1.5">Xarid narxi (so'm)</label>
                  <input type="number" value={form.buyPrice||''} onChange={e=>setForm(f=>({...f,buyPrice:+e.target.value}))}
                    className="w-full px-3 py-2.5 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-violet-500" />
                </div>
                <div>
                  <label className="text-xs font-semibold text-slate-600 block mb-1.5">Sotuv narxi (so'm) *</label>
                  <input type="number" value={form.sellPrice||''} onChange={e=>setForm(f=>({...f,sellPrice:+e.target.value}))}
                    className="w-full px-3 py-2.5 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-violet-500" />
                </div>
                <div>
                  <label className="text-xs font-semibold text-slate-600 block mb-1.5">Stok soni</label>
                  <input type="number" value={form.stock||''} onChange={e=>setForm(f=>({...f,stock:+e.target.value}))}
                    className="w-full px-3 py-2.5 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-violet-500" />
                </div>
                <div>
                  <label className="text-xs font-semibold text-slate-600 block mb-1.5">Min. stok (ogohlantirish)</label>
                  <input type="number" value={form.minStock||''} onChange={e=>setForm(f=>({...f,minStock:+e.target.value}))}
                    className="w-full px-3 py-2.5 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-violet-500" />
                </div>
              </div>
              {/* Sizes */}
              <div>
                <label className="text-xs font-semibold text-slate-600 block mb-1.5">O'lchamlar</label>
                <div className="flex gap-2 mb-2">
                  <input value={sizeInput} onChange={e=>setSizeInput(e.target.value)}
                    onKeyDown={e=>{ if(e.key==='Enter'){ e.preventDefault(); addTag('sizes',sizeInput,setSizeInput); }}}
                    placeholder="S, M, L, XL..."
                    className="flex-1 px-3 py-2 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-violet-500" />
                  <button onClick={()=>addTag('sizes',sizeInput,setSizeInput)} className="px-3 py-2 bg-slate-100 rounded-xl text-sm hover:bg-slate-200 transition-colors">+</button>
                </div>
                <div className="flex flex-wrap gap-1.5">
                  {form.sizes.map(s=>(
                    <span key={s} className="flex items-center gap-1 px-2 py-0.5 bg-violet-100 text-violet-700 text-xs rounded-full">
                      {s} <button onClick={()=>removeTag('sizes',s)}><X className="w-3 h-3" /></button>
                    </span>
                  ))}
                </div>
              </div>
              {/* Colors */}
              <div>
                <label className="text-xs font-semibold text-slate-600 block mb-1.5">Ranglar</label>
                <div className="flex gap-2 mb-2">
                  <input value={colorInput} onChange={e=>setColorInput(e.target.value)}
                    onKeyDown={e=>{ if(e.key==='Enter'){ e.preventDefault(); addTag('colors',colorInput,setColorInput); }}}
                    placeholder="Qora, Oq, Ko'k..."
                    className="flex-1 px-3 py-2 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-violet-500" />
                  <button onClick={()=>addTag('colors',colorInput,setColorInput)} className="px-3 py-2 bg-slate-100 rounded-xl text-sm hover:bg-slate-200 transition-colors">+</button>
                </div>
                <div className="flex flex-wrap gap-1.5">
                  {form.colors.map(c=>(
                    <span key={c} className="flex items-center gap-1 px-2 py-0.5 bg-blue-100 text-blue-700 text-xs rounded-full">
                      {c} <button onClick={()=>removeTag('colors',c)}><X className="w-3 h-3" /></button>
                    </span>
                  ))}
                </div>
              </div>
              <div>
                <label className="text-xs font-semibold text-slate-600 block mb-1.5">Holat</label>
                <select value={form.status} onChange={e=>setForm(f=>({...f,status:e.target.value as any}))}
                  className="w-full px-3 py-2.5 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-violet-500 bg-white">
                  <option value="active">Faol</option>
                  <option value="inactive">Nofaol</option>
                  <option value="out_of_stock">Tugagan</option>
                </select>
              </div>
            </div>
            <div className="flex gap-3 px-6 pb-6">
              <button onClick={close} className="flex-1 px-4 py-2.5 rounded-xl border border-slate-200 text-sm font-medium text-slate-600 hover:bg-slate-50 transition-colors">Bekor qilish</button>
              <button onClick={handleSave} className="flex-1 px-4 py-2.5 rounded-xl bg-violet-600 hover:bg-violet-700 text-white text-sm font-medium transition-colors">Saqlash</button>
            </div>
          </div>
        </div>
      )}

      {/* Delete modal */}
      {modal === 'delete' && selected && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40">
          <div className="bg-white rounded-2xl shadow-2xl w-full max-w-sm p-6 space-y-4">
            <div className="w-12 h-12 bg-red-100 rounded-2xl flex items-center justify-center mx-auto">
              <Trash2 className="w-6 h-6 text-red-600" />
            </div>
            <div className="text-center">
              <h2 className="font-bold text-slate-800">Mahsulotni o'chirish</h2>
              <p className="text-sm text-slate-500 mt-1">"{selected.name}" mahsulotini o'chirishni tasdiqlaysizmi?</p>
            </div>
            <div className="flex gap-3">
              <button onClick={close} className="flex-1 px-4 py-2.5 rounded-xl border border-slate-200 text-sm font-medium text-slate-600 hover:bg-slate-50 transition-colors">Bekor</button>
              <button onClick={() => { onDelete(selected.id); close(); }} className="flex-1 px-4 py-2.5 rounded-xl bg-red-600 hover:bg-red-700 text-white text-sm font-medium transition-colors">O'chirish</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
