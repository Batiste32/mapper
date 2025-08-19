import { useState } from "react";
import PasswordInput from "./components/PasswordInput";

interface LoginPanelProps {
  setUsername: (u: string) => void;
  setHasDatabase: (b: boolean) => void;
}

export default function LoginPanel({ setUsername, setHasDatabase }: LoginPanelProps) {
  const [user, setUser] = useState("");
  const [password, setPassword] = useState("");
  const [isRegister, setIsRegister] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async () => {
    try {
      const route = isRegister ? "/register" : "/login";
      console.log("username : ",user," password : ",password)
      const res = await fetch(`${import.meta.env.VITE_API_BASE}${route}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user, password }),
      });

      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || "Error");
      }

      const data = await res.json();
      setUsername(user);
      setHasDatabase(data.has_db); // backend returns whether DB exists
    } catch (err: any) {
      setError(err.message);
    }
  };

  return (
    <div className="flex flex-col items-center justify-center h-screen bg-midnight text-white">
      <h1 className="text-2xl mb-4">{isRegister ? "Register" : "Login"}</h1>
      <div className="flex flex-col h-1/2 w-1/2 m-4 p-4 items-center justify-center bg-purple">
        <input
            type="text"
            placeholder="Username"
            value={user}
            onChange={(e) => setUser(e.target.value)}
            className="relative w-full m-4 p-4 rounded text-white bg-midnight hover:bg-lavender"
        />
        <PasswordInput value={password} onChange={setPassword} placeholder="Password"/>
        {error && <p className="text-red-400 mb-2">{error}</p>}
        <button
            onClick={handleSubmit}
            className="bg-midnight hover:bg-lavender p-2 rounded mb-2 w-32"
        >
            {isRegister ? "Register" : "Login"}
        </button>
      </div>
    <button
        onClick={() => setIsRegister(!isRegister)}
        className="underline text-sm"
    >
        {isRegister ? "Already have an account? Login" : "New user? Register"}
    </button>
    </div>
  );
}
