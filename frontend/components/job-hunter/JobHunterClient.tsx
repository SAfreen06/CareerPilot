'use client'

import { useState } from 'react'
import {
    Search, MapPin, DollarSign, Calendar, Briefcase, Globe,
    Bookmark, BookmarkCheck, ExternalLink, Loader2, Sparkles,
    CheckCircle2, XCircle, Wifi,
} from 'lucide-react'
import { getBackendUrl } from '@/lib/backend'

interface JobCard {
    role: string
    company: string | null
    location: string | null
    salary: string | null
    deadline: string | null
    job_type: string | null
    skills: string[]
    summary: string
    apply_url: string
    relevance_score: number
    source: 'tavily' | 'remotive' | 'curated'
    fit_percent: number | null
    matched_skills: string[]
    missing_skills: string[]
    reasoning: string
}

const MOCK_JOBS: JobCard[] = [
    {
        role: 'Senior Full Stack Engineer',
        company: 'Tech Startup Inc.',
        location: 'Remote',
        salary: '$120,000 - $150,000',
        deadline: '6/15/2026',
        job_type: 'full-time',
        skills: ['React', 'Python', 'PostgreSQL', 'AWS'],
        summary: 'Looking for an experienced full-stack engineer to build scalable web applications.',
        apply_url: '#',
        relevance_score: 0.95,
        source: 'remotive',
        fit_percent: 85,
        matched_skills: ['React', 'Python', 'PostgreSQL'],
        missing_skills: ['AWS'],
        reasoning: 'Your experience with React, FastAPI, and PostgreSQL matches perfectly.',
    },
    {
        role: 'ML Engineer Intern',
        company: null,
        location: 'Dhaka, Bangladesh',
        salary: 'BDT 15,000–20,000/month',
        deadline: null,
        job_type: 'internship',
        skills: ['Python', 'TensorFlow', 'REST APIs'],
        summary: 'ML internship role focused on model development and deployment.',
        apply_url: '#',
        relevance_score: 0.87,
        source: 'tavily',
        fit_percent: 72,
        matched_skills: ['Python', 'REST APIs'],
        missing_skills: ['TensorFlow'],
        reasoning: 'Python and REST API experience matches. TensorFlow not found in CV.',
    },
    {
        role: 'Backend Engineer Intern',
        company: 'TechVenture BD',
        location: 'Gulshan, Dhaka',
        salary: null,
        deadline: null,
        job_type: 'internship',
        skills: ['Python', 'FastAPI', 'PostgreSQL'],
        summary: 'Looking for Python and FastAPI developers with REST API experience.',
        apply_url: '#',
        relevance_score: 0.75,
        source: 'curated',
        fit_percent: 91,
        matched_skills: ['Python', 'FastAPI', 'PostgreSQL'],
        missing_skills: [],
        reasoning: 'Excellent match — all required skills found in your CV.',
    },
]

const SOURCE_CONFIG = {
    remotive: { label: 'Remote', color: 'text-cyan-400 border-cyan-400/30 bg-cyan-400/10', icon: Globe },
    tavily:   { label: 'BD Local', color: 'text-amber-400 border-amber-400/30 bg-amber-400/10', icon: MapPin },
    curated:  { label: 'Featured', color: 'text-slate-400 border-slate-600 bg-slate-800', icon: Sparkles },
}

const fitColor = (pct: number | null) => {
    if (!pct) return 'text-slate-400 border-slate-700 bg-slate-800'
    if (pct >= 80) return 'text-emerald-400 border-emerald-400/30 bg-emerald-400/10'
    if (pct >= 60) return 'text-amber-400 border-amber-400/30 bg-amber-400/10'
    return 'text-red-400 border-red-400/30 bg-red-400/10'
}

