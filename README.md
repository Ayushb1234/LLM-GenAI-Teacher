# AI Tutor System

A smarter way to learn — powered by NLP, LLMs, multi-language voice interaction, and adaptive topic simplification.

# Overview

AI Tutor System is an intelligent learning assistant that transforms raw documents (PDFs, text files, or notes) into easy-to-understand, structured learning content.

The system extracts text → generates chapter-wise sections → simplifies content using an LLM → explains concepts interactively using a whiteboard-based React UI with voice-enabled explanation, refinement learning, and multi-language support.

It’s basically ChatGPT meets Khan Academy vibes 👇
📄 → 🧠 AI Understanding → 🎯 Simplified Lessons → 🗣 Interactive Learning

# Key Features

Feature	Description

📄 Document Upload	Upload PDFs, text files, or raw notes

🔍 Text Extraction	OCR + NLP-based parsing for clean structured text

🧩 Auto Chapter Generation	AI groups content into chapters + subtopics

🧠 LLM-Powered Simplification	Converts complex content → simple explanations

🎨 React Whiteboard	Visual learning with drawings, highlights & annotations

🎤 Voice Support	Listen to chapters in multiple languages

🔁 Refinement Mode	If the user doesn’t understand — content is re-explained with examples

🌎 Multi-Language Output	Explains content in the user’s preferred language

👤 Personalized Learning	Tracks user difficulty → adapts teaching style

# Tech Stack

Layer	Technologies

Frontend	React, Tailwind / Chakra UI, React-Whiteboard, Web Speech API

Backend	FastAPI / Django (choose based on stack)

AI / NLP	OpenAI / Llama / Groq, SpaCy, LangChain

Text Extraction	PyPDF2, Tesseract OCR

Audio	gTTS / Vosk / Whisper

Storage	PostgreSQL / MongoDB

Deployment	Docker, Vercel / AWS / Render


 # System Architecture

<img width="618" height="507" alt="image" src="https://github.com/user-attachments/assets/7f93a58a-a933-4484-b179-42efa9d9e46d" />


 # Installation

# Clone the repo
```
git clone https://github.com/<your-username>/ai-tutor-system.git

cd ai-tutor-system
```

# Backend setup
```
cd backend
pip install -r requirements.txt
```

# Frontend setup
```
cd ../frontend
npm install
```

▶️ Run the Project

# Start backend

```
cd backend
uvicorn app:app --reload
```
# Start frontend
```
cd frontend
npm run dev
```

## 🎮 Demo & Screenshots
-------------------------

<img width="1898" height="955" alt="image" src="https://github.com/user-attachments/assets/2da18f01-f61c-40a4-b584-50608882daf4" />

<img width="1303" height="661" alt="image" src="https://github.com/user-attachments/assets/6b457c6d-9a06-43ee-b8ae-5318de4bc9df" />



## 📚 Future Enhancements
-----------------------------

🧬 Adaptive Learning Model (difficulty scoring)

🎓 Quiz & Auto-Feedback

🏆 Student Progress Dashboard

🧩 Offline Mode

## 🤝 Contributing
--------------------

Pull requests are welcome! For major changes, please open an issue to discuss your idea first.

## 📄 License
-----------------

MIT License — free to use, modify, and build on.

## ✨ Author
--------------

Ayush Choudhary
🚀 AI/ML Developer | Backend Engineer | NLP Enthusiast
🔗 GitHub · LinkedIn · Portfolio (add links)
