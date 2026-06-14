import { useState, useCallback } from 'react';
import { useAuth } from './context/AuthContext';
import { AuthRouter } from './components/auth/AuthRouter';
import { Layout } from './components/Layout';
import { Dashboard } from './components/Dashboard';
import { Products } from './components/Products';
import { Customers } from './components/Customers';
import { Sales } from './components/Sales';
import { Reports } from './components/Reports';
import { Settings } from './components/Settings';
import type { Product, Customer, Order, StoreSettings } from './types';
import {
  products as initProducts,
  customers as initCustomers,
  orders as initOrders,
  notifications as initNotifications,
  storeSettings as initSettings,
} from './data/mockData';

export type PageKey = 'dashboard' | 'products' | 'customers' | 'sales' | 'reports' | 'settings';

let nextId = 100;
const genId = (prefix: string) => `${prefix}${++nextId}`;

export default function App() {
  const [page, setPage] = useState<PageKey>('dashboard');
  const [products, setProducts] = useState<Product[]>(initProducts);
  const [customers, setCustomers] = useState<Customer[]>(initCustomers);
  const [orders, setOrders] = useState<Order[]>(initOrders);
  const [settings, setSettings] = useState<StoreSettings>(initSettings);
  const [notifications] = useState(initNotifications);

  const addProduct = useCallback((data: Omit<Product, 'id'>) => {
    setProducts(prev => [{ ...data, id: genId('p') }, ...prev]);
  }, []);
  const editProduct = useCallback((updated: Product) => {
    setProducts(prev => prev.map(p => p.id === updated.id ? updated : p));
  }, []);
  const deleteProduct = useCallback((id: string) => {
    setProducts(prev => prev.filter(p => p.id !== id));
  }, []);

  const addCustomer = useCallback((data: Omit<Customer, 'id'>) => {
    setCustomers(prev => [{ ...data, id: genId('c') }, ...prev]);
  }, []);
  const editCustomer = useCallback((updated: Customer) => {
    setCustomers(prev => prev.map(c => c.id === updated.id ? updated : c));
  }, []);
  const deleteCustomer = useCallback((id: string) => {
    setCustomers(prev => prev.filter(c => c.id !== id));
  }, []);

  const addOrder = useCallback((data: Omit<Order, 'id'>) => {
    const newOrder: Order = { ...data, id: genId('o') };
    setOrders(prev => [newOrder, ...prev]);
    if (data.customerId) {
      setCustomers(prev => prev.map(c =>
        c.id === data.customerId
          ? { ...c, totalOrders: c.totalOrders + 1, totalSpent: c.totalSpent + data.total }
          : c
      ));
    }
    data.items.forEach(item => {
      setProducts(prev => prev.map(p => {
        if (p.id === item.productId) {
          const newStock = Math.max(0, p.stock - item.qty);
          return { ...p, stock: newStock, status: newStock === 0 ? 'out_of_stock' : p.status };
        }
        return p;
      }));
    });
  }, []);

  const { isAuthenticated } = useAuth();
  if (!isAuthenticated) return <AuthRouter />;

  return (
    <Layout currentPage={page} onNavigate={setPage} notifications={notifications}>
      {page === 'dashboard' && (
        <Dashboard products={products} customers={customers} orders={orders} onNavigate={setPage} />
      )}
      {page === 'products' && (
        <Products products={products} onAdd={addProduct} onEdit={editProduct} onDelete={deleteProduct} />
      )}
      {page === 'customers' && (
        <Customers customers={customers} orders={orders} onAdd={addCustomer} onEdit={editCustomer} onDelete={deleteCustomer} />
      )}
      {page === 'sales' && (
        <Sales orders={orders} products={products} customers={customers} onAdd={addOrder} />
      )}
      {page === 'reports' && (
        <Reports orders={orders} products={products} customers={customers} />
      )}
      {page === 'settings' && (
        <Settings settings={settings} onSave={setSettings} />
      )}
    </Layout>
  );
}