function JobCardComponent({ job }: { job: JobCard }) {
    const [saved, setSaved] = useState(false)
    const src = SOURCE_CONFIG[job.source]
    const SrcIcon = src.icon

    return (
        <div className="rounded-2xl border border-slate-700/60 bg-[#0f172a] overflow-hidden hover:border-slate-600 transition-all duration-200">
            <div className="p-5 pb-4">
                <div className="flex items-start justify-between gap-3">
                    <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 flex-wrap mb-1">
                            <span className={`inline-flex items-center gap-1 text-xs px-2 py-0.5 rounded-full border font-medium ${src.color}`}>
                                <SrcIcon className="w-3 h-3" />
                                {src.label}
                            </span>
                            {job.job_type && (
                                <span className="text-xs px-2 py-0.5 rounded-full border border-slate-700 bg-slate-800 text-slate-400 capitalize">
                                    {job.job_type}
                                </span>
                            )}
                        </div>
                        <h3 className="text-white font-semibold text-lg leading-tight">{job.role}</h3>
                        <p className="text-slate-400 text-sm mt-0.5">
                            {job.company ?? 'Multiple companies'}
                        </p>
                    </div>
                    {job.fit_percent !== null && (
                        <div className={`flex-shrink-0 text-center px-3 py-2 rounded-xl border font-semibold ${fitColor(job.fit_percent)}`}>
                            <div className="text-lg leading-none">{job.fit_percent}%</div>
                            <div className="text-xs mt-0.5 opacity-70">Match</div>
                        </div>
                    )}
                </div>

                <div className="flex flex-wrap gap-3 mt-3 text-xs text-slate-400">
                    {job.location && <span className="flex items-center gap-1"><MapPin className="w-3 h-3" />{job.location}</span>}
                    {job.salary && <span className="flex items-center gap-1"><DollarSign className="w-3 h-3" />{job.salary}</span>}
                    {job.deadline && <span className="flex items-center gap-1"><Calendar className="w-3 h-3" />Apply by {job.deadline}</span>}
                </div>

                <p className="text-slate-300 text-sm mt-3 leading-relaxed">{job.summary}</p>

                {job.reasoning && (
                    <div className="mt-3 rounded-lg border border-slate-700/60 bg-slate-800/50 px-4 py-3 text-sm text-slate-300">
                        <span className="font-medium text-white">Why you match: </span>
                        {job.reasoning}
                    </div>
                )}

                <div className="flex flex-wrap gap-2 mt-3">
                    {job.matched_skills.map(s => (
                        <span key={s} className="inline-flex items-center gap-1 text-xs px-2 py-1 rounded-md border border-emerald-400/20 bg-emerald-400/10 text-emerald-300">
                            <CheckCircle2 className="w-3 h-3" />{s}
                        </span>
                    ))}
                    {job.missing_skills.map(s => (
                        <span key={s} className="inline-flex items-center gap-1 text-xs px-2 py-1 rounded-md border border-red-400/20 bg-red-400/10 text-red-300">
                            <XCircle className="w-3 h-3" />{s}
                        </span>
                    ))}
                    {job.skills
                        .filter(s => !job.matched_skills.includes(s) && !job.missing_skills.includes(s))
                        .map(s => (
                            <span key={s} className="text-xs px-2 py-1 rounded-md border border-slate-700 bg-slate-800 text-slate-400">{s}</span>
                        ))}
                </div>
            </div>

            <div className="border-t border-slate-700/60 px-5 py-3 flex items-center gap-3 bg-[#0a1020]">
                <a
                    href={job.apply_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex-1 flex items-center justify-center gap-2 py-2 rounded-lg bg-slate-100 hover:bg-white text-slate-900 text-sm font-medium transition-colors"
                >
                    Apply now <ExternalLink className="w-3.5 h-3.5" />
                </a>
                <button
                    onClick={() => setSaved(v => !v)}
                    className={`flex items-center gap-1.5 px-3 py-2 rounded-lg border text-sm transition-colors ${
                        saved
                            ? 'border-cyan-400/40 bg-cyan-400/10 text-cyan-300'
                            : 'border-slate-700 bg-transparent text-slate-400 hover:text-white hover:border-slate-500'
                    }`}
                >
                    {saved ? <BookmarkCheck className="w-4 h-4" /> : <Bookmark className="w-4 h-4" />}
                    {saved ? 'Saved' : 'Save'}
                </button>
            </div>
        </div>
    )
}

export default function JobHunterClient() {
    const [query, setQuery] = useState('')
    const [loading, setLoading] = useState(false)
    const [jobs, setJobs] = useState<JobCard[]>(MOCK_JOBS)
    const [searched, setSearched] = useState(false)
    const [error, setError] = useState<string | null>(null)
    const [activeFilter, setActiveFilter] = useState<'all' | 'remote' | 'local' | 'internship'>('all')

    const handleSearch = async () => {
        if (!query.trim()) return
        setLoading(true)
        setSearched(true)
        setError(null)

        try {
            // ── uses getBackendUrl() — same as CV upload ──
            const backendUrl = getBackendUrl()
            const res = await fetch(`${backendUrl}/api/jobs/search`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query, user_id: 'test_user' }),
            })

            if (!res.ok) {
                const data = await res.json().catch(() => null)
                throw new Error(data?.detail || `Server error ${res.status}`)
            }

            const data = await res.json()
            const results = data.results ?? []

            if (results.length === 0) {
                setError('No jobs found. Try a different search.')
                setJobs([])
            } else {
                setJobs(results)
            }
        } catch (err) {
            // backend down or network error — fall back to mock
            console.error('[job-hunter] search failed:', err)
            setError('Could not reach backend — showing sample results.')
            setJobs(MOCK_JOBS)
        } finally {
            setLoading(false)
        }
    }

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter') handleSearch()
    }

    const suggestions = [
        'ML internships in Dhaka',
        'Remote React developer jobs',
        'Senior Python backend roles',
        'Data science jobs today',
    ]

    const filtered = jobs.filter(j => {
        if (activeFilter === 'remote') return j.source === 'remotive'
        if (activeFilter === 'local') return j.source === 'tavily' || j.source === 'curated'
        if (activeFilter === 'internship') return j.job_type === 'internship'
        return true
    })

    return (
        <div className="max-w-4xl mx-auto space-y-8">
            {/* Header */}
            <div className="space-y-1">
                <h1 className="text-3xl sm:text-4xl font-semibold text-white">Job opportunities</h1>
                <p className="text-slate-400 text-sm">Personalized opportunities based on your resume.</p>
            </div>

            {/* Search bar */}
            <div className="space-y-3">
                <div className="flex gap-3">
                    <div className="flex-1 flex items-center gap-3 rounded-xl border border-slate-700 bg-[#0f172a] px-4 py-3 focus-within:border-slate-500 transition-colors">
                        <Search className="w-4 h-4 text-slate-500 flex-shrink-0" />
                        <input
                            value={query}
                            onChange={e => setQuery(e.target.value)}
                            onKeyDown={handleKeyDown}
                            placeholder="Search by job title, company, or skills"
                            className="flex-1 bg-transparent text-white placeholder-slate-500 text-sm outline-none"
                        />
                        {loading && <Loader2 className="w-4 h-4 text-slate-400 animate-spin flex-shrink-0" />}
                    </div>
                    <button
                        onClick={handleSearch}
                        disabled={loading || !query.trim()}
                        className="px-5 py-3 rounded-xl bg-slate-100 hover:bg-white disabled:opacity-40 disabled:cursor-not-allowed text-slate-900 text-sm font-medium transition-colors flex-shrink-0"
                    >
                        Search
                    </button>
                </div>

                {/* Suggestion chips */}
                {!searched && (
                    <div className="flex flex-wrap gap-2">
                        <span className="text-xs text-slate-500 self-center">Try:</span>
                        {suggestions.map(s => (
                            <button
                                key={s}
                                onClick={() => setQuery(s)}
                                className="text-xs px-3 py-1.5 rounded-full border border-slate-700 bg-[#0f172a] text-slate-400 hover:text-white hover:border-slate-500 transition-colors"
                            >
                                {s}
                            </button>
                        ))}
                    </div>
                )}
            </div>

            {/* Error banner */}
            {error && (
                <div className="rounded-xl border border-amber-400/20 bg-amber-400/5 px-4 py-3 text-sm text-amber-300">
                    {error}
                </div>
            )}

            {/* Filter tabs */}
            <div className="flex items-center gap-2 flex-wrap">
                {(['all', 'remote', 'local', 'internship'] as const).map(f => (
                    <button
                        key={f}
                        onClick={() => setActiveFilter(f)}
                        className={`text-xs px-3 py-1.5 rounded-full border transition-colors capitalize ${
                            activeFilter === f
                                ? 'border-slate-400 bg-slate-700 text-white'
                                : 'border-slate-700 bg-transparent text-slate-400 hover:text-white hover:border-slate-600'
                        }`}
                    >
                        {f === 'all' ? `All (${jobs.length})` : f}
                    </button>
                ))}
                <div className="ml-auto flex items-center gap-2 text-xs text-slate-500">
                    <Wifi className="w-3 h-3" />
                    <span className="text-emerald-400">Remotive</span>
                    <span>+</span>
                    <span className="text-amber-400">Tavily</span>
                </div>
            </div>

            {/* Results */}
            {loading ? (
                <div className="flex flex-col items-center justify-center py-20 gap-4">
                    <Loader2 className="w-8 h-8 text-slate-400 animate-spin" />
                    <p className="text-slate-400 text-sm">Searching jobs and computing fit scores...</p>
                </div>
            ) : filtered.length === 0 ? (
                <div className="flex flex-col items-center justify-center py-20 gap-3">
                    <Briefcase className="w-10 h-10 text-slate-600" />
                    <p className="text-slate-400">No jobs found. Try a different search.</p>
                </div>
            ) : (
                <div className="space-y-4">
                    <p className="text-xs text-slate-500">
                        {filtered.length} result{filtered.length !== 1 ? 's' : ''}
                        {searched ? ` for "${query}"` : ' — sample results'}
                        {' '}· sorted by fit score
                    </p>
                    {[...filtered]
                        .sort((a, b) => (b.fit_percent ?? 0) - (a.fit_percent ?? 0))
                        .map((job, i) => (
                            <JobCardComponent key={i} job={job} />
                        ))}
                </div>
            )}
        </div>
    )
}