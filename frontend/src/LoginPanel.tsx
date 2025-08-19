import { useState } from "react";

interface LoginPanelProps {
  setUsername: (u: string) => void;
  setHasDatabase: (b: boolean) => void;
}

export default function LoginPanel({ setUsername, setHasDatabase }: LoginPanelProps) {
  const [username, setU] = useState("");
  const [password, setP] = useState("");
  const [isRegister, setIsRegister] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async () => {
    try {
      const route = isRegister ? "/register" : "/login";
      const res = await fetch(`${import.meta.env.VITE_API_BASE}${route}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
      });

      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || "Error");
      }

      const data = await res.json();
      setUsername(username);
      setHasDatabase(data.has_db); // backend returns whether DB exists
    } catch (err: any) {
      setError(err.message);
    }
  };

  return (
    <div className="flex flex-col items-center justify-center h-screen bg-purple text-white">
      <h1 className="text-2xl mb-4">{isRegister ? "Register" : "Login"}</h1>
      <input
        type="text"
        placeholder="Username"
        value={username}
        onChange={(e) => setU(e.target.value)}
        className="p-2 mb-2 rounded text-white bg-purple hover:bg-lavender"
      />
      <input
        type="password"
        placeholder="Password"
        value={password}
        onChange={(e) => setP(e.target.value)}
        className="p-2 mb-2 rounded text-white bg-purple hover:bg-lavender"
      />
      {error && <p className="text-red-400 mb-2">{error}</p>}
      <button
        onClick={handleSubmit}
        className="bg-purple hover:bg-lavender p-2 rounded mb-2 w-32"
      >
        {isRegister ? "Register" : "Login"}
      </button>
      <button
        onClick={() => setIsRegister(!isRegister)}
        className="underline text-sm"
      >
        {isRegister ? "Already have an account? Login" : "New user? Register"}
      </button>
    </div>
  );
}
