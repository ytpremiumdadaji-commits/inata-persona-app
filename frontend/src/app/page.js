"use client";
import { useState } from 'react';

export default function Home() {
  const [username, setUsername] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleAnalyze = async () => {
    if (!username) return alert("Please enter a username");
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL;
      const response = await fetch(`${backendUrl}/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username: username.replace('@', '').trim() })
      });

      const data = await response.json();
      if (data.success) {
        setResult(data.data);
      } else {
        setError("User not found or profile is private.");
      }
    } catch (err) {
      setError("Connect error. Check if backend is live.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-slate-50 flex flex-col items-center p-8">
      <h1 className="text-4xl font-bold text-pink-600 mb-8">InstaPersona AI</h1>
      <div className="w-full max-w-md flex gap-2">
        <input 
          className="border p-3 rounded-lg w-full text-black"
          placeholder="Instagram username..."
          value={username}
          onChange={(e) => setUsername(e.target.value)}
        />
        <button 
          onClick={handleAnalyze}
          disabled={loading}
          className="bg-pink-600 text-white px-6 py-3 rounded-lg font-bold disabled:bg-gray-400"
        >
          {loading ? "..." : "Analyze"}
        </button>
      </div>

      {error && <p className="text-red-500 mt-4">{error}</p>}

      {result && (
        <div className="mt-10 p-8 bg-white rounded-2xl shadow-xl max-w-xl w-full border">
          <div className="flex items-center gap-4 mb-6">
            <img src={result.profile_pic} className="w-20 h-20 rounded-full border-2 border-pink-500" alt="pfp" />
            <div>
              <h2 className="text-2xl font-bold text-black">{result.name}</h2>
              <p className="text-gray-500">@{result.username} • {result.followers} Followers</p>
            </div>
          </div>
          <div className="bg-pink-50 p-4 rounded-xl text-gray-800 italic">
            {result.personality_report}
          </div>
        </div>
      )}
    </main>
  );
}
