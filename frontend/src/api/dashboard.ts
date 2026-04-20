import api from "./client";

export interface DashboardOverview {
  total_feedbacks: number;
  total_today: number;
  total_this_week: number;
  total_this_month: number;
  avg_rating: number;
  positive_rate: number;
  negative_rate: number;
  open_tickets: number;
  sla_compliance_rate: number;
}

export interface TrendPoint {
  date: string;
  value: number;
}

export interface TrendData {
  negative_count: TrendPoint[];
  positive_rate: TrendPoint[];
  avg_rating: TrendPoint[];
}

export interface DistributionItem {
  label: string;
  count: number;
  percentage: number;
}

export interface DistributionData {
  by_rating: DistributionItem[];
  by_route: DistributionItem[];
  by_city: DistributionItem[];
  by_category: DistributionItem[];
  by_time_period: DistributionItem[];
}

export interface TicketMetrics {
  by_priority: DistributionItem[];
  avg_resolve_time_hours: Record<string, number>;
  sla_compliance_by_priority: Record<string, number>;
  open_tickets_aging: DistributionItem[];
}

export interface RouteTrendSeries {
  route: string;
  data: number[];
}

export interface RouteTrendData {
  dates: string[];
  series: RouteTrendSeries[];
}

export interface DashboardReportResponse {
  report: string;
  period: string;
  generated_at: string;
}

export const dashboardApi = {
  overview: () => api.get<DashboardOverview>("/dashboard/overview"),
  trends: (days?: number, granularity?: string) =>
    api.get<TrendData>("/dashboard/trends", { params: { days, granularity } }),
  distribution: () => api.get<DistributionData>("/dashboard/distribution"),
  ticketMetrics: () => api.get<TicketMetrics>("/dashboard/ticket-metrics"),
  routeTrends: (days?: number, topN?: number) =>
    api.get<RouteTrendData>("/dashboard/route-trends", { params: { days, top_n: topN } }),
  aiReport: (period: string) =>
    api.post<DashboardReportResponse>(
      "/dashboard/ai-report",
      { period },
      { timeout: 120000 },
    ),
};
