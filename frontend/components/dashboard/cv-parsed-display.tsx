'use client'

import { useState, useEffect } from 'react'
import {
    Briefcase,
    BookOpen,
    Code,
    Zap,
    Upload,
    AlertCircle,
    Loader2,
    Check,
} from 'lucide-react'

interface CVParsedItem {
    section: string
    content: string
}

interface DashboardProps {
    fileId: string
    fileName: string
    chunkCount: number
}

export default function DashboardContent({
    fileId,
    fileName,
    chunkCount,
}: DashboardProps) {
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState<string | null>(null)
    const [parsedData, setParsedData] = useState<{
        experience: CVParsedItem[]
        education: CVParsedItem[]
        skills: CVParsedItem[]
        projects: CVParsedItem[]
    }>({
        experience: [],
        education: [],
        skills: [],
        projects: [],
    })

    useEffect(() => {
        // Simulate parsing CV data
        // In a real app, this would fetch from your backend or Chroma vector DB
        const mockData = {
            experience: [
                {
                    section: 'Software Engineer',
                    content: 'Built and maintained scalable backend services using Python and FastAPI',
                },
                {
                    section: 'Junior Developer',
                    content: 'Developed frontend components with React and TypeScript',
                },
            ],
            education: [
                {
                    section: 'Bachelor of Computer Science',
                    content: 'University of Technology - Graduated 2022',
                },
            ],
            skills: [
                { section: 'Languages', content: 'Python, JavaScript, TypeScript' },
                {
                    section: 'Frameworks',
                    content: 'FastAPI, React, Next.js, Tailwind CSS',
                },
                {
                    section: 'Tools & Databases',
                    content: 'PostgreSQL, MongoDB, Docker, AWS',
                },
            ],
            projects: [
                {
                    section: 'CareerPilot',
                    content: 'AI-powered career guidance platform with job recommendations',
                },
                {
                    section: 'Task Management App',
                    content: 'Full-stack application with real-time updates',
                },
            ],
        }

        // Simulate delay
        setTimeout(() => {
            setParsedData(mockData)
            setLoading(false)
        }, 800)
    }, [fileId])

    const sectionConfig = [
        {
            key: 'experience',
            title: 'Experience',
            icon: Briefcase,
        },
        {
            key: 'education',
            title: 'Education',
            icon: BookOpen,
        },
        {
            key: 'skills',
            title: 'Skills',
            icon: Code,
        },
        {
            key: 'projects',
            title: 'Projects',
            icon: Zap,
        },
    ]

    if (loading) {
        return (
            <div className="flex items-center justify-center py-20">
                <div className="text-center space-y-4">
                    <Loader2 className="w-10 h-10 text-gray-500 animate-spin mx-auto" />
                    <p className="text-gray-400">Loading your resume...</p>
                </div>
            </div>
        )
    }

    return (
        <div className="max-w-6xl mx-auto space-y-10">
            <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
                <div className="space-y-2">
                    <h1 className="text-3xl sm:text-4xl font-semibold text-white">
                        Your profile
                    </h1>
                    <p className="text-gray-400 text-sm">
                        Resume: <span className="text-gray-200">{fileName}</span>
                    </p>
                </div>
                <button className="inline-flex items-center gap-2 px-4 py-2 rounded-lg border border-gray-700 bg-[#1e1b18] text-gray-200 text-sm">
                    <Upload className="w-4 h-4" />
                    Upload new resume
                </button>
            </div>

            {error && (
                <div className="rounded-xl bg-red-500/10 border border-red-500/40 p-4 flex gap-3">
                    <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
                    <div>
                        <p className="text-red-200 font-medium">Error loading resume</p>
                        <p className="text-red-300 text-sm mt-1">{error}</p>
                    </div>
                </div>
            )}

            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div className="rounded-xl border border-gray-800 bg-[#151312] p-5">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-gray-400 text-sm">Chunks extracted</p>
                            <p className="text-2xl font-semibold text-white mt-2">
                                {chunkCount}
                            </p>
                        </div>
                        <Zap className="w-6 h-6 text-gray-600" />
                    </div>
                </div>
                <div className="rounded-xl border border-gray-800 bg-[#151312] p-5">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-gray-400 text-sm">Sections</p>
                            <p className="text-2xl font-semibold text-white mt-2">4</p>
                        </div>
                        <Code className="w-6 h-6 text-gray-600" />
                    </div>
                </div>
                <div className="rounded-xl border border-gray-800 bg-[#151312] p-5">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-gray-400 text-sm">Indexed</p>
                            <p className="text-2xl font-semibold text-white mt-2">Yes</p>
                        </div>
                        <Check className="w-6 h-6 text-gray-600" />
                    </div>
                </div>
                <div className="rounded-xl border border-gray-800 bg-[#151312] p-5">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-gray-400 text-sm">Ready</p>
                            <p className="text-2xl font-semibold text-white mt-2">Yes</p>
                        </div>
                        <BookOpen className="w-6 h-6 text-gray-600" />
                    </div>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {sectionConfig.map((section) => {
                    const Icon = section.icon
                    const data =
                        parsedData[section.key as keyof typeof parsedData] || []

                    return (
                        <div
                            key={section.key}
                            className="rounded-xl border border-gray-800 bg-[#151312] overflow-hidden"
                        >
                            <div className="border-b border-gray-800 px-5 py-4 flex items-center gap-3 bg-[#141210]">
                                <Icon className="w-4 h-4 text-gray-400" />
                                <h2 className="text-white font-semibold text-sm">
                                    {section.title}
                                </h2>
                                <span className="ml-auto bg-[#1e1b18] text-gray-300 text-xs font-medium px-2 py-1 rounded">
                                    {data.length}
                                </span>
                            </div>

                            <div className="p-5">
                                {data.length > 0 ? (
                                    <ul className="space-y-4">
                                        {data.map((item, idx) => (
                                            <li key={idx} className="space-y-1">
                                                <p className="font-medium text-gray-200">
                                                    {item.section}
                                                </p>
                                                <p className="text-gray-400 text-sm leading-relaxed">
                                                    {item.content}
                                                </p>
                                            </li>
                                        ))}
                                    </ul>
                                ) : (
                                    <p className="text-gray-500 text-sm">
                                        No {section.title.toLowerCase()} found in your resume
                                    </p>
                                )}
                            </div>
                        </div>
                    )
                })}
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="rounded-xl border border-gray-800 bg-[#151312] p-6">
                    <h3 className="text-white font-semibold text-lg mb-2">
                        Find jobs
                    </h3>
                    <p className="text-gray-400 text-sm mb-4">
                        Discover job opportunities tailored to your skills and experience.
                    </p>
                    <button className="text-gray-200 hover:text-white font-medium text-sm transition-colors">
                        Explore jobs
                    </button>
                </div>

                <div className="rounded-xl border border-gray-800 bg-[#151312] p-6">
                    <h3 className="text-white font-semibold text-lg mb-2">
                        AI assistant
                    </h3>
                    <p className="text-gray-400 text-sm mb-4">
                        Chat with your AI career co-pilot for personalized guidance.
                    </p>
                    <button className="text-gray-200 hover:text-white font-medium text-sm transition-colors">
                        Start chat
                    </button>
                </div>
            </div>
        </div>
    )
}
