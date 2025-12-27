"use client";
import { useState } from 'react';

export default function Home() {
  const [url, setUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  const handleAnalyze = async () => {
    setLoading(true);
    try {
      const response = await fetch('https://YOUR-RENDER-BACKEND-URL.com/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ profile_url: url })
      });
      const data = await response.json();
      setResult(data);
    } catch (error) {
      alert("Error analyzing profile");
    }
    setLoading(false);
  };

  return (
    <main className="min-h-screen bg-gray-50 flex flex-col items-center p-8">
      <h1 className="text-4xl font-bold text-pink-600 mb-4">InstaPersona AI</h1>
      <p className="text-gray-600 mb-8">Get AI insights from any public Instagram profile</p>
      
      <div className="flex gap-2 w-full max-w-md">
        <input 
          className="border p-2 rounded w-full text-black"
          placeholder="https://instagram.com/username"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
        />
        <button 
          onClick={handleAnalyze}
          disabled={loading}
          className="bg-pink-600 text-white px-4 py-2 rounded hover:bg-pink-700 disabled:bg-gray-400"
        >
          {loading ? "Analyzing..." : "Analyze"}
        </button>
      </div>

      {result && (
        <div className="mt-10 p-6 bg-white rounded-lg shadow-xl max-w-2xl w-full">
          <div className="flex items-center gap-4 mb-4">
            <img src={result.profile_pic} className="w-16 h-16 rounded-full border-2 border-pink-500" alt="profile" />
            <h2 className="text-2xl font-semibold text-black">{result.full_name} (@{result.username})</h2>
          </div>
          <div className="prose text-gray-700 whitespace-pre-wrap">
            {result.analysis}
          </div>
        </div>
      )}
    </main>
  );
}
