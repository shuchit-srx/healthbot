export interface TopicValidationResponse {
  valid: boolean;
  topic: string;
  message: string;
}

export interface Source {
  title: string;
  url: string;
  content: string;
  score?: number;
}

export interface SummaryResponse {
  topic: string;
  summary: string;
  sources: Source[];
}

export interface QuizResponse {
  question: string;
}

export interface GradeResponse {
  grade: string;
  feedback: string;
}

export interface SessionResponse {
  continue_session: boolean;
  message: string;
}