"use client";

import { useState } from "react";
import { signInWithPopup, signOut } from "firebase/auth";
import { auth, googleProvider, githubProvider } from "../../_utils/firebase";

export default function OAuth2FA() {
  const [user, setUser] = useState(null);
  const [twoFACode, setTwoFACode] = useState("");
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [isTwoFAVerified, setIsTwoFAVerified] = useState(false);

  const buttonStyle =
    "bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded transition";

  const sendOtpToBackend = async (firebaseUser) => {
    const token = await firebaseUser.getIdToken();

    const response = await fetch("/auth/send-otp", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail || "Failed to send OTP");
    }

    setMessage("2FA code sent to your email.");
  };

  const handleGoogleLogin = async () => {
    try {
      setError("");
      setMessage("");
      setIsTwoFAVerified(false);

      const result = await signInWithPopup(auth, googleProvider);
      setUser(result.user);
      await sendOtpToBackend(result.user);
    } catch (err) {
      console.error("Google login error:", err);
      setError(err.message || "Google login failed or OTP could not be sent.");
    }
  };

  const handleGithubLogin = async () => {
    try {
      setError("");
      setMessage("");
      setIsTwoFAVerified(false);

      const result = await signInWithPopup(auth, githubProvider);
      setUser(result.user);
      await sendOtpToBackend(result.user);
    } catch (err) {
      console.error("GitHub login error:", err);
      setError(err.message || "GitHub login failed or OTP could not be sent.");
    }
  };

  const handleVerify2FA = async () => {
    try {
      setError("");
      setMessage("");

      if (!user) {
        setError("Please log in first.");
        return;
      }

      const token = await user.getIdToken();

      const response = await fetch("/auth/verify-otp", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ code: twoFACode }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "OTP verification failed");
      }

      setIsTwoFAVerified(true);
      setMessage("2FA verified successfully.");
    } catch (err) {
      console.error("2FA verification error:", err);
      setError(err.message || "Verification failed.");
    }
  };

  const handleLogout = async () => {
    try {
      await signOut(auth);
      setUser(null);
      setTwoFACode("");
      setError("");
      setMessage("");
      setIsTwoFAVerified(false);
    } catch (err) {
      console.error("Logout error:", err);
      setError("Logout failed. Please try again.");
    }
  };

  return (
    <section className="mt-8">
      <h2 className="text-2xl font-semibold mb-4">OAuth & 2FA Integration</h2>

      <div className="bg-white rounded-lg shadow p-4 dark:bg-gray-900 dark:text-gray-100">
        <p className="font-semibold mb-3">Secure Login</p>

        <div className="flex gap-3 flex-wrap mb-4">
          <button onClick={handleGoogleLogin} className={buttonStyle}>
            Login with Google
          </button>

          <button onClick={handleGithubLogin} className={buttonStyle}>
            Login with GitHub
          </button>

          {user && (
            <button
              onClick={handleLogout}
              className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded transition"
            >
              Logout
            </button>
          )}
        </div>

        {user && (
          <div className="mb-4 p-3 border rounded bg-gray-50 dark:bg-gray-800">
            <p className="text-sm">
              <span className="font-semibold">Signed in as:</span>{" "}
              {user.displayName || "No name"}
            </p>
            <p className="text-sm">{user.email || "No email available"}</p>
            <p className="text-sm mt-2">
              <span className="font-semibold">2FA status:</span>{" "}
              {isTwoFAVerified ? "Verified" : "Pending"}
            </p>
          </div>
        )}

        {message && <p className="text-green-500 text-sm mb-3">{message}</p>}
        {error && <p className="text-red-500 text-sm mb-3">{error}</p>}

        <label className="block text-sm font-medium mb-2">Enter 2FA Code</label>

        <div className="flex gap-3">
          <input
            type="text"
            placeholder="Enter your 2FA code"
            value={twoFACode}
            onChange={(e) => setTwoFACode(e.target.value)}
            className="w-full border border-gray-300 rounded px-3 py-2 text-black dark:text-white"
          />
          <button
            onClick={handleVerify2FA}
            className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded transition"
          >
            Verify
          </button>
        </div>
      </div>
    </section>
  );
}