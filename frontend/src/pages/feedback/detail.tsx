import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import {
  Button,
  Card,
  Col,
  Descriptions,
  Divider,
  message,
  Modal,
  Rate,
  Row,
  Select,
  Tag,
  Timeline,
  Typography,
} from "antd";
import dayjs from "dayjs";
import { feedbackApi, ticketApi, type Feedback, type Ticket } from "../../api/feedback";

const { Title, Paragraph } = Typography;

const PRIORITY_COLORS: Record<string, string> = {
  P0: "#003a8c",
  P1: "#0958d9",
  P2: "#4096ff",
  P3: "#91caff",
};

const STATUS_LABELS: Record<string, string> = {
  pending: "待处理",
  processing: "处理中",
  resolved: "已解决",
  closed: "已关闭",
};

const SLA_COLORS: Record<string, string> = {
  normal: "#1677ff",
  warning: "#69c0ff",
  overdue: "#003a8c",
};

const ASSIGNEE_NAMES: Record<string, string> = {
  op01: "李明",
  op02: "王芳",
  supervisor01: "张华",
  admin: "管理员",
  system: "系统",
};

const displayName = (username: string) => ASSIGNEE_NAMES[username] || username;

export default function FeedbackDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [feedback, setFeedback] = useState<Feedback | null>(null);
  const [ticket, setTicket] = useState<Ticket | null>(null);
  const [loading, setLoading] = useState(true);
  const [createModalOpen, setCreateModalOpen] = useState(false);
  const [newPriority, setNewPriority] = useState<string>("P2");

  const fetchData = async () => {
    if (!id) return;
    setLoading(true);
    try {
      const fbRes = await feedbackApi.getById(id);
      setFeedback(fbRes.data);
      if (fbRes.data.ticket_biz_id) {
        try {
          const tkRes = await ticketApi.getById(fbRes.data.ticket_biz_id);
          setTicket(tkRes.data);
        } catch {
          // ticket fetch failed, ignore
        }
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [id]);

  const handleCreateTicket = async () => {
    if (!feedback) return;
    try {
      const res = await ticketApi.create({
        feedback_id: feedback.feedback_id,
        priority: newPriority as "P0" | "P1" | "P2" | "P3",
      });
      setTicket(res.data);
      setCreateModalOpen(false);
      message.success("工单创建成功");
      fetchData();
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
      message.error(msg || "创建失败");
    }
  };

  if (loading || !feedback) {
    return null;
  }

  return (
    <div>
      <Button type="link" onClick={() => navigate(-1)} style={{ padding: 0, marginBottom: 16 }}>
        ← 返回列表
      </Button>
      <Title level={4}>反馈详情 {feedback.feedback_id}</Title>

      <Row gutter={24}>
        <Col span={16}>
          {/* Basic Info */}
          <Card title="基础信息" style={{ marginBottom: 16 }}>
            <Descriptions column={2}>
              <Descriptions.Item label="用户ID">{feedback.user_id}</Descriptions.Item>
              <Descriptions.Item label="行程ID">{feedback.trip_id}</Descriptions.Item>
              <Descriptions.Item label="车辆ID">{feedback.vehicle_id}</Descriptions.Item>
              <Descriptions.Item label="评分">
                <Rate disabled value={feedback.rating} style={{ fontSize: 14 }} />
                <span style={{ marginLeft: 8 }}>{feedback.rating} 星</span>
              </Descriptions.Item>
              <Descriptions.Item label="城市">{feedback.city}</Descriptions.Item>
              <Descriptions.Item label="路线">{feedback.route}</Descriptions.Item>
              <Descriptions.Item label="行程时间">
                {dayjs(feedback.trip_time).format("YYYY-MM-DD HH:mm")}
              </Descriptions.Item>
              <Descriptions.Item label="行程时长">
                {Math.round(feedback.trip_duration / 60)} 分钟
              </Descriptions.Item>
              <Descriptions.Item label="反馈时间">
                {dayjs(feedback.feedback_time).format("YYYY-MM-DD HH:mm")}
              </Descriptions.Item>
              <Descriptions.Item label="来源">{feedback.source}</Descriptions.Item>
            </Descriptions>
          </Card>

          {/* Feedback Text */}
          <Card title="反馈内容" style={{ marginBottom: 16 }}>
            <Paragraph>{feedback.feedback_text}</Paragraph>
          </Card>

          {/* AI Analysis */}
          <Card title="AI 分析" style={{ marginBottom: 16 }}>
            <Descriptions column={2}>
              <Descriptions.Item label="分类">
                {feedback.ai_category ? (
                  <Tag color="blue">{feedback.ai_category}</Tag>
                ) : (
                  <Tag>未分类</Tag>
                )}
              </Descriptions.Item>
              <Descriptions.Item label="置信度">
                {feedback.ai_confidence != null
                  ? `${(feedback.ai_confidence * 100).toFixed(0)}%`
                  : "-"}
              </Descriptions.Item>
              <Descriptions.Item label="AI 状态">{feedback.ai_status}</Descriptions.Item>
              <Descriptions.Item label="聚类ID">
                {feedback.cluster_id || "-"}
              </Descriptions.Item>
            </Descriptions>
          </Card>
        </Col>

        <Col span={8}>
          {/* Ticket Info */}
          <Card
            title="工单信息"
            extra={
              !feedback.ticket_id && (
                <Button type="primary" size="small" onClick={() => setCreateModalOpen(true)}>
                  创建工单
                </Button>
              )
            }
          >
            {ticket ? (
              <>
                <Descriptions column={1} size="small">
                  <Descriptions.Item label="工单号">{ticket.ticket_id}</Descriptions.Item>
                  <Descriptions.Item label="优先级">
                    <Tag color={PRIORITY_COLORS[ticket.priority]}>{ticket.priority}</Tag>
                  </Descriptions.Item>
                  <Descriptions.Item label="状态">
                    {STATUS_LABELS[ticket.status] || ticket.status}
                  </Descriptions.Item>
                  <Descriptions.Item label="负责人">
                    {ticket.assignee ? displayName(ticket.assignee) : "未分派"}
                  </Descriptions.Item>
                  <Descriptions.Item label="SLA 状态">
                    <Tag color={SLA_COLORS[ticket.sla_status]}>{ticket.sla_status}</Tag>
                  </Descriptions.Item>
                </Descriptions>

                {ticket.logs.length > 0 && (
                  <>
                    <Divider />
                    <Title level={5}>操作日志</Title>
                    <Timeline
                      items={ticket.logs.map((log) => ({
                        children: (
                          <div>
                            <div>
                              <strong>{displayName(log.operator)}</strong> — {log.action}
                            </div>
                            {log.detail && <div style={{ color: "#666" }}>{log.detail}</div>}
                            <div style={{ color: "#999", fontSize: 12 }}>
                              {dayjs(log.created_at).format("YYYY-MM-DD HH:mm")}
                            </div>
                          </div>
                        ),
                      }))}
                    />
                  </>
                )}
              </>
            ) : feedback.ticket_id ? (
              <div style={{ color: "#999" }}>工单已关联 (ID: {feedback.ticket_id})</div>
            ) : (
              <div style={{ color: "#999" }}>暂无工单</div>
            )}
          </Card>
        </Col>
      </Row>

      {/* Create Ticket Modal */}
      <Modal
        title="创建工单"
        open={createModalOpen}
        onOk={handleCreateTicket}
        onCancel={() => setCreateModalOpen(false)}
      >
        <div style={{ marginBottom: 16 }}>
          <div style={{ marginBottom: 8 }}>优先级：</div>
          <Select
            value={newPriority}
            onChange={setNewPriority}
            style={{ width: "100%" }}
            options={[
              { label: "P0 — 安全/SOS", value: "P0" },
              { label: "P1 — 严重体验问题", value: "P1" },
              { label: "P2 — 一般差评", value: "P2" },
              { label: "P3 — 建议类反馈", value: "P3" },
            ]}
          />
        </div>
      </Modal>
    </div>
  );
}
