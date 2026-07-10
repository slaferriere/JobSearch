export type RemoteType = "remote" | "hybrid" | "onsite" | "unknown"

export interface Job {
  id: number
  source: string
  title: string
  company: string
  location_raw: string | null
  remote_type: RemoteType
  salary_min: number | null
  salary_max: number | null
  salary_currency: string
  apply_url: string
  apply_url_is_redirect: boolean
  posted_date: string | null
  is_active: boolean
  likely_duplicate_of: number | null
  llm_score: number | null
}

export interface JobDetail extends Job {
  description_html: string | null
  description_text: string | null
  llm_rationale: string | null
  matching_skills: string[]
  missing_skills: string[]
}

export interface ResumeProfile {
  id: number
  uploaded_at: string
  original_filename: string | null
  label: string | null
  is_current: boolean
  parsed: {
    name: string
    email: string | null
    phone: string | null
    linkedin_url: string | null
    target_titles: string[]
    years_experience: number
    seniority_level: string
    skills: string[]
    clearance_status: string | null
    work_history: { title: string; company: string; duration: string; highlights: string[] }[]
    education: { degree: string; institution: string; year: string | null }[]
    summary: string
  }
}

export interface IngestionRun {
  id: number
  started_at: string
  finished_at: string | null
  source: string | null
  jobs_added: number
  jobs_updated: number
  jobs_deactivated: number
  error: string | null
}

export interface JobFilters {
  remote_type?: string[]
  salary_min?: number
  salary_max?: number
  location?: string
  keyword?: string
  source?: string[]
  min_match_score?: number
  sort_by?: string
}
