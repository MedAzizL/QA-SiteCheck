/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {   
     extend: {
      fontFamily: {
        sans: ['Inter', 'ui-sans-serif', 'system-ui', '-apple-system', 'Segoe UI', 'Roboto', 'Arial'],
      },
      colors: {
        th: {
          blue: "#0052FF",
          blueHover: "#0041CC",
          bg: "#FAFAFA",
          surface: "#FFFFFF",
          border: "#E5E7EB",
          border2: "#D1D5DB",
          heading: "#1A1A1A",
          body: "#374151",
          secondary: "#6B7280",
          muted: "#9CA3AF",
          success: "#10B981",
          warning: "#F59E0B",
          error: "#EF4444",
          info: "#3B82F6",
        },
      },
      boxShadow: {
        card: "0 1px 3px rgba(0,0,0,0.05)",
      },
    },
  },
  plugins: [],
};
