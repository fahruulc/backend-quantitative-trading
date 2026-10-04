/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{vue,js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                finbase: '#0B0E14',
                fincard: '#141920',
                finborder: '#1E2736',
                fingreen: '#00C076',
                finred: '#F23645',
                finblue: '#2962FF',
                finyellow: '#F5A623',
            },
            fontFamily: {
                sans: ['Inter', 'sans-serif'],
                mono: ['JetBrains Mono', 'monospace'],
            },
            boxShadow: {
                'glow-green': '0 0 20px rgba(0,192,118,0.25)',
                'glow-blue': '0 0 20px rgba(41,98,255,0.25)',
                'glow-red': '0 0 20px rgba(242,54,69,0.25)',
            }
        },
    },
    plugins: [],
}
