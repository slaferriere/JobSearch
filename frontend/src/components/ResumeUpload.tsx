import { useRef, useState } from "react"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { fetchCurrentResume, uploadResume } from "../api/client"

export function ResumeUpload() {
  const queryClient = useQueryClient()
  const fileInput = useRef<HTMLInputElement>(null)
  const [error, setError] = useState<string | null>(null)

  const resumeQuery = useQuery({
    queryKey: ["resume"],
    queryFn: fetchCurrentResume,
    retry: false,
  })

  const uploadMutation = useMutation({
    mutationFn: uploadResume,
    onSuccess: () => {
      setError(null)
      queryClient.invalidateQueries({ queryKey: ["resume"] })
      queryClient.invalidateQueries({ queryKey: ["jobs"] })
    },
    onError: (err: Error) => setError(err.message),
  })

  const handleFile = (file: File | undefined) => {
    if (!file) return
    uploadMutation.mutate(file)
  }

  const profile = resumeQuery.data?.parsed

  return (
    <div className="rounded-lg border border-slate-200 dark:border-slate-700 p-4 bg-white dark:bg-slate-900">
      <div className="flex items-center justify-between gap-4">
        <div>
          <h2 className="text-sm font-semibold text-slate-900 dark:text-slate-100">Resume</h2>
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
            ref={fileInput}
            type="file"
            accept=".pdf,.docx"
            className="hidden"
            onChange={(e) => handleFile(e.target.files?.[0])}
          />
          <button
            onClick={() => fileInput.current?.click()}
            disabled={uploadMutation.isPending}
            className="px-3 py-1.5 text-sm rounded-md bg-indigo-600 text-white hover:bg-indigo-500 disabled:opacity-50"
          >
            {uploadMutation.isPending ? "Uploading..." : profile ? "Replace resume" : "Upload resume"}
          </button>
        </div>
      </div>
      {error && <p className="mt-2 text-sm text-red-600">{error}</p>}
    </div>
  )
}
