export type UserRole = 'superadmin' | 'admin' | 'seller' | 'cashier';
export type PaymentMethod = 'cash' | 'card' | 'transfer';
export type ProductStatus = 'active' | 'inactive' | 'out_of_stock';
export type OrderStatus = 'completed' | 'pending' | 'cancelled' | 'refunded';

export interface Product {
  id: string;
  name: string;
  category: string;
  brand: string;
  sizes: string[];          // ['XS','S','M','L','XL']
  colors: string[];         // ['Qora','Oq','Ko\'k']
  buyPrice: number;         // xarid narxi
  sellPrice: number;        // sotuv narxi
  stock: number;            // ombordagi soni
  minStock: number;         // minimal stok (ogohlantirish uchun)
  barcode?: string;
  status: ProductStatus;
  image?: string;
  addedDate: string;
}

export interface Customer {
  id: string;
  firstName: string;
  lastName: string;
  phone: string;
  address?: string;
  birthday?: string;
  totalOrders: number;
  totalSpent: number;
  discount: number;         // % chegirma
  addedDate: string;
  notes?: string;
}

export interface OrderItem {
  productId: string;
  productName: string;
  size: string;
  color: string;
  qty: number;
  unitPrice: number;
  discount: number;
}

export interface Order {
  id: string;
  customerId?: string;
  customerName: string;
  items: OrderItem[];
  subtotal: number;
  discount: number;
  total: number;
  paid: number;
  change: number;
  method: PaymentMethod;
  status: OrderStatus;
  date: string;
  sellerId: string;
  notes?: string;
}

export interface Notification {
  id: string;
  title: string;
  message: string;
  type: 'info' | 'success' | 'warning' | 'error';
  read: boolean;
  date: string;
}

export interface StoreSettings {
  id: string;
  name: string;
  logo?: string;
  phone: string;
  address: string;
  currency: string;
  language: 'uz' | 'ru' | 'en';
  taxPercent: number;
  receiptFooter: string;
  subscriptionPlan: 'free' | 'starter' | 'pro' | 'enterprise';
  subscriptionExpiry: string;
}
