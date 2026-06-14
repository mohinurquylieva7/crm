import type { Product, Customer, Order, Notification, StoreSettings } from '../types';

export const products: Product[] = [
  { id: 'p1', name: "Erkaklar ko'ylagi (slim fit)", category: "Ko'ylak", brand: 'Mango', sizes: ['S','M','L','XL'], colors: ['Oq',"Ko'k",'Qora'], buyPrice: 85000, sellPrice: 150000, stock: 24, minStock: 5, status: 'active', addedDate: '2025-01-10' },
  { id: 'p2', name: 'Ayollar bluzkasi', category: 'Bluzka', brand: 'Zara', sizes: ['XS','S','M','L'], colors: ['Pushti','Sariq','Oq'], buyPrice: 70000, sellPrice: 130000, stock: 18, minStock: 5, status: 'active', addedDate: '2025-01-15' },
  { id: 'p3', name: 'Jins shim (straight)', category: 'Shim', brand: 'Levis', sizes: ['28','30','32','34','36'], colors: ["Ko'k",'Qora','Kulrang'], buyPrice: 120000, sellPrice: 220000, stock: 3, minStock: 5, status: 'active', addedDate: '2025-01-20' },
  { id: 'p4', name: 'Sport kurtka', category: 'Kurtka', brand: 'Nike', sizes: ['S','M','L','XL','XXL'], colors: ['Qora','Qizil',"To'q sariq"], buyPrice: 180000, sellPrice: 320000, stock: 12, minStock: 3, status: 'active', addedDate: '2025-02-01' },
  { id: 'p5', name: "Ayollar ko'ylagi (floral)", category: "Ko'ylak", brand: 'H&M', sizes: ['XS','S','M','L'], colors: ['Guldor'], buyPrice: 95000, sellPrice: 170000, stock: 0, minStock: 5, status: 'out_of_stock', addedDate: '2025-02-05' },
  { id: 'p6', name: 'Erkaklar futbolkasi', category: 'Futbolka', brand: 'Adidas', sizes: ['S','M','L','XL','XXL'], colors: ['Oq','Qora','Kulrang',"Ko'k"], buyPrice: 45000, sellPrice: 89000, stock: 40, minStock: 10, status: 'active', addedDate: '2025-02-10' },
  { id: 'p7', name: 'Qishki palto', category: 'Palto', brand: 'Mango', sizes: ['S','M','L','XL'], colors: ['Kulrang','Qora','Jigarrang'], buyPrice: 350000, sellPrice: 620000, stock: 8, minStock: 3, status: 'active', addedDate: '2025-02-15' },
  { id: 'p8', name: 'Yoga shim', category: 'Shim', brand: 'Nike', sizes: ['XS','S','M','L'], colors: ['Qora',"To'q ko'k",'Binafsha'], buyPrice: 90000, sellPrice: 160000, stock: 22, minStock: 5, status: 'active', addedDate: '2025-03-01' },
];

export const customers: Customer[] = [
  { id: 'c1', firstName: 'Malika', lastName: 'Yusupova', phone: '+998901234567', address: 'Toshkent, Yunusobod', totalOrders: 8, totalSpent: 1240000, discount: 5, addedDate: '2024-11-01' },
  { id: 'c2', firstName: 'Jasur', lastName: 'Toshmatov', phone: '+998912345678', address: "Toshkent, Mirzo Ulug'bek", totalOrders: 3, totalSpent: 450000, discount: 0, addedDate: '2024-12-15' },
  { id: 'c3', firstName: 'Dilnoza', lastName: 'Karimova', phone: '+998934567890', address: 'Samarqand', totalOrders: 12, totalSpent: 2100000, discount: 10, addedDate: '2024-09-20' },
  { id: 'c4', firstName: 'Bobur', lastName: 'Ergashev', phone: '+998945678901', totalOrders: 1, totalSpent: 320000, discount: 0, addedDate: '2025-01-05' },
  { id: 'c5', firstName: 'Shahnoza', lastName: 'Nazarova', phone: '+998956789012', address: 'Toshkent, Chilonzor', totalOrders: 6, totalSpent: 890000, discount: 5, addedDate: '2024-10-30' },
  { id: 'c6', firstName: 'Akbar', lastName: 'Mirzayev', phone: '+998967890123', totalOrders: 2, totalSpent: 270000, discount: 0, addedDate: '2025-02-14' },
];

