import { useState } from "react"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { fetchJobs, triggerIngestion } from "../api/client"
import type { JobFilters } from "../api/types"
import { ResumeUpload } from "../components/ResumeUpload"
import { FilterSidebar } from "../components/FilterSidebar"
import { JobList } from "../components/JobList"
import { JobDetailPanel } from "../components/JobDetailPanel"

export function HomePage() {
  const [filters, setFilters] = useState<JobFilters>({ sort_by: "match_score" })
  const [selectedId, setSelectedId] = useState<number | null>(null)
  const queryClient = useQueryClient()

  const jobsQuery = useQuery({
    queryKey: ["jobs", filters],
    queryFn: () => fetchJobs(filters),
  })

  const ingestMutation = useMutation({
    mutationFn: () => triggerIngestion(),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["jobs"] }),
  })

  return (
    <div className="max-w-6xl mx-auto p-6 space-y-4">
      <header className="flex items-center justify-between">
        <h1 className="text-xl font-semibold text-slate-900 dark:text-slate-100">Job Search</h1>
        <button
          onClick={() => ingestMutation.mutate()}
          disabled={ingestMutation.isPending}
          className="text-sm px-3 py-1.5 rounded-md border border-slate-300 dark:border-slate-600 hover:bg-slate-50 dark:hover:bg-slate-800 disabled:opacity-50"
        >
          {ingestMutation.isPending ? "Refreshing..." : "Refresh listings"}
        </button>
      </header>

      <ResumeUpload />

      <div className="flex gap-4">
        <FilterSidebar filters={filters} onChange={setFilters} />
        <div className="flex-1 flex gap-4">
          <div className="w-96 shrink-0">
            <JobList
              jobs={jobsQuery.data ?? []}
              selectedId={selectedId}
              onSelect={setSelectedId}
              isLoading={jobsQuery.isLoading}
            />
          </div>
          <JobDetailPanel jobId={selectedId} />
        </div>
      </div>
    </div>
  )
}
