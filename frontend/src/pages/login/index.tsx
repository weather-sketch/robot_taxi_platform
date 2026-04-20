import { LockOutlined, UserOutlined } from "@ant-design/icons";
import { Button, Card, Form, Input, message } from "antd";
import { useNavigate } from "react-router-dom";
import { authApi, type LoginParams } from "../../api/auth";
import { useAuth } from "../../utils/auth";

export default function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [form] = Form.useForm();

  const onFinish = async (values: LoginParams) => {
    try {
      const res = await authApi.login(values);
      await login(res.data.access_token);
      message.success("登录成功");
      navigate("/dashboard", { replace: true });
    } catch {
      message.error("用户名或密码错误");
    }
  };

  return (
    <div
      style={{
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        height: "100vh",
        background: "#f0f2f5",
      }}
    >
      <Card title="Robotaxi 反馈管理平台" style={{ width: 400 }}>
        <Form form={form} onFinish={onFinish} size="large">
          <Form.Item name="username" rules={[{ required: true, message: "请输入用户名" }]}>
            <Input prefix={<UserOutlined />} placeholder="用户名" />
          </Form.Item>
          <Form.Item name="password" rules={[{ required: true, message: "请输入密码" }]}>
            <Input.Password prefix={<LockOutlined />} placeholder="密码" />
          </Form.Item>
          <Form.Item>
            <Button type="primary" htmlType="submit" block>
              登录
            </Button>
          </Form.Item>
          <div style={{ color: "#999", fontSize: 12, textAlign: "center" }}>
            测试账号: admin / admin123
          </div>
        </Form>
      </Card>
    </div>
  );
}
