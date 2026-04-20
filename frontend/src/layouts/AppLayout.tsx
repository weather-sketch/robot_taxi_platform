import {
  BarChartOutlined,
  CommentOutlined,
  FileTextOutlined,
  LogoutOutlined,
} from "@ant-design/icons";
import { Layout, Menu, Button, Avatar, Dropdown, Spin } from "antd";
import { Navigate, Outlet, useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../utils/auth";

const { Header, Sider, Content } = Layout;

const menuItems = [
  { key: "/dashboard", icon: <BarChartOutlined />, label: "数据仪表盘" },
  { key: "/feedbacks", icon: <CommentOutlined />, label: "反馈管理" },
  { key: "/tickets", icon: <FileTextOutlined />, label: "工单管理" },
];

export default function AppLayout() {
  const { user, loading, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  if (loading) {
    return (
      <div style={{ display: "flex", justifyContent: "center", alignItems: "center", height: "100vh" }}>
        <Spin size="large" />
      </div>
    );
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  const roleLabels: Record<string, string> = {
    admin: "管理员",
    supervisor: "运营主管",
    operator: "运营人员",
    analyst: "分析师",
  };

  return (
    <Layout style={{ minHeight: "100vh" }}>
      <Sider width={200} theme="light">
        <div
          style={{
            height: 64,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            fontWeight: 700,
            fontSize: 16,
            borderBottom: "1px solid #f0f0f0",
          }}
        >
          Robotaxi 反馈平台
        </div>
        <Menu
          mode="inline"
          selectedKeys={[location.pathname]}
          items={menuItems}
          onClick={({ key }) => navigate(key)}
          style={{ borderRight: 0 }}
        />
      </Sider>
      <Layout>
        <Header
          style={{
            background: "#fff",
            padding: "0 24px",
            display: "flex",
            justifyContent: "flex-end",
            alignItems: "center",
            borderBottom: "1px solid #f0f0f0",
          }}
        >
          <Dropdown
            menu={{
              items: [
                {
                  key: "logout",
                  icon: <LogoutOutlined />,
                  label: "退出登录",
                  onClick: () => {
                    logout();
                    navigate("/login");
                  },
                },
              ],
            }}
          >
            <Button type="text">
              <Avatar size="small" style={{ backgroundColor: "#1677ff", marginRight: 8 }}>
                {user.display_name[0]}
              </Avatar>
              {user.display_name}
              <span style={{ color: "#999", marginLeft: 8, fontSize: 12 }}>
                {roleLabels[user.role] || user.role}
              </span>
            </Button>
          </Dropdown>
        </Header>
        <Content style={{ margin: 24, padding: 24, background: "#fff", borderRadius: 8 }}>
          <Outlet />
        </Content>
      </Layout>
    </Layout>
  );
}
