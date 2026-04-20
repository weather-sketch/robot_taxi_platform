import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import { ConfigProvider } from "antd";
import zhCN from "antd/locale/zh_CN";
import { AuthProvider } from "./utils/auth";
import AppLayout from "./layouts/AppLayout";
import LoginPage from "./pages/login";
import DashboardPage from "./pages/dashboard";
import FeedbackListPage from "./pages/feedback";
import FeedbackDetailPage from "./pages/feedback/detail";
import TicketListPage from "./pages/tickets";

export default function App() {
  return (
    <ConfigProvider locale={zhCN}>
      <AuthProvider>
        <BrowserRouter>
          <Routes>
            <Route path="/login" element={<LoginPage />} />
            <Route element={<AppLayout />}>
              <Route path="/dashboard" element={<DashboardPage />} />
              <Route path="/feedbacks" element={<FeedbackListPage />} />
              <Route path="/feedbacks/:id" element={<FeedbackDetailPage />} />
              <Route path="/tickets" element={<TicketListPage />} />
            </Route>
            <Route path="*" element={<Navigate to="/dashboard" replace />} />
          </Routes>
        </BrowserRouter>
      </AuthProvider>
    </ConfigProvider>
  );
}
