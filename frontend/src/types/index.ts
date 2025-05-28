export interface User {
  id: string;
  username: string;
  email: string;
  name: string;
  role: string;
}

export interface AgentResponse {
  query: string;
  response: string;
}

export interface DbResponse {
  query: string;
  sqlQuery: string;
  rawResponse: any;
  naturalLanguageResponse: string;
}

export interface DocResponse {
  query: string;
  response: string;
}

export interface ApiError {
  status: string;
  message: string;
  data?: any;
}