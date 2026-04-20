import api from "./client";

export type FeedbackSource = "app_rating" | "app_feedback" | "customer_service" | "social_media";
export type Priority = "P0" | "P1" | "P2" | "P3";
export type TicketStatus = "pending" | "processing" | "resolved" | "closed";
export type SLAStatus = "normal" | "warning" | "overdue";

export interface Feedback {
  feedback_id: string;
  user_id: string;
  trip_id: string;
  vehicle_id: string;
  rating: number;
  feedback_text: string;
  city: string;
  route: string;
  trip_time: string;
  trip_duration: number;
  feedback_time: string;
  source: FeedbackSource;
  ai_category: string | null;
  ai_confidence: number | null;
  ai_status: string;
  cluster_id: string | null;
  ticket_id: number | null;
  ticket_biz_id: string | null;
  created_at: string;
  updated_at: string;
}

export interface FeedbackListResponse {
  items: Feedback[];
  total: number;
  page: number;
  page_size: number;
}

export interface FeedbackFilter {
  rating_min?: number;
  rating_max?: number;
  time_start?: string;
  time_end?: string;
  city?: string;
  route?: string;
  source?: string;
  ai_category?: string;
  ticket_status?: string;
  priority?: string;
  sort_by?: string;
  sort_order?: string;
  page?: number;
  page_size?: number;
}

export interface TicketLog {
  operator: string;
  action: string;
  detail: string | null;
  created_at: string;
}

export interface Ticket {
  ticket_id: string;
  priority: Priority;
  status: TicketStatus;
  assignee: string | null;
  sla_response_deadline: string | null;
  sla_resolve_deadline: string | null;
  sla_status: SLAStatus;
  escalated: boolean;
  processing_result: string | null;
  processing_note: string | null;
  resolved_time: string | null;
  feedback: Feedback | null;
  logs: TicketLog[];
  created_at: string;
  updated_at: string;
}

export interface TicketListResponse {
  items: Ticket[];
  total: number;
  page: number;
  page_size: number;
}

export interface TicketCreateParams {
  feedback_id: string;
  priority: Priority;
  assignee?: string;
}

export interface TicketUpdateParams {
  status?: TicketStatus;
  priority?: Priority;
  assignee?: string;
  processing_result?: string;
  processing_note?: string;
}

export interface AIAnalyzeSummary {
  major_problems: string[];
  feedback_themes: string[];
  action_suggestions: string[];
  trend_summary: string;
}

export interface AIAnalyzeResponse {
  summary: AIAnalyzeSummary;
  feedback_count: number;
}

export const feedbackApi = {
  list: (params: FeedbackFilter) =>
    api.get<FeedbackListResponse>("/feedbacks", { params }),
  listIds: (params: Omit<FeedbackFilter, "page" | "page_size" | "sort_by" | "sort_order">) =>
    api.get<{ ids: string[]; total: number }>("/feedbacks/ids", { params }),
  getById: (id: string) => api.get<Feedback>(`/feedbacks/${id}`),
  getByUser: (userId: string) => api.get<Feedback[]>(`/feedbacks/by-user/${userId}`),
  getByVehicle: (vehicleId: string) =>
    api.get<Feedback[]>(`/feedbacks/by-vehicle/${vehicleId}`),
  export: (params: FeedbackFilter & { ids?: string }) =>
    api.get<Blob>("/feedbacks/export", { params, responseType: "blob" }),
  aiAnalyze: (feedbackIds: string[]) =>
    api.post<AIAnalyzeResponse>(
      "/feedbacks/ai-analyze",
      { feedback_ids: feedbackIds },
      { timeout: 60000 },
    ),
};

export const ticketApi = {
  list: (params?: {
    status?: string;
    priority?: string;
    assignee?: string;
    sla_status?: string;
    page?: number;
    page_size?: number;
  }) => api.get<TicketListResponse>("/tickets", { params }),
  getById: (id: string) => api.get<Ticket>(`/tickets/${id}`),
  create: (data: TicketCreateParams) => api.post<Ticket>("/tickets", data),
  update: (id: string, data: TicketUpdateParams) =>
    api.patch<Ticket>(`/tickets/${id}`, data),
  export: (params?: {
    ids?: string;
    status?: string;
    priority?: string;
    assignee?: string;
    sla_status?: string;
  }) => api.get<Blob>("/tickets/export", { params, responseType: "blob" }),
};
