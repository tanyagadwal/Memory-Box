🧾 1. PRD for “Memory Box” — Production-Ready Version
✨ Product Vision
Memory Box is a beautifully designed web app that lets users upload screenshots of chat conversations (e.g., WhatsApp), extract structured messages from them using advanced OCR or LLMs, and store them in categorized, searchable chat repositories — almost like a private museum of memories.

🎯 Core Features
📤 Upload
Drag & drop + multi-file upload support

Accept image formats: JPG, PNG, WebP

Option to assign:

Title

Category

Tags (optional)

🔍 Chat Extraction
Use smart OCR (see next section)

Parse sender, timestamp, message

Maintain order of screenshots (chronological stitching)

LLM fallback if OCR fails

🗂️ Chat Management
View all chats in a grid/list view

Filter/sort by category, date, tags

View full chat thread in bubble format

Edit metadata (title/category)

Delete chats

🧠 Optional Extras (Post-MVP)
Full-text search inside messages

Pin conversations / favorite messages

Tag people/entities via LLM

Export to PDF / Markdown

End-to-end encryption or secure login

Offline support (PWA)

🖌️ Design & Aesthetics (Tailwind Themes)
Modern, calm, and nostalgic palette (lavenders, off-whites, soft indigos)

Bubble-based chat interface (like iMessage)

Animations: subtle fade/slide for uploads, messages

Mobile-first responsive layout

Use Tailwind’s @apply + clsx for tidy component styles

🧪 Dev & Infra Plan

Area	Stack / Notes
Frontend	React + React Router + Tailwind CSS
Backend	FastAPI (already great)
OCR Engine	See section below 👇
LLM Support	Optionally integrate HuggingFace Inference API or local model
DB	Supabase (easy + real-time) or PostgreSQL
Auth (later)	Clerk/Auth.js/Firebase or custom OAuth
Hosting	Frontend: Vercel / Netlify
Backend: Render / Railway