export interface User {
    id: number;
    username: string;
    email: string;
    profile_picture: string;
  }
  
  export interface Project {
    id: number;
    name: string;
    owner_id: number;
    periodicity: string;
  }
  
  export interface Task {
    id: number;
    name: string;
    description?: string;
    status: string;
    assignee_id?: number;
    project_id: number;
    sprint_id?: number;
  }