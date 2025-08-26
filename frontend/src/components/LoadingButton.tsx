import { useState } from "react";

type LoadingButtonProps = {
  text: string;
  loadingParameter: boolean;
  onClick: () => void;
};

export default function LoadingButton({ text, loadingParameter, onClick }: LoadingButtonProps) {
  return (
    <button
      onClick={onClick}
      disabled={loadingParameter}
      className="relative flex items-center justify-center m-4 p-4 rounded-lg bg-midnight text-white hover:bg-lavender disabled:opacity-50 disabled:cursor-wait"
    >
      {loadingParameter ? (
        <svg
          className="animate-spin h-5 w-5 text-white"
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
        >
          <circle
            className="opacity-25"
            cx="12"
            cy="12"
            r="10"
            stroke="currentColor"
            strokeWidth="4"
          />
          <path
            className="opacity-75"
            fill="currentColor"
            d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z"
          />
        </svg>
      ) : (
        text
      )}
    </button>
  );
}
