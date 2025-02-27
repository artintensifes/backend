# from fastapi import FastAPI, HTTPException
# import os
# import json
# import firebase_admin
# from firebase_admin import credentials, db
# from fastapi.middleware.cors import CORSMiddleware
# from transformers import pipeline

# # Initialize FastAPI
# app = FastAPI()

# # Enable CORS (Set allow_origins to your frontend domain for security)
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # Change "*" to your frontend domain in production
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Firebase Setup
# firebase_key = os.getenv("FIREBASE_KEY")

# if firebase_key:
#     cred = credentials.Certificate(json.loads(firebase_key))
#     firebase_admin.initialize_app(cred, {
#         "databaseURL": "https://tomnet-amg-default-rtdb.europe-west1.firebasedatabase.app/"
#     })
# else:
#     raise ValueError("❌ ERROR: Firebase key is missing!")

# # Load AI Model on Startup
# @app.on_event("startup")
# async def load_model():
#     global question_generator
#     print("⏳ Loading AI Model...")
#     question_generator = pipeline("text2text-generation", model="mrm8488/t5-base-finetuned-question-generation-ap")
#     print("✅ AI Model Loaded Successfully!")

# @app.get("/healthz")
# def health_check():
#     """Render uses this route to check if the service is running."""
#     return {"status": "ok"}

# @app.get("/get_note/{document_id}")
# def get_note(document_id: str, num_questions: int = 3):
#     """Fetches a note from Firebase and generates multiple creative questions using AI."""
    
#     # Fetch note from Firebase
#     notes_ref = db.reference(f"notes/{document_id}")
#     note_data = notes_ref.get()

#     if not note_data:
#         raise HTTPException(status_code=404, detail="❌ Document not found")

#     content = note_data.get("content", "").strip()

#     if not content:
#         raise HTTPException(status_code=400, detail="❌ Note content is empty")

#     try:
#         # Generate a more creative and thought-provoking question
#         question_text = (
#             "Generate a creative, thought-provoking exam question based on the following text: " + content
#         )

#         # Generate multiple questions
#         generated_questions = question_generator(
#             question_text,
#             max_length=60,
#             num_return_sequences=num_questions,
#             do_sample=True,  # Enables sampling for diversity
#             top_k=50,        # Limits selection to top 50 words
#             top_p=0.95,      # Nucleus sampling for variety
#             temperature=1.0   # Controls creativity (1.2 for even more diversity)
#         )

#         # Extract generated question texts
#         questions = [q["generated_text"] for q in generated_questions]

#         return {
#             "document_id": document_id,
#             "topic": note_data.get("topic", ""),
#             "content": content,
#             "questions": questions  # Returns an array of multiple creative questions
#         }

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"🔥 AI Model Error: {str(e)}")

# if __name__ == "__main__":
#     port = int(os.environ.get("PORT", 10000))  # Default to 10000 if PORT is not set
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=port)

#############################################

# from fastapi import FastAPI
# import os
# import json
# import firebase_admin
# from firebase_admin import credentials, db
# from fastapi.middleware.cors import CORSMiddleware
# from transformers import pipeline

# # Load Firebase Credentials from Environment Variable
# firebase_key = os.getenv("FIREBASE_KEY")

# if firebase_key:
#     cred = credentials.Certificate(json.loads(firebase_key))
#     firebase_admin.initialize_app(cred, {
#         "databaseURL": "https://tomnet-amg-default-rtdb.europe-west1.firebasedatabase.app/"
#     })
# else:
#     raise ValueError("❌ ERROR: Firebase key is missing! Set the FIREBASE_KEY environment variable.")

# # Initialize FastAPI
# app = FastAPI()

# # Enable CORS (Set allow_origins to your frontend domain for security)
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # Change "*" to your frontend domain in production
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Load T5 Question Generation Model
# print("⏳ Loading AI Model...")
# question_generator = pipeline("text2text-generation", model="mrm8488/t5-base-finetuned-question-generation-ap")
# print("✅ AI Model Loaded Successfully!")

# @app.get("/healthz")
# def health_check():
#     """Render uses this route to check if the service is running."""
#     return {"status": "ok"}

# @app.get("/get_note/{document_id}")
# def get_note(document_id: str):
#     """Fetches a note from Firebase and generates a question using AI."""
    
#     # Fetch note from Firebase
#     notes_ref = db.reference(f"notes/{document_id}")
#     note_data = notes_ref.get()

#     if not note_data:
#         return {"error": "❌ Document not found"}

#     content = note_data.get("content", "").strip()

#     if not content:
#         return {"error": "❌ Note content is empty"}

#     # Generate a question using T5 Model
#     question_text = "generate question: " + content
#     generated_question = question_generator(question_text, max_length=50, num_return_sequences=1)

#     return {
#         "document_id": document_id,
#         "topic": note_data.get("topic", ""),
#         "content": content,
#         "question": generated_question[0]['generated_text'] if generated_question else "⚠ No valid question generated."
#     }

# if __name__ == "__main__":
#     port = int(os.environ.get("PORT", 10000))  # Default to 10000 if PORT is not set
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=port)


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

# ✅ Load Firebase Credentials from Environment Variable
firebase_key = os.getenv("FIREBASE_KEY")

if firebase_key:
    cred = credentials.Certificate(json.loads(firebase_key))
    firebase_admin.initialize_app(cred, {
        "databaseURL": "https://tomnet-amg-default-rtdb.europe-west1.firebasedatabase.app/"
    })
else:
    raise ValueError("❌ ERROR: Firebase key is missing! Set the FIREBASE_KEY environment variable.")

# ✅ Load AI Model on Startup
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

@app.get("/generate_questions/{user_id}")
def generate_questions(user_id: str, num_questions: int = 3):
    """Fetches user preferences from Firebase and generates questions dynamically."""
    
    # Fetch user preferences from Firebase
    user_ref = db.reference(f"user_preferences/{user_id}")
    user_data = user_ref.get()

    if not user_data:
        raise HTTPException(status_code=404, detail="❌ User preferences not found")

    topics = user_data.get("topics", [])

    if not topics:
        raise HTTPException(status_code=400, detail="❌ No topics selected by user")

    generated_questions = []
    
    for topic in topics:
        question_text = f"Generate a question about: {topic}"
        
        # Generate multiple questions for each topic
        try:
            questions = question_generator(
                question_text,
                max_length=60,
                num_return_sequences=num_questions,
                do_sample=True,
                top_k=50,
                top_p=0.95,
                temperature=1.0
            )

            generated_questions.extend([q["generated_text"] for q in questions])

        except Exception as e:
            print(f"🔥 AI Model Error: {str(e)}")
            raise HTTPException(status_code=500, detail=f"🔥 AI Model Error: {str(e)}")

    return {
        "user_id": user_id,
        "topics": topics,
        "questions": generated_questions
    }

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))  # Default to 10000 if PORT is not set
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=port)
