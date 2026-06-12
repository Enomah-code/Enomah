export interface Agent {
  id: string;
  name: string;
  role: string;
  title: string;
  color: string;
  gradient: [string, string];
  emoji: string;
  skills: string[];
  status: 'active' | 'thinking' | 'idle' | 'offline';
  tasksCompleted: number;
  successRate: number;
  description: string;
  personality: string[];
  tools: string[];
  limits: string;
}

export interface Message {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
  agentsUsed?: string[];
  missionId?: string;
  isStreaming?: boolean;
}

export interface Mission {
  id: string;
  title: string;
  status: 'pending' | 'active' | 'completed' | 'failed';
  agents: string[];
  progress: number;
  startedAt: Date;
  completedAt?: Date;
  result?: string;
}

export interface Project {
  id: string;
  name: string;
  description: string;
  status: 'planning' | 'active' | 'review' | 'completed';
  agents: string[];
  progress: number;
  createdAt: Date;
  updatedAt: Date;
  missions: Mission[];
  tags: string[];
  priority: 'low' | 'medium' | 'high' | 'critical';
}

export interface MemoryEntry {
  id: string;
  type: 'user' | 'project' | 'business' | 'evolution';
  content: string;
  source: string;
  relevance: number;
  createdAt: Date;
  tags: string[];
}

export interface NetworkStats {
  totalAgents: number;
  activeAgents: number;
  totalMissions: number;
  successRate: number;
  memoryEntries: number;
  uptime: string;
}

export interface ChatSession {
  id: string;
  messages: Message[];
  activeMissions: Mission[];
  activeAgents: string[];
}
