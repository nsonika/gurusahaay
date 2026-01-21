const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

let authToken: string | null = null;

// Check if we're in browser environment
const isBrowser = typeof window !== 'undefined';

// Initialize token from localStorage if in browser
if (isBrowser) {
  authToken = localStorage.getItem('auth_token');
}

export function setAuthToken(token: string | null) {
  authToken = token;
  if (isBrowser) {
    if (token) {
      localStorage.setItem('auth_token', token);
    } else {
      localStorage.removeItem('auth_token');
    }
  }
}

export function getAuthToken(): string | null {
  if (isBrowser && !authToken) {
    authToken = localStorage.getItem('auth_token');
  }
  return authToken;
}

async function apiFetch<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const token = getAuthToken();
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    ...options.headers,
  };
  
  if (token) {
    (headers as Record<string, string>)['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Request failed' }));
    throw new Error(error.detail || 'Request failed');
  }

  return response.json();
}

// Auth APIs
export async function login(phone: string, password: string) {
  const response = await fetch(`${API_URL}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ phone, password }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Login failed' }));
    throw new Error(error.detail || 'Login failed');
  }

  return response.json();
}
export async function register(userData: {
  name: string;
  phone: string;
  password: string;
  language_preference?: string;
  school_name?: string;
  district?: string;
  state?: string;
}) {
  return apiFetch<{ access_token: string; teacher: Teacher }>('/auth/register', {
    method: 'POST',
    body: JSON.stringify(userData),
  });
}

export async function getCurrentUser() {
  return apiFetch<Teacher>('/auth/me');
}

export async function updateLanguagePreference(language: string) {
  return apiFetch<Teacher>(`/auth/me/language?language=${language}`, {
    method: 'PATCH',
  });
}

// Concepts APIs
export async function getConcepts(language?: string) {
  const params = language ? `?language=${language}` : '';
  return apiFetch<Concept[]>(`/concepts${params}`);
}

export async function getConcept(conceptId: string) {
  return apiFetch<Concept>(`/concepts/${conceptId}`);
}

// Help Request APIs
export async function createHelpRequest(data: {
  query_text?: string;
  audio_base64?: string;
  request_type?: string;
  category?: string;
  subject?: string;
  grade?: string;
}) {
  return apiFetch<HelpRequestResponse>('/help/request', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function getHelpRequests() {
  return apiFetch<HelpRequestResponse[]>('/help/recent');
}

export async function getHelpRequestById(id: string) {
  return apiFetch<HelpRequestResponse>(`/help/request/${id}`);
}

export async function getHelpRequest(id: string) {
  return apiFetch<HelpRequestResponse>(`/help/request/${id}`);
}

export async function addHelpResponse(helpRequestId: string, data: {
  content_id?: string;
  response_text?: string;
}) {
  return apiFetch<HelpResponseItem>(`/help/request/${helpRequestId}/respond`, {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

// Suggestions APIs
export async function getSuggestions(conceptId: string) {
  return apiFetch<SuggestionResponse>(`/suggestions?concept_id=${conceptId}`);
}

// Content APIs
export async function uploadContent(data: {
  concept_id: string;
  title: string;
  content_url?: string;
  description?: string;
  content_type?: string;
  language?: string;
  help_request_id?: string;
  subject?: string;
  grade?: string;
}) {
  return apiFetch<Content>('/content/upload', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function uploadContentWithFile(formData: FormData) {
  const token = getAuthToken();
  const headers: HeadersInit = {};
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  
  const response = await fetch(`${API_URL}/content/upload-file`, {
    method: 'POST',
    headers,
    body: formData,
  });
  
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Upload failed' }));
    throw new Error(error.detail || 'Upload failed');
  }
  
  return response.json();
}

export async function uploadFileToCloudinary(data: {
  file: File;
  title: string;
  concept_id: string;
  content_type: string;
  description?: string;
  language?: string;
  help_request_id?: string;
}) {
  const token = getAuthToken();
  const headers: HeadersInit = {};
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  
  const formData = new FormData();
  formData.append('file', data.file);
  formData.append('title', data.title);
  formData.append('concept_id', data.concept_id);
  formData.append('content_type', data.content_type);
  if (data.description) formData.append('description', data.description);
  if (data.language) formData.append('language', data.language);
  if (data.help_request_id) formData.append('help_request_id', data.help_request_id);
  
  const response = await fetch(`${API_URL}/content/upload-file`, {
    method: 'POST',
    headers,
    body: formData,
  });
  
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Upload failed' }));
    throw new Error(error.detail || 'Upload failed');
  }
  
  return response.json();
}

export async function getContentById(contentId: string) {
  return apiFetch<Content>(`/content/${contentId}`);
}

export async function addFeedback(contentId: string, data: {
  worked: boolean;
  rating: number;
  comment?: string;
}) {
  return apiFetch(`/content/${contentId}/feedback`, {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function checkCloudinaryStatus() {
  return apiFetch<{ configured: boolean; message: string }>('/content/cloudinary-status');
}

// Points APIs
export async function getMyPoints() {
  return apiFetch<PointsResponse>('/points');
}

export async function getPoints() {
  return apiFetch<PointsResponse>('/points');
}

export async function getLeaderboard(limit?: number) {
  const params = limit ? `?limit=${limit}` : '';
  return apiFetch<LeaderboardEntry[]>(`/points/leaderboard${params}`);
}

// Notifications APIs
export async function getNotifications(limit?: number) {
  const params = limit ? `?limit=${limit}` : '';
  return apiFetch<Notification[]>(`/notifications${params}`);
}

export async function getUnreadNotificationCount() {
  const notifications = await apiFetch<Notification[]>('/notifications');
  return notifications.filter(n => !n.is_read).length;
}

export async function markNotificationRead(notificationId: string) {
  return apiFetch(`/notifications/${notificationId}/read`, {
    method: 'POST',
  });
}

export async function markNotificationAsRead(notificationId: string) {
  return apiFetch(`/notifications/${notificationId}/read`, {
    method: 'POST',
  });
}

export async function markAllNotificationsRead() {
  return apiFetch('/notifications/read-all', {
    method: 'POST',
  });
}

export async function markAllNotificationsAsRead() {
  return apiFetch('/notifications/read-all', {
    method: 'POST',
  });
}

// AI APIs
export async function getAIStatus() {
  return apiFetch<{ available: boolean; message: string }>('/ai/status');
}

export async function suggestTopic(title: string, description?: string) {
  return apiFetch<TopicSuggestion>('/ai/suggest-topic', {
    method: 'POST',
    body: JSON.stringify({ title, description: description || '' }),
  });
}

export async function createTopicWithTranslations(
  topicId: string,
  topicName: string,
  topicNameHi?: string,
  topicNameKn?: string,
  synonymsEn?: string[],
  synonymsHi?: string[],
  synonymsKn?: string[],
  subject?: string,
  grade?: string
) {
  return apiFetch<{
    topic_id: string;
    topic_name: string;
    topic_name_hi?: string;
    topic_name_kn?: string;
    synonyms_added: number;
  }>('/ai/create-topic', {
    method: 'POST',
    body: JSON.stringify({ 
      topic_id: topicId, 
      topic_name: topicName,
      topic_name_hi: topicNameHi,
      topic_name_kn: topicNameKn,
      synonyms_en: synonymsEn || [],
      synonyms_hi: synonymsHi || [],
      synonyms_kn: synonymsKn || [],
      subject, 
      grade 
    })
  });
}

// Content interaction APIs
export async function recordContentView(contentId: string) {
  return apiFetch<{ message: string }>(`/content/${contentId}/view`, {
    method: 'POST',
  });
}

export async function toggleContentLike(contentId: string) {
  return apiFetch<{ liked: boolean; likes_count: number }>(`/content/${contentId}/like`, {
    method: 'POST',
  });
}

// Community Feed API
export async function getCommunityFeed(tab?: string, limit?: number, offset?: number) {
  const params = new URLSearchParams();
  if (tab) params.append('tab', tab);
  if (limit) params.append('limit', limit.toString());
  if (offset) params.append('offset', offset.toString());
  const queryString = params.toString();
  return apiFetch<Content[]>(`/community/feed${queryString ? `?${queryString}` : ''}`);
}

// Recent help requests
export async function getRecentHelpRequests(limit?: number) {
  const params = limit ? `?limit=${limit}` : '';
  return apiFetch<HelpRequestResponse[]>(`/help/recent${params}`);
}

// Types
export interface Teacher {
  id: string;
  name: string;
  phone: string;
  language_preference: string;
  school_name?: string;
  district?: string;
  state?: string;
  total_points: number;
  created_at: string;
}

export interface Concept {
  concept_id: string;
  description_en?: string;
  description_hi?: string;
  description_kn?: string;
  subject?: string;
  grade?: string;
  synonyms: { term: string; language: string }[];
}

export interface HelpRequestResponse {
  id: string;
  teacher_id: string;
  teacher_name?: string;
  original_query_text: string;
  detected_language?: string;
  help_request_id?: string;
  normalized_text?: string;
  concept_id?: string;
  subject?: string;
  grade?: string;
  request_type?: string;
  created_at: string;
  responses?: HelpResponseItem[];
}

export interface HelpResponseItem {
  id: string;
  responder_id?: string;
  teacher_id?: string;
  responder_name?: string;
  teacher_name?: string;
  content_id?: string;
  response_text?: string;
  created_at: string;
}

export interface Content {
  id: string;
  concept_id: string;
  title: string;
  content_url?: string;
  description?: string;
  content_type?: string;
  language: string;
  subject?: string;
  grade?: string;
  source_type: string;
  is_verified: boolean;
  created_at: string;
  feedback_score?: number;
  uploader_name?: string;
  likes_count?: number;
  views_count?: number;
  user_liked?: boolean;
}

export interface SuggestionResponse {
  concept_id: string;
  suggestions: Content[];
  source: string;
  message?: string;
}

export interface PointsResponse {
  total_points: number;
  history?: {
    id: string;
    points: number;
    reason: string;
    created_at: string;
  }[];
}

export interface LeaderboardEntry {
  rank: number;
  teacher_id: string;
  name: string;
  total_points: number;
  school_name?: string;
}

export interface Notification {
  id: string;
  type: string;
  title: string;
  message: string;
  is_read: boolean;
  reference_id?: string;
  reference_type?: string;
  created_at: string;
  data?: Record<string, unknown>;
}

export interface TopicSuggestion {
  matched_topic_id?: string | null;
  matched_topic_name?: string | null;
  confidence: number;
  suggested_new_topic?: string | null;
  suggested_new_topic_id?: string | null;
  suggested_new_topic_hi?: string | null;
  suggested_new_topic_kn?: string | null;
  synonyms_en?: string[];
  synonyms_hi?: string[];
  synonyms_kn?: string[];
  error?: string;
}

// Type aliases
export type HelpRequestDetail = HelpRequestResponse;
export type NotificationItem = Notification;
