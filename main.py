from fastapi import FastAPI, HTTPException
import os
import json
import firebase_admin
from firebase_admin import credentials, db
from fastapi.middleware.cors import CORSMiddleware
from transformers import pipeline
import uvicorn

# Initialize FastAPI
app = FastAPI(title="DAI-Model API", description="AI-powered Exam Question Generator", version="1.0")

# Enable CORS (Replace "*" with your frontend domain in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Firebase Setup
firebase_key = os.getenv("FIREBASE_KEY")

if not firebase_key:
    print("❌ ERROR: Firebase key is missing! Check your environment variables.")
    raise ValueError("Firebase key is required.")

try:
    cred = credentials.Certificate(json.loads(firebase_key))
    firebase_admin.initialize_app(cred, {
        "databaseURL": "https://tomnet-amg-default-rtdb.europe-west1.firebasedatabase.app/"
    })
    print("✅ Firebase Initialized Successfully!")
except Exception as e:
    print(f"🔥 Firebase Initialization Error: {e}")
    raise ValueError("Failed to initialize Firebase.")

# Load AI Model on Startup
@app.on_event("startup")
async def load_model():
    global question_generator
    print("⏳ Loading AI Model...")
    try:
        question_generator = pipeline("text2text-generation", model="mrm8488/t5-base-finetuned-question-generation-ap")
        print("✅ AI Model Loaded Successfully!")
    except Exception as e:
        print(f"🔥 AI Model Loading Failed: {e}")
        raise ValueError("Failed to load AI model.")

@app.get("/healthz", tags=["Health Check"])
def health_check():
    """Render uses this route to check if the service is running."""
    return {"status": "ok"}

@app.get("/get_note/{document_id}", tags=["Notes"])
def get_note(document_id: str, num_questions: int = 3):
    """Fetches a note from Firebase and generates multiple creative exam questions using AI."""
    
    # Fetch note from Firebase
    try:
        notes_ref = db.reference("notes").child(document_id)  # Correct path
        note_data = notes_ref.get()

        if not note_data:
            raise HTTPException(status_code=404, detail=f"❌ Note '{document_id}' not found.")

        content = note_data.get("content", "").strip()

        if not content:
            raise HTTPException(status_code=400, detail="❌ Note content is empty.")

        # Generate creative exam questions
        question_prompt = f"Generate {num_questions} diverse and creative exam questions based on: {content}"

        generated_questions = question_generator(
            question_prompt,
            max_length=80,
            num_return_sequences=num_questions,
            do_sample=True,
            top_k=50,
            top_p=0.95,
            temperature=1.2
        )

        questions = [q["generated_text"] for q in generated_questions]

        return {
            "document_id": document_id,
            "topic": note_data.get("topic", ""),
            "content": content,
            "questions": questions
        }

    except Exception as e:
        print(f"🔥 Error fetching/generating questions: {e}")
        raise HTTPException(status_code=500, detail=f"🔥 AI Model Error: {str(e)}")

if __name__ == "__main__":
    port = int(os.getenv("PORT", 10000))  # Default to port 10000
    uvicorn.run(app, host="0.0.0.0", port=port)
