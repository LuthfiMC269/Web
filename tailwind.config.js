/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './templates/**/*.html',
    './static/**/*.js',
  ],
  theme: {
    extend: {
  fontFamily: {
    poppins: ['Poppins', 'sans-serif'],
    sans: ['Poppins', 'sans-serif'],
  },
  },
  },
  plugins: [],
}
