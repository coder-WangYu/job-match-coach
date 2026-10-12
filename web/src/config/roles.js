export const ROLES = {
    job_seeker: {
        label: "求职者",
        path: "/job-seeker"
    },
    hr: {
        label: "HR",
        path: "/hr"
    },
    head_hunter: {
        label: "猎头",
        path: "/head-hunter"
    }
}

export const ROLE_OPTIONS = Object.entries(ROLES).map(([value, meta]) => ({
    value,
    label: meta.label
}))
