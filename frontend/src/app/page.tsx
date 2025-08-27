"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Image from "next/image";
import { Loader2, Stethoscope, Code2, FlaskConical } from "lucide-react";

const API_URL = process.env.NEXT_PUBLIC_API_URL;

export default function Home() {
  const [role, setRole] = useState("clinician");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  const handleLogin = async () => {
    setLoading(true);
    setError(null);

    try {
      const res = await fetch(`${API_URL}/token`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ role }),
      });

      if (!res.ok) {
        throw new Error(`Login failed: ${res.status}`);
      }

      const data = await res.json();

      if (data.access_token) {
        localStorage.setItem("token", data.access_token);
        localStorage.setItem("role", role);
        router.push("/patients");
      } else {
        setError("No token received from server.");
      }
    } catch (err) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError("Unexpected error occurred.");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen flex flex-col md:flex-row bg-gradient-to-br from-blue-50 via-white to-blue-100 dark:from-gray-900 dark:via-gray-950 dark:to-gray-900 transition-colors">
      {/* Left branding section */}
      <div className="flex-1 flex flex-col justify-center items-center p-10 text-center bg-gradient-to-br from-blue-100 to-blue-50 dark:from-gray-800 dark:to-gray-900">
        <Image
          src="/logo.png"
          alt="InnoGuard Logo"
          width={80}
          height={80}
          className="rounded-2xl shadow-lg border border-gray-200 mb-6"
          priority
        />
        <h1 className="text-5xl font-extrabold text-gray-800 dark:text-white mb-4">
          InnoGuard
        </h1>
        <p className="text-lg text-gray-600 dark:text-gray-300 max-w-md">
          The{" "}
          <span className="font-semibold text-blue-600 dark:text-blue-400">
            Smart Security Guard
          </span>{" "}
          for Sensitive Data. Designed for doctors, researchers, and developers.
        </p>
      </div>

      {/* Right login section */}
      <div className="flex-1 flex items-center justify-center p-8">
        <div className="w-full max-w-md backdrop-blur-lg bg-white/80 dark:bg-gray-800/80 rounded-2xl shadow-xl border border-gray-200 dark:border-gray-700 p-8 space-y-6">
          <h2 className="text-2xl font-bold text-center text-gray-800 dark:text-white">
            Secure Access
          </h2>

          {/* Role Selection */}
          <div>
            <label className="text-sm font-medium text-gray-700 dark:text-gray-300 block mb-3">
              Choose Your Role
            </label>
            <div className="grid grid-cols-3 gap-3">
              {[
                {
                  id: "clinician",
                  label: "Doctor",
                  icon: <Stethoscope className="w-6 h-6" />,
                },
                {
                  id: "developer",
                  label: "Developer",
                  icon: <Code2 className="w-6 h-6" />,
                },
                {
                  id: "researcher",
                  label: "Researcher",
                  icon: <FlaskConical className="w-6 h-6" />,
                },
              ].map(({ id, label, icon }) => (
                <button
                  key={id}
                  onClick={() => setRole(id)}
                  className={`relative flex flex-col items-center justify-center p-4 rounded-xl border-2 transition-all duration-200
                    ${
                      role === id
                        ? "border-blue-600 shadow-md scale-105 bg-white dark:bg-gray-900"
                        : "border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-900 hover:border-blue-300 dark:hover:border-blue-600"
                    }`}
                >
                  {icon}
                  <span className="mt-2 text-sm font-medium">{label}</span>
                </button>
              ))}
            </div>
          </div>

          {/* Login button */}
          <div className="space-y-3">
            <button
              onClick={handleLogin}
              disabled={loading}
              className="w-full flex items-center justify-center gap-2 bg-gradient-to-r from-blue-600 to-blue-500 text-white font-semibold py-3 rounded-full hover:from-blue-700 hover:to-blue-600 transition disabled:opacity-50 shadow-lg"
            >
              {loading ? (
                <>
                  <Loader2 className="animate-spin w-5 h-5" />
                  <span>Securing Session...</span>
                </>
              ) : (
                <span>
                  {role === "clinician"
                    ? "Continue as Doctor"
                    : role === "developer"
                    ? "Continue as Developer"
                    : "Continue as Researcher"}
                </span>
              )}
            </button>

            <p className="text-xs text-gray-500 dark:text-gray-400 text-center">
              Your session will be protected with role-based access control.
            </p>
          </div>

          {/* Error message */}
          {error && (
            <p className="text-red-600 dark:text-red-400 text-sm text-center font-medium animate-pulse">
              {error}
            </p>
          )}

          <p className="text-xs text-gray-500 dark:text-gray-400 text-center mt-6">
            © {new Date().getFullYear()} InnoGuard. All rights reserved.
          </p>
        </div>
      </div>
    </main>
  );
}
