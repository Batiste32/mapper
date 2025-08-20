import { useState } from "react";
import PasswordInput from "./components/PasswordInput";

interface LoginPanelProps {
  setUsername: (u: string) => void;
  setPassword: (p: string) => void;
  setHasDatabase: (b: boolean) => void;
}

export default function LoginPanel({ setUsername, setPassword, setHasDatabase }: LoginPanelProps) {
  const [mode, setMode] = useState<"login" | "register" | "reset">("login");
  const [user, setUser] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPass] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState("");

  const handleSubmit = async () => {
    try {
      console.log("username : ",user," mail : ",email," password : ",password," repeat : ",confirmPassword);

      const route = "/" + mode;
      if ((mode === "register") && (password !== confirmPassword)) {
        alert("Passwords different, please verify them.");
        return;
      }
      const res = await fetch(`${import.meta.env.VITE_API_BASE}${route}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username:user, password, email }),
      });

      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || "Error");
      }
      if (mode === "reset") {
        const data = await res.json();
        alert(`Password successfully changed. Please log in with ${data.temp_password}.`);
        return;
      }
      const data = await res.json();
      setUsername(user);
      setPassword(password);
      setHasDatabase(data.has_db); // backend returns whether DB exists
    } catch (err: any) {
      setError(err.message);
    }
  };

  return (
    <div className="flex flex-col items-center justify-center h-screen bg-midnight">
      <h2 className="text-xl font-bold text-center text-white">
        {mode === "login" ? "Login" : mode === "register" ? "Register" : "Forgot Password"}
      </h2>
      <div className="flex flex-col flex-1 items-center h-1/3 w-1/2 bg-purple m-4 p-4">
        {/* Username */}
        {mode !== "reset" && (
            <input
            type="text"
            value={user}
            onChange={(e) => setUser(e.target.value)}
            placeholder="Username"
            className="bg-midnight hover:bg-lavender w-full m-4 p-4 rounded"
            />
        )}

        {/* Email */}
        {(mode === "register" || mode === "reset") && (
            <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="Email"
            className="bg-midnight hover:bg-lavender w-full m-4 p-4 rounded"
            />
        )}

        {/* Password */}
        {mode !== "reset" && (
            <PasswordInput
            value={password}
            onChange={setPassword}
            placeholder="Password"
            />
        )}

        {/* Confirm Password (register only) */}
        {mode === "register" && (
            <PasswordInput
            value={confirmPassword}
            onChange={setConfirmPassword}
            placeholder="Confirm Password"
            />
        )}

        <button
            onClick={handleSubmit}
            className="bg-midnight text-white m-4 p-4 rounded hover:bg-lavender"
        >
            {mode === "login" ? "Login" : mode === "register" ? "Register" : "Reset Password"}
        </button>
      </div>
      {/* Switch between modes */}
      <div className="text-sm text-gray-300 text-center">
        {mode === "login" && (
          <>
            <button
              onClick={() => setMode("register")}
              className="text-lavender hover:underline mr-2"
            >
              Create an account
            </button>
            <button
              onClick={() => setMode("reset")}
              className="text-lavender hover:underline"
            >
              Forgot Password?
            </button>
          </>
        )}
        {mode === "register" && (
          <button
            onClick={() => setMode("login")}
            className="text-lavender hover:underline"
          >
            Back to Login
          </button>
        )}
        {mode === "reset" && (
          <button
            onClick={() => setMode("login")}
            className="text-lavender hover:underline"
          >
            Back to Login
          </button>
        )}
      </div>
    </div>
  );
}