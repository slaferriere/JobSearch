import type { Job, JobDetail, JobFilters, ResumeProfile, IngestionRun } from "./types"

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(path, options)
  if (!res.ok) {
    const body = await res.text()
    throw new Error(`${res.status} ${res.statusText}: ${body}`)
  }
  return res.json() as Promise<T>
}

export function fetchJobs(filters: JobFilters): Promise<Job[]> {
  const params = new URLSearchParams()
  if (filters.remote_type) filters.remote_type.forEach((r) => params.append("remote_type", r))
  if (filters.salary_min != null) params.set("salary_min", String(filters.salary_min))
  if (filters.salary_max != null) params.set("salary_max", String(filters.salary_max))
  if (filters.location) params.set("location", filters.location)
  if (filters.keyword) params.set("keyword", filters.keyword)
  if (filters.source) filters.source.forEach((s) => params.append("source", s))
  if (filters.min_match_score != null) params.set("min_match_score", String(filters.min_match_score))
  if (filters.sort_by) params.set("sort_by", filters.sort_by)
  return request<Job[]>(`/api/jobs?${params.toString()}`)
}

export function fetchJobDetail(id: number): Promise<JobDetail> {
  return request<JobDetail>(`/api/jobs/${id}`)
}

export function rescoreJob(id: number): Promise<JobDetail> {
  return request<JobDetail>(`/api/jobs/${id}/match`, { method: "POST" })
}

export function fetchCurrentResume(): Promise<ResumeProfile> {
  return request<ResumeProfile>(`/api/resume`)
}

export function fetchAllResumes(): Promise<ResumeProfile[]> {
  return request<ResumeProfile[]>(`/api/resume/all`)
}

export async function uploadResume(args: { file: File; label?: string }): Promise<ResumeProfile> {
  const form = new FormData()
  form.append("file", args.file)
  if (args.label) form.append("label", args.label)
  return request<ResumeProfile>(`/api/resume`, { method: "POST", body: form })
}

export function activateResume(id: number): Promise<ResumeProfile> {
  return request<ResumeProfile>(`/api/resume/${id}/activate`, { method: "POST" })
}

export function triggerIngestion(sources?: string[]): Promise<IngestionRun[]> {
  const params = new URLSearchParams()
  sources?.forEach((s) => params.append("source", s))
  return request<IngestionRun[]>(`/api/ingest/run?${params.toString()}`, { method: "POST" })
}
