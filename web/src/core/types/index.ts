export interface LoginRequest {
  email: string;
  pin: string;
}

export interface LoginResponse {
  access_token: string;
  refresh_token: string;
}

export interface RegisterRequest {
  first_names: string;
  last_names: string;
  email: string;
  phone_number: { country_code: string; number: string };
  pin: string;
}

export interface VerifyRequest {
  email: string;
  code: string;
}

export interface Timestamp {
  value: number;
}

export interface AccountData {
  id: string;
  user_id: string;
  balance: string;
  currency: string;
  created_at: Timestamp;
  updated_at: Timestamp;
}

export interface MovementData {
  id: string;
  account_id: string;
  user_id: string;
  amount: string;
  currency: string;
  opening_balance: string;
  closing_balance: string;
  category: string;
  description: string;
  movement_type: "INCOME" | "EXPENSE";
  created_at: Timestamp;
}

export interface MovementPageData {
  items: MovementData[];
  next_cursor: string | null;
}

export interface CategoryStatData {
  category: string;
  total: string;
  movement_type: string;
  count: number;
}

export interface MonthlyStatData {
  year: number;
  month: number;
  income: string;
  expense: string;
  count: number;
}

export interface DailyBalanceData {
  date: string;
  income: string;
  expense: string;
  count: number;
}

export interface WeeklyStatData {
  total_income: string;
  total_expense: string;
  movement_count: number;
  by_category: CategoryStatData[];
  daily_balance: DailyBalanceData[];
}

export interface SummaryData {
  current_balance: string;
  currency: string;
  total_income: string;
  total_expense: string;
  movement_count: number;
}

export interface ApiResponse<T> {
  success: boolean;
  body: T;
  errors: { title: string; code: string; detail: string }[];
}
