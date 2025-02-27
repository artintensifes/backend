from fastapi import FastAPI, HTTPException
import os
import json
import firebase_admin
from firebase_admin import credentials, db
from fastapi.middleware.cors import CORSMiddleware
from transformers import pipeline

# Initialize FastAPI
app = FastAPI()

# Enable CORS (Set allow_origins to your frontend domain for security)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change "*" to your frontend domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Firebase Setup
firebase_key = os.getenv("FIREBASE_KEY")

if firebase_key:
    cred = credentials.Certificate(json.loads(firebase_key))
    firebase_admin.initialize_app(cred, {
        "databaseURL": "https://tomnet-amg-default-rtdb.europe-west1.firebasedatabase.app/"
    })
else:
    raise ValueError("❌ ERROR: Firebase key is missing!")

# Load AI Model on Startup
@app.on_event("startup")
async def load_model():
    global question_generator
    print("⏳ Loading AI Model...")
    question_generator = pipeline("text2text-generation", model="mrm8488/t5-base-finetuned-question-generation-ap")
    print("✅ AI Model Loaded Successfully!")

@app.get("/healthz")
def health_check():
    """Render uses this route to check if the service is running."""
    return {"status": "ok"}

@app.get("/get_note/{document_id}")
def get_note(document_id: str, num_questions: int = 3):
    """Fetches a note from Firebase and generates multiple creative questions using AI."""
    
    # Fetch note from Firebase
    notes_ref = db.reference(f"notes/{document_id}")
    note_data = notes_ref.get()

    if not note_data:
        raise HTTPException(status_code=404, detail="❌ Document not found")

    content = note_data.get("content", "").strip()

    if not content:
        raise HTTPException(status_code=400, detail="❌ Note content is empty")

    try:
        # Generate a more creative and thought-provoking question
        question_prompt = (
            f"Generate {num_questions} diverse and creative exam questions based on the following content: {content}"
        )

        # Generate multiple questions
        generated_questions = question_generator(
            question_prompt,
            max_length=80,
            num_return_sequences=num_questions,
            do_sample=True,
            top_k=50,
            top_p=0.95,
            temperature=1.2
        )

        # Extract generated question texts
        questions = [q["generated_text"] for q in generated_questions]

        return {
            "document_id": document_id,
            "topic": note_data.get("topic", ""),
            "content": content,
            "questions": questions  # Returns an array of multiple creative questions
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"🔥 AI Model Error: {str(e)}")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))  # Default to 10000 if PORT is not set
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=port)
