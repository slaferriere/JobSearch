import { useRef, useState } from "react"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { activateResume, fetchAllResumes, fetchCurrentResume, uploadResume } from "../api/client"

export function ResumeUpload() {
  const queryClient = useQueryClient()
  const fileInput = useRef<HTMLInputElement>(null)
  const [error, setError] = useState<string | null>(null)
  const [pendingLabel, setPendingLabel] = useState("")

  const resumeQuery = useQuery({
    queryKey: ["resume"],
    queryFn: fetchCurrentResume,
    retry: false,
  })

  const allResumesQuery = useQuery({
    queryKey: ["resumes"],
    queryFn: fetchAllResumes,
  })

  const invalidateAfterSwitch = () => {
    setError(null)
    queryClient.invalidateQueries({ queryKey: ["resume"] })
    queryClient.invalidateQueries({ queryKey: ["resumes"] })
    queryClient.invalidateQueries({ queryKey: ["jobs"] })
  }

  const uploadMutation = useMutation({
    mutationFn: uploadResume,
    onSuccess: invalidateAfterSwitch,
    onError: (err: Error) => setError(err.message),
  })

  const activateMutation = useMutation({
    mutationFn: activateResume,
    onSuccess: invalidateAfterSwitch,
    onError: (err: Error) => setError(err.message),
  })

  const handleFile = (file: File | undefined) => {
    if (!file) return
    uploadMutation.mutate({ file, label: pendingLabel.trim() || undefined })
    setPendingLabel("")
  }

  const profile = resumeQuery.data?.parsed
  const resumes = allResumesQuery.data ?? []
  const isBusy = uploadMutation.isPending || activateMutation.isPending

  return (
    <div className="rounded-lg border border-slate-200 dark:border-slate-700 p-4 bg-white dark:bg-slate-900 space-y-3">
      <div className="flex items-center justify-between gap-4">
        <div>
          <h2 className="text-sm font-semibold text-slate-900 dark:text-slate-100">
            Resume{resumeQuery.data?.label ? ` — ${resumeQuery.data.label}` : ""}
          </h2>
          {profile ? (
            <p className="text-sm text-slate-600 dark:text-slate-400">
              {profile.name} &middot; {profile.seniority_level} &middot; {profile.years_experience} yrs
              &middot; targeting {profile.target_titles.slice(0, 2).join(", ")}
            </p>
          ) : (
            <p className="text-sm text-slate-500">No resume uploaded yet.</p>
          )}
        </div>
        <div className="flex items-center gap-2">
          <input
            value={pendingLabel}
            onChange={(e) => setPendingLabel(e.target.value)}
            placeholder="Label (e.g. Architect)"
            className="w-40 px-2 py-1.5 text-sm rounded-md border border-slate-300 dark:border-slate-600 bg-transparent"
          />
          <input
            ref={fileInput}
            type="file"
            accept=".pdf,.docx"
            className="hidden"
            onChange={(e) => handleFile(e.target.files?.[0])}
          />
          <button
            onClick={() => fileInput.current?.click()}
            disabled={isBusy}
            className="px-3 py-1.5 text-sm rounded-md bg-indigo-600 text-white hover:bg-indigo-500 disabled:opacity-50"
          >
            {uploadMutation.isPending ? "Uploading..." : "Upload new resume"}
          </button>
        </div>
      </div>

      {resumes.length > 1 && (
        <div className="flex items-center gap-2 pt-2 border-t border-slate-100 dark:border-slate-800">
          <span className="text-xs font-medium text-slate-500 dark:text-slate-400">Active resume:</span>
          <select
            value={resumeQuery.data?.id ?? ""}
            disabled={isBusy}
            onChange={(e) => activateMutation.mutate(Number(e.target.value))}
            className="text-sm px-2 py-1 rounded-md border border-slate-300 dark:border-slate-600 bg-transparent"
          >
            {resumes.map((r) => (
              <option key={r.id} value={r.id}>
                {r.label || r.original_filename || `Resume #${r.id}`}
              </option>
            ))}
          </select>
          {activateMutation.isPending && (
            <span className="text-xs text-slate-500">Switching &amp; scoring new jobs&hellip;</span>
          )}
        </div>
      )}

      {error && <p className="mt-2 text-sm text-red-600">{error}</p>}
    </div>
  )
}