export const orders: Order[] = [
  {
    id: 'o1', customerId: 'c1', customerName: 'Malika Yusupova',
    items: [{ productId: 'p2', productName: 'Ayollar bluzkasi', size: 'M', color: 'Pushti', qty: 2, unitPrice: 130000, discount: 5 }],
    subtotal: 260000, discount: 13000, total: 247000, paid: 247000, change: 0,
    method: 'card', status: 'completed', date: '2025-06-06', sellerId: 'u1',
  },
  {
    id: 'o2', customerId: 'c3', customerName: 'Dilnoza Karimova',
    items: [
      { productId: 'p4', productName: 'Sport kurtka', size: 'L', color: 'Qora', qty: 1, unitPrice: 320000, discount: 10 },
      { productId: 'p6', productName: 'Erkaklar futbolkasi', size: 'L', color: 'Oq', qty: 2, unitPrice: 89000, discount: 10 },
    ],
    subtotal: 498000, discount: 49800, total: 448200, paid: 450000, change: 1800,
    method: 'cash', status: 'completed', date: '2025-06-06', sellerId: 'u1',
  },
  {
    id: 'o3', customerName: "Noma'lum",
    items: [{ productId: 'p1', productName: "Erkaklar ko'ylagi", size: 'L', color: "Ko'k", qty: 1, unitPrice: 150000, discount: 0 }],
    subtotal: 150000, discount: 0, total: 150000, paid: 150000, change: 0,
    method: 'cash', status: 'completed', date: '2025-06-05', sellerId: 'u1',
  },
  {
    id: 'o4', customerId: 'c5', customerName: 'Shahnoza Nazarova',
    items: [{ productId: 'p7', productName: 'Qishki palto', size: 'S', color: 'Kulrang', qty: 1, unitPrice: 620000, discount: 5 }],
    subtotal: 620000, discount: 31000, total: 589000, paid: 589000, change: 0,
    method: 'transfer', status: 'completed', date: '2025-06-05', sellerId: 'u1',
  },
  {
    id: 'o5', customerId: 'c2', customerName: 'Jasur Toshmatov',
    items: [{ productId: 'p3', productName: 'Jins shim', size: '32', color: 'Qora', qty: 1, unitPrice: 220000, discount: 0 }],
    subtotal: 220000, discount: 0, total: 220000, paid: 220000, change: 0,
    method: 'card', status: 'completed', date: '2025-06-04', sellerId: 'u1',
  },
  {
    id: 'o6', customerName: "Noma'lum",
    items: [{ productId: 'p8', productName: 'Yoga shim', size: 'M', color: 'Qora', qty: 2, unitPrice: 160000, discount: 0 }],
    subtotal: 320000, discount: 0, total: 320000, paid: 300000, change: 0,
    method: 'cash', status: 'pending', date: '2025-06-04', sellerId: 'u1',
  },
];

export const notifications: Notification[] = [
  { id: 'n1', title: 'Stok kam!', message: "Jins shim qoldig'i 3 taga tushdi", type: 'warning', read: false, date: '2025-06-06' },
  { id: 'n2', title: 'Yangi buyurtma', message: "Malika Yusupova 247,000 so'mlik buyurtma berdi", type: 'success', read: false, date: '2025-06-06' },
  { id: 'n3', title: 'Mahsulot tugadi', message: "Ayollar ko'ylagi (floral) ombordan tugadi", type: 'error', read: true, date: '2025-06-05' },
];

export const storeSettings: StoreSettings = {
  id: 's1',
  name: 'Reteake CRM',
  phone: '+998901234567',
  address: 'Toshkent, Chilonzor',
  currency: 'UZS',
  language: 'uz',
  taxPercent: 0,
  receiptFooter: 'Xaridingiz uchun rahmat!',
  subscriptionPlan: 'pro',
  subscriptionExpiry: '2026-01-01',
};
