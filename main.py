# from fastapi import FastAPI
# import firebase_admin
# from firebase_admin import credentials, db
# from fastapi.middleware.cors import CORSMiddleware

# # Initialize Firebase
# cred = credentials.Certificate("serviceAccountKey.json")  
# firebase_admin.initialize_app(cred, {
#     "databaseURL": "https://tomnet-amg-default-rtdb.europe-west1.firebasedatabase.app/"
# })

# # Initialize FastAPI
# app = FastAPI()

# # Enable CORS (Allows Flutter Web to fetch data)
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # Change "*" to specific domain for security in production
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# @app.get("/get_note/{document_id}")
# def get_note(document_id: str):
#     # Fetch note from Firebase
#     notes_ref = db.reference(f"notes/{document_id}")
#     note_data = notes_ref.get()

#     if not note_data:
#         return {"error": "Document not found"}

#     return {
#         "document_id": document_id,
#         "topic": note_data.get("topic", ""),
#         "content": note_data.get("content", "")
#     }

from fastapi import FastAPI
import firebase_admin
from firebase_admin import credentials, db
from fastapi.middleware.cors import CORSMiddleware
from transformers import pipeline

# Initialize Firebase
cred = credentials.Certificate("FIREBASE_KEY")  
firebase_admin.initialize_app(cred, {
    "databaseURL": "https://tomnet-amg-default-rtdb.europe-west1.firebasedatabase.app/"
})

# Initialize FastAPI
app = FastAPI()

# Enable CORS (Allows Flutter Web to fetch data)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change "*" to specific domain for security in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load T5 Question Generation Model
question_generator = pipeline("text2text-generation", model="mrm8488/t5-base-finetuned-question-generation-ap")

@app.get("/get_note/{document_id}")
def get_note(document_id: str):
    # Fetch note from Firebase
    notes_ref = db.reference(f"notes/{document_id}")
    note_data = notes_ref.get()

    if not note_data:
        return {"error": "Document not found"}

    content = note_data.get("content", "")

    # Generate questions using AI
    question_text = "generate question: " + content
    generated_question = question_generator(question_text, max_length=50, num_return_sequences=1)

    return {
        "document_id": document_id,
        "topic": note_data.get("topic", ""),
        "content": content,
        "question": generated_question[0]['generated_text'] if generated_question else "No question generated"
    }
