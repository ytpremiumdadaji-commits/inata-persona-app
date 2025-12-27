from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import openai
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# CORS allow karna taaki Vercel frontend isse baat kar sake
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ProfileRequest(BaseModel):
    profile_url: str

# API Keys (Render ke Dashboard mein daalni hongi)
RAPID_API_KEY = os.getenv("RAPID_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

@app.get("/")
def health_check():
    return {"status": "Active", "message": "InstaPersona API is running"}

@app.post("/analyze")
async def analyze_profile(request: ProfileRequest):
    # 1. Instagram Username nikalna URL se
    username = request.profile_url.strip("/").split("/")[-1]
    
    # 2. RapidAPI se Data Fetch karna (Instagram Data Provider API)
    rapid_url = "https://instagram-data1.p.rapidapi.com/user/info"
    headers = {
        "X-RapidAPI-Key": RAPID_API_KEY,
        "X-RapidAPI-Host": "instagram-data1.p.rapidapi.com"
    }
    
    try:
        insta_response = requests.get(rapid_url, headers=headers, params={"username": username})
        data = insta_response.json()
        
        bio = data.get("biography", "No bio available")
        full_name = data.get("full_name", username)
        
        # 3. OpenAI Analysis
        openai.api_key = OPENAI_API_KEY
        prompt = f"""
        Analyze this Instagram profile:
        Name: {full_name}
        Bio: {bio}
        
        Provide a personality analysis in 3 bullet points:
        1. Communication Style
        2. Content Vibe
        3. Potential Audience
        Keep the tone professional and helpful.
        """
        
        ai_res = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )
        
        return {
            "success": True,
            "username": username,
            "full_name": full_name,
            "analysis": ai_res.choices[0].message.content,
            "profile_pic": data.get("profile_pic_url")
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
