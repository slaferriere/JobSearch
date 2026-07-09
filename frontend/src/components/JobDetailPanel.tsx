import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { fetchJobDetail, rescoreJob } from "../api/client"

interface Props {
  jobId: number | null
}

export function JobDetailPanel({ jobId }: Props) {
  const queryClient = useQueryClient()

  const detailQuery = useQuery({
    queryKey: ["job", jobId],
    queryFn: () => fetchJobDetail(jobId as number),
    enabled: jobId != null,
  })

  const rescoreMutation = useMutation({
    mutationFn: () => rescoreJob(jobId as number),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["job", jobId] })
      queryClient.invalidateQueries({ queryKey: ["jobs"] })
    },
  })

  if (jobId == null) {
    return (
      <div className="flex-1 rounded-lg border border-slate-200 dark:border-slate-700 p-6 text-sm text-slate-500 bg-white dark:bg-slate-900">
        Select a job to see the full description.
      </div>
    )
  }

  if (detailQuery.isLoading) {
    return <div className="flex-1 p-6 text-sm text-slate-500">Loading...</div>
  }

  const job = detailQuery.data
  if (!job) return null

  return (
    <div className="flex-1 rounded-lg border border-slate-200 dark:border-slate-700 p-6 bg-white dark:bg-slate-900 overflow-y-auto max-h-[80vh]">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h2 className="text-lg font-semibold text-slate-900 dark:text-slate-100">{job.title}</h2>
          <p className="text-sm text-slate-600 dark:text-slate-400">
            {job.company} &middot; {job.location_raw ?? "location n/a"} &middot;{" "}
            <span className="capitalize">{job.remote_type}</span>
          </p>
        </div>
        <a
          href={job.apply_url}
          target="_blank"
          rel="noreferrer"
          className="shrink-0 px-4 py-2 rounded-md bg-indigo-600 text-white text-sm font-medium hover:bg-indigo-500"
        >
          Apply →
        </a>
      </div>

      {job.apply_url_is_redirect && (
        <p className="mt-2 text-xs text-amber-700 dark:text-amber-400">
          This apply link goes through an aggregator redirect, not directly to the employer's posting.
        </p>
      )}

      {job.llm_score != null ? (
        <div className="mt-4 rounded-md border border-emerald-200 dark:border-emerald-800 bg-emerald-50 dark:bg-emerald-950 p-3">
          <p className="text-sm font-semibold text-emerald-900 dark:text-emerald-200">
            Match score: {job.llm_score}/100
          </p>
          {job.llm_rationale && <p className="text-sm text-emerald-800 dark:text-emerald-300 mt-1">{job.llm_rationale}</p>}
          <div className="mt-2 flex flex-wrap gap-3 text-xs">
            {job.matching_skills.length > 0 && (
              <span>
                <strong>Matches:</strong> {job.matching_skills.join(", ")}
              </span>
            )}
            {job.missing_skills.length > 0 && (
              <span>
                <strong>Gaps:</strong> {job.missing_skills.join(", ")}
              </span>
            )}
          </div>
        </div>
      ) : (
        <button
          onClick={() => rescoreMutation.mutate()}
          disabled={rescoreMutation.isPending}
          className="mt-4 text-sm px-3 py-1.5 rounded-md border border-slate-300 dark:border-slate-600 hover:bg-slate-50 dark:hover:bg-slate-800 disabled:opacity-50"
        >
          {rescoreMutation.isPending ? "Scoring..." : "Score this job against my resume"}
        </button>
      )}

      <div className="mt-5 text-sm text-slate-700 dark:text-slate-300 whitespace-pre-wrap">
        {job.description_text}
      </div>
    </div>
  )
}
