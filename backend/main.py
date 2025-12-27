import os
import requests
import openai
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# Environment variables load karein
load_dotenv()

app = FastAPI()

# Frontend (Vercel) ko backend se baat karne ki permission dena
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request Model
class AnalyzeRequest(BaseModel):
    username: str

# Configuration (Render Dashboard mein set karein)
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
RAPID_API_KEY = os.getenv("RAPID_API_KEY")
RAPID_API_HOST = "instagram-profile-data-api.p.rapidapi.com"

@app.get("/")
def health_check():
    return {"status": "success", "message": "Backend is live and using OpenRouter!"}

@app.post("/analyze")
async def get_personality(request: AnalyzeRequest):
    # 1. Instagram Data Fetching
    # Hum 'User Info' endpoint use kar rahe hain
    insta_url = f"https://{RAPID_API_HOST}/user/info"
    headers = {
        "X-RapidAPI-Key": RAPID_API_KEY,
        "X-RapidAPI-Host": RAPID_API_HOST
    }

    try:
        # API se data mangwana
        insta_res = requests.get(insta_url, headers=headers, params={"username": request.username})
        
        if insta_res.status_code != 200:
            raise HTTPException(status_code=404, detail="Instagram profile not found")
            
        data = insta_res.json()
        
        # Profile details nikalna
        bio = data.get("biography", "No bio available")
        full_name = data.get("full_name", request.username)
        profile_pic = data.get("profile_pic_url", "")
        followers = data.get("follower_count", 0)

        # 2. OpenRouter AI Analysis (DeepSeek-R1 Free)
        # OpenAI ki library ko OpenRouter ke base URL par redirect karna
        openai.api_key = OPENROUTER_API_KEY
        openai.api_base = "https://openrouter.ai/api/v1"

        prompt = f"""
        Analyze the Instagram personality of {full_name} (@{request.username}).
        Bio: {bio}
        Followers: {followers}
        
        Task: Provide a creative 3-point personality analysis, their 'vibe' check, 
        and a 'fun fact' based on their profile data. Keep it engaging and respectful.
        """

        # OpenRouter Call
        ai_res = openai.ChatCompletion.create(
            model="tngtech/deepseek-r1t-chimera:free",
            messages=[
                {"role": "system", "content": "You are a professional social media behavior analyst."},
                {"role": "user", "content": prompt}
            ],
            headers={
                "HTTP-Referer": "https://instapersona.vercel.app", # Aapka Vercel URL
                "X-Title": "InstaPersona AI"
            }
        )

        # 3. Final Result return karna
        return {
            "success": True,
            "data": {
                "name": full_name,
                "username": request.username,
                "profile_pic": profile_pic,
                "followers": followers,
                "personality_report": ai_res.choices[0].message.content
            }
        }

    except Exception as e:
        print(f"Error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail="Analysis failed. Check API keys or username.")

