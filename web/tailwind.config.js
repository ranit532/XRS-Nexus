/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                'nexus-bg': '#0f172a',
                'nexus-card': '#1e293b',
                'nexus-accent': '#3b82f6',
                'nexus-glass': 'rgba(255, 255, 255, 0.05)',
            },
            fontFamily: {
                mono: ['Fira Code', 'monospace'],
            }
        },
    },
    plugins: [],
}
