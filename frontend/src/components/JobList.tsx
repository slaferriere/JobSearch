import type { Job } from "../api/types"

interface Props {
  jobs: Job[]
  selectedId: number | null
  onSelect: (id: number) => void
  isLoading: boolean
}

function formatSalary(job: Job): string | null {
  if (job.salary_min == null && job.salary_max == null) return null
  const fmt = (n: number) => `$${Math.round(n / 1000)}k`
  if (job.salary_min != null && job.salary_max != null) return `${fmt(job.salary_min)}–${fmt(job.salary_max)}`
  return fmt(job.salary_min ?? job.salary_max ?? 0)
}

export function JobList({ jobs, selectedId, onSelect, isLoading }: Props) {
  if (isLoading) {
    return <p className="text-sm text-slate-500 p-4">Loading jobs...</p>
  }
  if (jobs.length === 0) {
    return <p className="text-sm text-slate-500 p-4">No jobs match your filters yet.</p>
  }

  return (
    <ul className="flex-1 divide-y divide-slate-200 dark:divide-slate-700 border border-slate-200 dark:border-slate-700 rounded-lg overflow-hidden bg-white dark:bg-slate-900">
      {jobs.map((job) => (
        <li
          key={job.id}
          onClick={() => onSelect(job.id)}
          className={`p-3 cursor-pointer hover:bg-slate-50 dark:hover:bg-slate-800 ${
            selectedId === job.id ? "bg-indigo-50 dark:bg-indigo-950" : ""
          }`}
        >
          <div className="flex items-start justify-between gap-2">
            <div>
              <p className="font-medium text-sm text-slate-900 dark:text-slate-100">{job.title}</p>
              <p className="text-sm text-slate-600 dark:text-slate-400">
                {job.company} &middot; {job.location_raw ?? "location n/a"} &middot;{" "}
                <span className="capitalize">{job.remote_type}</span>
                {formatSalary(job) && <> &middot; {formatSalary(job)}</>}
              </p>
              {job.likely_duplicate_of && (
                <span className="inline-block mt-1 text-xs px-1.5 py-0.5 rounded bg-amber-100 text-amber-800 dark:bg-amber-900 dark:text-amber-200">
                  possible duplicate listing
                </span>
              )}
            </div>
            {job.llm_score != null && (
              <span className="shrink-0 text-sm font-semibold rounded-full px-2 py-0.5 bg-emerald-100 text-emerald-800 dark:bg-emerald-900 dark:text-emerald-200">
                {job.llm_score}
              </span>
            )}
          </div>
        </li>
      ))}
    </ul>
  )
}
