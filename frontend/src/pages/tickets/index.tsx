import React, { useEffect, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import {
  Badge,
  Button,
  Input,
  message,
  Modal,
  Select,
  Space,
  Table,
  Tag,
  Typography,
} from "antd";
import type { ColumnsType } from "antd/es/table";
import dayjs from "dayjs";
import { ticketApi, type Ticket, type TicketUpdateParams } from "../../api/feedback";

const { Title } = Typography;

const ASSIGNEE_NAMES: Record<string, string> = {
  op01: "李明",
  op02: "王芳",
  supervisor01: "张华",
  admin: "管理员",
};

const PRIORITY_COLORS: Record<string, string> = {
  P0: "#003a8c",
  P1: "#0958d9",
  P2: "#4096ff",
  P3: "#91caff",
};

const STATUS_MAP: Record<string, { label: string; color: string }> = {
  pending: { label: "待处理", color: "#bae7ff" },
  processing: { label: "处理中", color: "#1677ff" },
  resolved: { label: "已解决", color: "#0050b3" },
  closed: { label: "已关闭", color: "#d6e4ff" },
};

const SLA_LABELS: Record<string, string> = {
  normal: "正常",
  warning: "即将超时",
  overdue: "已超时",
};

const SLA_COLORS: Record<string, string> = {
  normal: "#1677ff",
  warning: "#69c0ff",
  overdue: "#003a8c",
};

interface TicketFilters {
  status?: string;
  priority?: string;
  assignee?: string;
  sla_status?: string;
  page: number;
  page_size: number;
}

export default function TicketListPage() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [data, setData] = useState<Ticket[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [filters, setFilters] = useState<TicketFilters>(() => {
    const init: TicketFilters = { page: 1, page_size: 20 };
    const status = searchParams.get("status");
    if (status) init.status = status;
    const priority = searchParams.get("priority");
    if (priority) init.priority = priority;
    const assignee = searchParams.get("assignee");
    if (assignee) init.assignee = assignee;
    const slaStatus = searchParams.get("sla_status");
    if (slaStatus) init.sla_status = slaStatus;
    return init;
  });
  const [selectedRowKeys, setSelectedRowKeys] = useState<React.Key[]>([]);
  const [editModal, setEditModal] = useState<{ ticket: Ticket; visible: boolean }>({
    ticket: {} as Ticket,
    visible: false,
  });
  const [editForm, setEditForm] = useState<TicketUpdateParams>({});

  const fetchData = async () => {
    setLoading(true);
    try {
      const res = await ticketApi.list({
        status: filters.status,
        priority: filters.priority,
        assignee: filters.assignee,
        sla_status: filters.sla_status,
        page: filters.page,
        page_size: filters.page_size,
      });
      setData(res.data.items);
      setTotal(res.data.total);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [filters]);

  const [exporting, setExporting] = useState(false);
  const handleExport = async () => {
    setExporting(true);
    try {
      const exportParams = selectedRowKeys.length > 0
        ? { ids: selectedRowKeys.join(",") }
        : {
            status: filters.status,
            priority: filters.priority,
            assignee: filters.assignee,
            sla_status: filters.sla_status,
          };
      const res = await ticketApi.export(exportParams);
      const url = URL.createObjectURL(res.data);
      const a = document.createElement("a");
      a.href = url;
      a.download = "tickets.xlsx";
      a.click();
      URL.revokeObjectURL(url);
      message.success("导出成功");
    } catch {
      message.error("导出失败");
    } finally {
      setExporting(false);
    }
  };

  const handleUpdate = async () => {
    try {
      await ticketApi.update(editModal.ticket.ticket_id, editForm);
      message.success("更新成功");
      setEditModal({ ticket: {} as Ticket, visible: false });
      setEditForm({});
      fetchData();
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
      message.error(msg || "更新失败");
    }
  };

  const columns: ColumnsType<Ticket> = [
    {
      title: "工单号",
      dataIndex: "ticket_id",
      width: 120,
    },
    {
      title: "优先级",
      dataIndex: "priority",
      width: 80,
      render: (p: string) => <Tag color={PRIORITY_COLORS[p]}>{p}</Tag>,
    },
    {
      title: "状态",
      dataIndex: "status",
      width: 90,
      render: (s: string) => (
        <Badge status={STATUS_MAP[s]?.color as "processing"} text={STATUS_MAP[s]?.label || s} />
      ),
    },
    {
      title: "负责人",
      dataIndex: "assignee",
      width: 100,
      render: (a: string | null) => (a ? ASSIGNEE_NAMES[a] || a : "未分派"),
    },
    {
      title: "SLA 状态",
      dataIndex: "sla_status",
      width: 100,
      render: (s: string) => <Tag color={SLA_COLORS[s]}>{SLA_LABELS[s] || s}</Tag>,
    },
    {
      title: "反馈内容",
      key: "feedback_text",
      ellipsis: true,
      render: (_: unknown, record: Ticket) => record.feedback?.feedback_text || "-",
    },
    {
      title: "创建时间",
      dataIndex: "created_at",
      width: 160,
      render: (t: string) => dayjs(t).format("YYYY-MM-DD HH:mm"),
    },
    {
      title: "操作",
      width: 140,
      render: (_: unknown, record: Ticket) => (
        <Space>
          <Button
            type="link"
            size="small"
            onClick={() => {
              if (record.feedback?.feedback_id) {
                navigate(`/feedbacks/${record.feedback.feedback_id}`);
              }
            }}
          >
            查看反馈
          </Button>
          <Button
            type="link"
            size="small"
            onClick={() => {
              setEditModal({ ticket: record, visible: true });
              setEditForm({});
            }}
          >
            处理
          </Button>
        </Space>
      ),
    },
  ];

  return (
    <div>
      <Title level={4} style={{ marginBottom: 16 }}>
        工单管理
      </Title>

      <Space wrap style={{ marginBottom: 16 }}>
        <Select
          allowClear
          placeholder="状态"
          style={{ width: 110 }}
          value={filters.status ?? undefined}
          options={[
            { label: "待处理", value: "pending" },
            { label: "处理中", value: "processing" },
            { label: "已解决", value: "resolved" },
            { label: "已关闭", value: "closed" },
          ]}
          onChange={(v) => setFilters((prev) => ({ ...prev, status: v, page: 1 }))}
        />
        <Select
          allowClear
          placeholder="优先级"
          style={{ width: 100 }}
          value={filters.priority ?? undefined}
          options={[
            { label: "P0", value: "P0" },
            { label: "P1", value: "P1" },
            { label: "P2", value: "P2" },
            { label: "P3", value: "P3" },
          ]}
          onChange={(v) => setFilters((prev) => ({ ...prev, priority: v, page: 1 }))}
        />
        <Select
          allowClear
          placeholder="负责人"
          style={{ width: 120 }}
          value={filters.assignee ?? undefined}
          options={Object.entries(ASSIGNEE_NAMES).map(([k, v]) => ({
            label: v,
            value: k,
          }))}
          onChange={(v) => setFilters((prev) => ({ ...prev, assignee: v, page: 1 }))}
        />
        <Select
          allowClear
          placeholder="SLA 状态"
          style={{ width: 120 }}
          value={filters.sla_status ?? undefined}
          options={[
            { label: "正常", value: "normal" },
            { label: "即将超时", value: "warning" },
            { label: "已超时", value: "overdue" },
          ]}
          onChange={(v) => setFilters((prev) => ({ ...prev, sla_status: v, page: 1 }))}
        />
        <Button onClick={() => setFilters({ page: 1, page_size: 20 })}>重置</Button>
        <Button type="primary" loading={exporting} onClick={handleExport}>
          {selectedRowKeys.length > 0 ? `导出选中(${selectedRowKeys.length})` : "导出Excel"}
        </Button>
      </Space>

      <Table
        rowKey="ticket_id"
        columns={columns}
        dataSource={data}
        loading={loading}
        rowSelection={{
          selectedRowKeys,
          onChange: (keys) => setSelectedRowKeys(keys),
        }}
        pagination={{
          current: filters.page,
          pageSize: filters.page_size,
          total,
          showSizeChanger: true,
          showTotal: (t) => `共 ${t} 条`,
          onChange: (p, ps) => {
            setFilters((prev) => ({ ...prev, page: p, page_size: ps }));
          },
        }}
        scroll={{ x: 1000 }}
      />

      <Modal
        title={`处理工单 ${editModal.ticket.ticket_id}`}
        open={editModal.visible}
        onOk={handleUpdate}
        onCancel={() => setEditModal({ ticket: {} as Ticket, visible: false })}
        width={500}
      >
        <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
          <div>
            <div style={{ marginBottom: 4 }}>状态：</div>
            <Select
              allowClear
              placeholder="变更状态"
              style={{ width: "100%" }}
              onChange={(v) => setEditForm((prev) => ({ ...prev, status: v }))}
              options={[
                { label: "处理中", value: "processing" },
                { label: "已解决", value: "resolved" },
                { label: "已关闭", value: "closed" },
              ]}
            />
          </div>
          <div>
            <div style={{ marginBottom: 4 }}>优先级：</div>
            <Select
              allowClear
              placeholder="变更优先级"
              style={{ width: "100%" }}
              onChange={(v) => setEditForm((prev) => ({ ...prev, priority: v }))}
              options={[
                { label: "P0", value: "P0" },
                { label: "P1", value: "P1" },
                { label: "P2", value: "P2" },
                { label: "P3", value: "P3" },
              ]}
            />
          </div>
          <div>
            <div style={{ marginBottom: 4 }}>负责人：</div>
            <Select
              allowClear
              placeholder="分派给"
              style={{ width: "100%" }}
              onChange={(v) => setEditForm((prev) => ({ ...prev, assignee: v }))}
              options={Object.entries(ASSIGNEE_NAMES).map(([k, v]) => ({
                label: v,
                value: k,
              }))}
            />
          </div>
          <div>
            <div style={{ marginBottom: 4 }}>处理方式：</div>
            <Select
              allowClear
              placeholder="处理方式"
              style={{ width: "100%" }}
              onChange={(v) => setEditForm((prev) => ({ ...prev, processing_result: v }))}
              options={[
                { label: "补偿", value: "补偿" },
                { label: "技术问题", value: "技术问题" },
                { label: "无需处理", value: "无需处理" },
                { label: "其他", value: "其他" },
              ]}
            />
          </div>
          <div>
            <div style={{ marginBottom: 4 }}>处理备注：</div>
            <Input.TextArea
              rows={3}
              placeholder="输入处理备注..."
              onChange={(e) =>
                setEditForm((prev) => ({ ...prev, processing_note: e.target.value }))
              }
            />
          </div>
        </div>
      </Modal>
    </div>
  );
}
