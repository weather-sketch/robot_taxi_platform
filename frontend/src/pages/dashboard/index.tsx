import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Button, Card, Col, message, Row, Segmented, Spin, Statistic, Typography } from "antd";
import {
  ArrowDownOutlined,
  ArrowUpOutlined,
  CommentOutlined,
  FileTextOutlined,
  SafetyOutlined,
  StarOutlined,
} from "@ant-design/icons";
import ReactECharts from "echarts-for-react";
import {
  dashboardApi,
  type DashboardOverview,
  type TrendData,
  type DistributionData,
  type TicketMetrics,
} from "../../api/dashboard";

const { Title } = Typography;

const clickableCard: React.CSSProperties = { cursor: "pointer" };

export default function DashboardPage() {
  const navigate = useNavigate();
  const [overview, setOverview] = useState<DashboardOverview | null>(null);
  const [trends, setTrends] = useState<TrendData | null>(null);
  const [distribution, setDistribution] = useState<DistributionData | null>(null);
  const [ticketMetrics, setTicketMetrics] = useState<TicketMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [granularity, setGranularity] = useState<string>("day");
  const [reportPeriod, setReportPeriod] = useState<string>("daily");
  const [reportLoading, setReportLoading] = useState(false);
  const [reportContent, setReportContent] = useState<string>("");

  const fetchAll = async () => {
    setLoading(true);
    try {
      const [ov, tr, dist, tm] = await Promise.all([
        dashboardApi.overview(),
        dashboardApi.trends(30, granularity),
        dashboardApi.distribution(),
        dashboardApi.ticketMetrics(),
      ]);
      setOverview(ov.data);
      setTrends(tr.data);
      setDistribution(dist.data);
      setTicketMetrics(tm.data);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAll();
  }, [granularity]);

  const handleGenerateReport = async () => {
    setReportLoading(true);
    setReportContent("");
    try {
      const res = await dashboardApi.aiReport(reportPeriod);
      setReportContent(res.data.report);
    } catch {
      message.error("报告生成失败，请稍后重试");
    } finally {
      setReportLoading(false);
    }
  };

  if (loading || !overview) {
    return <Spin size="large" style={{ display: "block", margin: "100px auto" }} />;
  }

  /* ---------- Trend chart ---------- */
  const trendOption = trends
    ? {
        tooltip: { trigger: "axis" as const },
        legend: { data: ["差评数", "好评率(%)", "平均评分"] },
        xAxis: {
          type: "category" as const,
          data: trends.negative_count.map((p) => p.date),
        },
        yAxis: [
          { type: "value" as const, name: "数量/评分" },
          { type: "value" as const, name: "百分比", axisLabel: { formatter: "{value}%" } },
        ],
        series: [
          {
            name: "差评数",
            type: "bar",
            data: trends.negative_count.map((p) => p.value),
            cursor: "pointer",
          },
          {
            name: "好评率(%)",
            type: "line",
            yAxisIndex: 1,
            data: trends.positive_rate.map((p) => p.value),
          },
          {
            name: "平均评分",
            type: "line",
            data: trends.avg_rating.map((p) => p.value),
          },
        ],
      }
    : {};

  const handleTrendClick = (params: { dataIndex?: number }) => {
    if (!trends || params.dataIndex == null) return;
    const dateStr = trends.negative_count[params.dataIndex]?.date;
    if (dateStr) {
      navigate(`/feedbacks?time_start=${dateStr}&time_end=${dateStr}`);
    }
  };

  /* ---------- Rating pie ---------- */
  const ratingPieOption = distribution
    ? {
        tooltip: { trigger: "item" as const },
        series: [
          {
            type: "pie",
            radius: ["40%", "70%"],
            cursor: "pointer",
            data: distribution.by_rating.map((d) => ({
              name: d.label,
              value: d.count,
            })),
          },
        ],
      }
    : {};

  const handleRatingClick = (params: { name?: string }) => {
    if (!params.name) return;
    const rating = params.name.replace("星", "");
    navigate(`/feedbacks?rating=${rating}`);
  };

  /* ---------- Category bar ---------- */
  const categoryBarOption = distribution
    ? {
        tooltip: { trigger: "axis" as const },
        xAxis: {
          type: "category" as const,
          data: distribution.by_category.map((d) => d.label),
          axisLabel: { rotate: 30 },
        },
        yAxis: { type: "value" as const },
        series: [
          {
            type: "bar",
            data: distribution.by_category.map((d) => d.count),
            itemStyle: { borderRadius: [4, 4, 0, 0] },
            cursor: "pointer",
          },
        ],
      }
    : {};

  const handleCategoryClick = (params: { name?: string }) => {
    if (!params.name) return;
    navigate(`/feedbacks?ai_category=${encodeURIComponent(params.name)}`);
  };

  /* ---------- Route distribution bar ---------- */
  const routeBarOption = distribution
    ? {
        tooltip: { trigger: "axis" as const },
        xAxis: {
          type: "category" as const,
          data: distribution.by_route.map((d) => d.label),
          axisLabel: { rotate: 30 },
        },
        yAxis: { type: "value" as const },
        series: [
          {
            type: "bar",
            data: distribution.by_route.map((d) => d.count),
            itemStyle: { borderRadius: [4, 4, 0, 0] },
            cursor: "pointer",
          },
        ],
      }
    : {};

  const handleRouteClick = (params: { name?: string }) => {
    if (!params.name) return;
    navigate(`/feedbacks?route=${encodeURIComponent(params.name)}`);
  };

  return (
    <div>
      <Title level={4} style={{ marginBottom: 24 }}>
        数据仪表盘
      </Title>

      {/* Metric Cards */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col span={6}>
          <Card hoverable style={clickableCard} onClick={() => navigate("/feedbacks")}>
            <Statistic
              title="总反馈数"
              value={overview.total_feedbacks}
              prefix={<CommentOutlined />}
              suffix={
                <span style={{ fontSize: 12, color: "#999" }}>
                  今日 {overview.total_today}
                </span>
              }
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card hoverable style={clickableCard} onClick={() => navigate("/feedbacks")}>
            <Statistic
              title="平均评分"
              value={overview.avg_rating}
              precision={2}
              prefix={<StarOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card hoverable style={clickableCard} onClick={() => navigate("/tickets")}>
            <Statistic
              title="好评率"
              value={overview.positive_rate}
              precision={1}
              suffix="%"
              prefix={<ArrowUpOutlined style={{ color: "#52c41a" }} />}
            />
            <Statistic
              title="差评率"
              value={overview.negative_rate}
              precision={1}
              suffix="%"
              valueStyle={{ fontSize: 14, color: "#ff4d4f" }}
              prefix={<ArrowDownOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card hoverable style={clickableCard} onClick={() => navigate("/tickets?status=pending")}>
            <Statistic
              title="未关闭工单"
              value={overview.open_tickets}
              prefix={<FileTextOutlined />}
            />
            <Statistic
              title="SLA 达标率"
              value={overview.sla_compliance_rate}
              precision={1}
              suffix="%"
              valueStyle={{ fontSize: 14, color: overview.sla_compliance_rate >= 90 ? "#52c41a" : "#ff4d4f" }}
              prefix={<SafetyOutlined />}
            />
          </Card>
        </Col>
      </Row>

      {/* Trend Chart */}
      <Card
        title="趋势分析"
        extra={
          <Segmented
            options={[
              { label: "按日", value: "day" },
              { label: "按周", value: "week" },
              { label: "按月", value: "month" },
            ]}
            value={granularity}
            onChange={(v) => setGranularity(v as string)}
          />
        }
        style={{ marginBottom: 24 }}
      >
        <ReactECharts
          option={trendOption}
          style={{ height: 350 }}
          onEvents={{ click: handleTrendClick }}
        />
      </Card>

      {/* Distribution Charts */}
      <Row gutter={[16, 16]}>
        <Col span={12}>
          <Card title="评分分布">
            <ReactECharts
              option={ratingPieOption}
              style={{ height: 300 }}
              onEvents={{ click: handleRatingClick }}
            />
          </Card>
        </Col>
        <Col span={12}>
          <Card title="反馈类型分布">
            <ReactECharts
              option={categoryBarOption}
              style={{ height: 300 }}
              onEvents={{ click: handleCategoryClick }}
            />
          </Card>
        </Col>
      </Row>

      {/* Route Distribution */}
      <Card title="路线分布 (Top 10)" style={{ marginTop: 24 }}>
        <ReactECharts
          option={routeBarOption}
          style={{ height: 300 }}
          onEvents={{ click: handleRouteClick }}
        />
      </Card>

      {/* Ticket Metrics */}
      {ticketMetrics && (
        <Card title="工单处理指标" style={{ marginTop: 24 }}>
          <Row gutter={16}>
            {ticketMetrics.by_priority.map((p) => (
              <Col
                span={6}
                key={p.label}
                style={clickableCard}
                onClick={() => navigate(`/tickets?priority=${p.label}`)}
              >
                <Card hoverable size="small" style={{ border: "none" }}>
                  <Statistic title={`${p.label} 工单数`} value={p.count} />
                  <div style={{ fontSize: 12, color: "#999", marginTop: 4 }}>
                    平均解决时长: {ticketMetrics.avg_resolve_time_hours[p.label] ?? "-"}h
                  </div>
                  <div style={{ fontSize: 12, color: "#999" }}>
                    SLA 达标: {ticketMetrics.sla_compliance_by_priority[p.label] ?? "-"}%
                  </div>
                </Card>
              </Col>
            ))}
          </Row>
        </Card>
      )}

      {/* AI Report */}
      <Card
        title="AI 智能报告"
        extra={
          <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
            <Segmented
              options={[
                { label: "按日", value: "daily" },
                { label: "按周", value: "weekly" },
                { label: "按月", value: "monthly" },
              ]}
              value={reportPeriod}
              onChange={(v) => {
                setReportPeriod(v as string);
                setReportContent("");
              }}
            />
            <Button type="primary" loading={reportLoading} onClick={handleGenerateReport}>
              生成报告
            </Button>
          </div>
        }
        style={{ marginTop: 24 }}
      >
        {reportLoading ? (
          <div style={{ textAlign: "center", padding: 48 }}>
            <Spin size="large" />
            <div style={{ marginTop: 16, color: "#999" }}>
              正在生成{reportPeriod === "daily" ? "日" : reportPeriod === "weekly" ? "周" : "月"}报...
            </div>
          </div>
        ) : reportContent ? (
          <Typography.Paragraph
            style={{ whiteSpace: "pre-wrap", lineHeight: 1.8, fontSize: 14 }}
          >
            {reportContent}
          </Typography.Paragraph>
        ) : (
          <div style={{ textAlign: "center", padding: 48, color: "#999" }}>
            请选择报告类型并点击"生成报告"
          </div>
        )}
      </Card>
    </div>
  );
}
