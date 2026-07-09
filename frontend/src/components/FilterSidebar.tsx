import type { JobFilters } from "../api/types"

interface Props {
  filters: JobFilters
  onChange: (filters: JobFilters) => void
}

const REMOTE_OPTIONS = ["remote", "hybrid", "onsite"] as const

export function FilterSidebar({ filters, onChange }: Props) {
  const toggleRemote = (value: string) => {
    const current = filters.remote_type ?? []
    const next = current.includes(value) ? current.filter((v) => v !== value) : [...current, value]
    onChange({ ...filters, remote_type: next.length ? next : undefined })
  }

  return (
    <aside className="w-64 shrink-0 space-y-5 rounded-lg border border-slate-200 dark:border-slate-700 p-4 bg-white dark:bg-slate-900 h-fit">
      <div>
        <h3 className="text-xs font-semibold uppercase tracking-wide text-slate-500 mb-2">Work type</h3>
        <div className="space-y-1">
          {REMOTE_OPTIONS.map((opt) => (
            <label key={opt} className="flex items-center gap-2 text-sm capitalize">
              <input
                type="checkbox"
                checked={filters.remote_type?.includes(opt) ?? false}
                onChange={() => toggleRemote(opt)}
              />
              {opt}
            </label>
          ))}
        </div>
      </div>

      <div>
        <h3 className="text-xs font-semibold uppercase tracking-wide text-slate-500 mb-2">Keyword</h3>
        <input
          type="text"
          placeholder="title or description"
          className="w-full rounded border border-slate-300 dark:border-slate-600 bg-transparent px-2 py-1 text-sm"
          defaultValue={filters.keyword ?? ""}
          onBlur={(e) => onChange({ ...filters, keyword: e.target.value || undefined })}
        />
      </div>

      <div>
        <h3 className="text-xs font-semibold uppercase tracking-wide text-slate-500 mb-2">Location</h3>
        <input
          type="text"
          placeholder="city, state, country"
          className="w-full rounded border border-slate-300 dark:border-slate-600 bg-transparent px-2 py-1 text-sm"
          defaultValue={filters.location ?? ""}
          onBlur={(e) => onChange({ ...filters, location: e.target.value || undefined })}
        />
      </div>

      <div>
        <h3 className="text-xs font-semibold uppercase tracking-wide text-slate-500 mb-2">Salary min ($)</h3>
        <input
          type="number"
          placeholder="e.g. 120000"
          className="w-full rounded border border-slate-300 dark:border-slate-600 bg-transparent px-2 py-1 text-sm"
          defaultValue={filters.salary_min ?? ""}
          onBlur={(e) => onChange({ ...filters, salary_min: e.target.value ? Number(e.target.value) : undefined })}
        />
      </div>

      <div>
        <h3 className="text-xs font-semibold uppercase tracking-wide text-slate-500 mb-2">Min match score</h3>
        <input
          type="range"
          min={0}
          max={100}
          step={5}
          value={filters.min_match_score ?? 0}
          onChange={(e) => onChange({ ...filters, min_match_score: Number(e.target.value) || undefined })}
          className="w-full"
        />
        <div className="text-xs text-slate-500">{filters.min_match_score ?? 0}+</div>
      </div>

      <div>
        <h3 className="text-xs font-semibold uppercase tracking-wide text-slate-500 mb-2">Sort by</h3>
        <select
          className="w-full rounded border border-slate-300 dark:border-slate-600 bg-transparent px-2 py-1 text-sm"
          value={filters.sort_by ?? "match_score"}
          onChange={(e) => onChange({ ...filters, sort_by: e.target.value })}
        >
          <option value="match_score">Match score</option>
          <option value="posted_date">Posted date</option>
          <option value="salary">Salary</option>
        </select>
      </div>
    </aside>
  )
}
