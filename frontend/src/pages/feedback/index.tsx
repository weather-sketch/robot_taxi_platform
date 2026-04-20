import React, { useEffect, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import {
  Alert,
  Badge,
  Button,
  DatePicker,
  Divider,
  message,
  Modal,
  Select,
  Space,
  Spin,
  Table,
  Tag,
  Typography,
} from "antd";
import type { ColumnsType, TablePaginationConfig } from "antd/es/table";
import dayjs from "dayjs";
import {
  feedbackApi,
  type AIAnalyzeResponse,
  type Feedback,
  type FeedbackFilter,
} from "../../api/feedback";

const { Title } = Typography;
const { RangePicker } = DatePicker;

const SOURCE_LABELS: Record<string, string> = {
  app_rating: "App评价",
  app_feedback: "App反馈",
  customer_service: "客服渠道",
  social_media: "社媒舆情",
};

const CATEGORY_COLORS: Record<string, string> = {
  驾驶行为: "red",
  接驾体验: "orange",
  车内环境: "gold",
  路线规划: "blue",
  安全感知: "magenta",
  费用相关: "green",
  新用户引导: "cyan",
  其他: "default",
};

const CITIES = ["武汉", "北京", "上海", "广州", "深圳", "重庆", "长沙", "苏州"];

export default function FeedbackListPage() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [data, setData] = useState<Feedback[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [filters, setFilters] = useState<FeedbackFilter>(() => {
    const init: FeedbackFilter = {
      page: 1,
      page_size: 20,
      sort_by: "feedback_time",
      sort_order: "desc",
    };
    const rating = searchParams.get("rating");
    if (rating) { init.rating_min = Number(rating); init.rating_max = Number(rating); }
    const category = searchParams.get("ai_category");
    if (category) init.ai_category = category;
    const source = searchParams.get("source");
    if (source) init.source = source;
    const city = searchParams.get("city");
    if (city) init.city = city;
    const route = searchParams.get("route");
    if (route) init.route = route;
    const ticketStatus = searchParams.get("ticket_status");
    if (ticketStatus) init.ticket_status = ticketStatus;
    const priority = searchParams.get("priority");
    if (priority) init.priority = priority;
    const timeStart = searchParams.get("time_start");
    if (timeStart) init.time_start = timeStart;
    const timeEnd = searchParams.get("time_end");
    if (timeEnd) init.time_end = timeEnd;
    return init;
  });

  const fetchData = async () => {
    setLoading(true);
    try {
      const res = await feedbackApi.list(filters);
      setData(res.data.items);
      setTotal(res.data.total);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [filters]);

  const [selectedRowKeys, setSelectedRowKeys] = useState<React.Key[]>([]);
  const [isAllSelected, setIsAllSelected] = useState(false);

  const handleSelectAll = async () => {
    try {
      const { page, page_size, sort_by, sort_order, ...filterParams } = filters;
      const res = await feedbackApi.listIds(filterParams);
      setSelectedRowKeys(res.data.ids);
      setIsAllSelected(true);
    } catch {
      message.error("获取全部ID失败");
    }
  };

  const handleClearSelection = () => {
    setSelectedRowKeys([]);
    setIsAllSelected(false);
  };

  const currentPageAllSelected =
    data.length > 0 && data.every((item) => selectedRowKeys.includes(item.feedback_id));

  const [exporting, setExporting] = useState(false);
  const handleExport = async () => {
    setExporting(true);
    try {
      const exportParams = selectedRowKeys.length > 0
        ? { ids: selectedRowKeys.join(",") }
        : { ...filters };
      const res = await feedbackApi.export(exportParams);
      const url = URL.createObjectURL(res.data);
      const a = document.createElement("a");
      a.href = url;
      a.download = "feedbacks.xlsx";
      a.click();
      URL.revokeObjectURL(url);
      message.success("导出成功");
    } catch {
      message.error("导出失败");
    } finally {
      setExporting(false);
    }
  };

  const [analyzing, setAnalyzing] = useState(false);
  const [summaryVisible, setSummaryVisible] = useState(false);
  const [summary, setSummary] = useState<AIAnalyzeResponse | null>(null);

  const handleAIAnalyze = async () => {
    if (selectedRowKeys.length === 0) {
      message.warning("请先选择要分析的反馈");
      return;
    }
    setAnalyzing(true);
    setSummaryVisible(true);
    setSummary(null);
    try {
      const res = await feedbackApi.aiAnalyze(selectedRowKeys as string[]);
      console.log("AI analyze response:", res.data);
      setSummary(res.data);
    } catch (err: unknown) {
      const axiosErr = err as { response?: { status?: number; data?: { detail?: string } } };
      if (axiosErr.response?.status === 403) {
        message.error("权限不足，请使用管理员或分析师账号");
      } else {
        message.error(axiosErr.response?.data?.detail || "AI分析失败，请稍后重试");
      }
      setSummaryVisible(false);
    } finally {
      setAnalyzing(false);
    }
  };

  const columns: ColumnsType<Feedback> = [
    {
      title: "反馈ID",
      dataIndex: "feedback_id",
      width: 120,
      render: (id: string) => (
        <a onClick={() => navigate(`/feedbacks/${id}`)}>{id}</a>
      ),
    },
    {
      title: "评分",
      dataIndex: "rating",
      width: 80,
      render: (r: number) => <span style={{ fontWeight: 500 }}>{r}</span>,
      sorter: true,
    },
    {
      title: "反馈内容",
      dataIndex: "feedback_text",
      ellipsis: true,
    },
    {
      title: "分类",
      dataIndex: "ai_category",
      width: 100,
      render: (cat: string | null) =>
        cat ? <Tag color={CATEGORY_COLORS[cat]}>{cat}</Tag> : <Tag>未分类</Tag>,
    },
    {
      title: "城市",
      dataIndex: "city",
      width: 80,
    },
    {
      title: "路线",
      dataIndex: "route",
      width: 140,
      ellipsis: true,
    },
    {
      title: "来源",
      dataIndex: "source",
      width: 90,
      render: (s: string) => SOURCE_LABELS[s] || s,
    },
    {
      title: "工单",
      dataIndex: "ticket_biz_id",
      width: 100,
      render: (bizId: string | null, record: Feedback) =>
        bizId ? (
          <a onClick={() => navigate(`/feedbacks/${record.feedback_id}`)}>
            <Badge status="processing" text={bizId} />
          </a>
        ) : (
          <Badge status="default" text="无" />
        ),
    },
    {
      title: "反馈时间",
      dataIndex: "feedback_time",
      width: 160,
      render: (t: string) => dayjs(t).format("YYYY-MM-DD HH:mm"),
      sorter: true,
    },
  ];

  const handleTableChange = (pagination: TablePaginationConfig, _: unknown, sorter: unknown) => {
    const s = sorter as { field?: string; order?: string };
    setFilters((prev) => ({
      ...prev,
      page: pagination.current || 1,
      page_size: pagination.pageSize || 20,
      sort_by: s.field || prev.sort_by,
      sort_order: s.order === "ascend" ? "asc" : "desc",
    }));
  };

  return (
    <div>
      <Title level={4} style={{ marginBottom: 16 }}>
        反馈管理
      </Title>

      {/* Filters */}
      <Space wrap style={{ marginBottom: 16 }}>
        <Select
          allowClear
          placeholder="评分"
          style={{ width: 100 }}
          value={filters.rating_min ?? undefined}
          options={[1, 2, 3, 4, 5].map((v) => ({ label: `${v} 星`, value: v }))}
          onChange={(v) =>
            setFilters((prev) => ({ ...prev, rating_min: v, rating_max: v, page: 1 }))
          }
        />
        <Select
          allowClear
          placeholder="分类"
          style={{ width: 120 }}
          value={filters.ai_category ?? undefined}
          options={Object.keys(CATEGORY_COLORS).map((c) => ({ label: c, value: c }))}
          onChange={(v) => setFilters((prev) => ({ ...prev, ai_category: v, page: 1 }))}
        />
        <Select
          allowClear
          placeholder="来源"
          style={{ width: 120 }}
          value={filters.source ?? undefined}
          options={Object.entries(SOURCE_LABELS).map(([k, v]) => ({ label: v, value: k }))}
          onChange={(v) => setFilters((prev) => ({ ...prev, source: v, page: 1 }))}
        />
        <Select
          allowClear
          placeholder="城市"
          style={{ width: 100 }}
          value={filters.city ?? undefined}
          options={CITIES.map((c) => ({ label: c, value: c }))}
          onChange={(v) =>
            setFilters((prev) => ({ ...prev, city: v, page: 1 }))
          }
        />
        <RangePicker
          onChange={(_, dateStrings) =>
            setFilters((prev) => ({
              ...prev,
              time_start: dateStrings[0] || undefined,
              time_end: dateStrings[1] || undefined,
              page: 1,
            }))
          }
        />
        <Button onClick={() => setFilters({ page: 1, page_size: 20 })}>重置</Button>
        <Button type="primary" loading={exporting} onClick={handleExport}>
          {selectedRowKeys.length > 0 ? `导出选中(${selectedRowKeys.length})` : "导出Excel"}
        </Button>
        <Button
          loading={analyzing}
          onClick={handleAIAnalyze}
          disabled={selectedRowKeys.length === 0}
        >
          AI分析{selectedRowKeys.length > 0 ? `(${selectedRowKeys.length})` : ""}
        </Button>
      </Space>

      {selectedRowKeys.length > 0 && (
        <Alert
          type="info"
          showIcon
          style={{ marginBottom: 16 }}
          message={
            <span>
              {isAllSelected
                ? `已选择全部 ${selectedRowKeys.length} 条反馈`
                : `已选择当前页 ${selectedRowKeys.length} 条`}
              {!isAllSelected && currentPageAllSelected && total > data.length && (
                <a onClick={handleSelectAll} style={{ marginLeft: 8 }}>
                  选择全部 {total} 条
                </a>
              )}
              <a onClick={handleClearSelection} style={{ marginLeft: 8 }}>
                清除选择
              </a>
            </span>
          }
        />
      )}

      <Table
        rowKey="feedback_id"
        columns={columns}
        dataSource={data}
        loading={loading}
        rowSelection={{
          selectedRowKeys,
          onChange: (keys) => {
            setSelectedRowKeys(keys);
            setIsAllSelected(false);
          },
        }}
        pagination={{
          current: filters.page,
          pageSize: filters.page_size,
          total,
          showSizeChanger: true,
          showTotal: (t) => `共 ${t} 条`,
        }}
        onChange={handleTableChange}
        scroll={{ x: 1100 }}
      />

      <Modal
        title="AI 反馈分析"
        open={summaryVisible}
        onCancel={() => setSummaryVisible(false)}
        footer={null}
        width={700}
      >
        {analyzing ? (
          <div style={{ textAlign: "center", padding: 48 }}>
            <Spin size="large" />
            <div style={{ marginTop: 16, color: "#999" }}>
              正在分析 {selectedRowKeys.length} 条反馈...
            </div>
          </div>
        ) : summary ? (
          <div>
            <Typography.Text type="secondary">
              共分析 {summary.feedback_count} 条反馈
            </Typography.Text>
            <Divider />
            <Typography.Title level={5}>主要问题</Typography.Title>
            <ul>
              {(summary.summary?.major_problems ?? []).map((item, i) => (
                <li key={i}>{item}</li>
              ))}
            </ul>
            <Typography.Title level={5}>反馈主题</Typography.Title>
            <ul>
              {(summary.summary?.feedback_themes ?? []).map((item, i) => (
                <li key={i}>{item}</li>
              ))}
            </ul>
            <Typography.Title level={5}>改进建议</Typography.Title>
            <ul>
              {(summary.summary?.action_suggestions ?? []).map((item, i) => (
                <li key={i}>{item}</li>
              ))}
            </ul>
            <Typography.Title level={5}>总体趋势</Typography.Title>
            <Typography.Paragraph>
              {summary.summary?.trend_summary ?? "暂无趋势分析"}
            </Typography.Paragraph>
          </div>
        ) : (
          <div style={{ textAlign: "center", padding: 48, color: "#999" }}>
            暂无分析结果
          </div>
        )}
      </Modal>
    </div>
  );
}
