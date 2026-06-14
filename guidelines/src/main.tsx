import { createRoot } from "react-dom/client";
import App from "./app/App.tsx";
import { AuthProvider } from "./app/context/AuthContext.tsx";
import { LanguageProvider } from "./app/context/LanguageContext.tsx";
import "./styles/index.css";

createRoot(document.getElementById("root")!).render(
  <LanguageProvider>
    <AuthProvider>
      <App />
    </AuthProvider>
  </LanguageProvider>
);
  