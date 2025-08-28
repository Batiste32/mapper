import { useState } from "react";
import { ChevronLeft, ChevronRight, ChevronUp, ChevronDown } from "lucide-react";

type CollapseButtonProps = {
  direction?: "left" | "right" | "top" | "bottom";
  children: React.ReactNode; // panel content
  className?: string;
};

export default function CollapsePanel({ direction = "left", children, className }: CollapseButtonProps) {
  const [collapsed, setCollapsed] = useState(false);

  const toggle = () => setCollapsed((prev) => !prev);

  // Icon depending on direction + state
  const getIcon = () => {
    if (direction === "left") return collapsed ? <ChevronRight /> : <ChevronLeft />;
    if (direction === "right") return collapsed ? <ChevronLeft /> : <ChevronRight />;
    if (direction === "top") return collapsed ? <ChevronDown /> : <ChevronUp />;
    if (direction === "bottom") return collapsed ? <ChevronUp /> : <ChevronDown />;
  };

  // Tailwind classes for positioning the button
  const buttonPosition =
    direction === "left"
      ? "top-1/2 -right-3"
      : direction === "right"
      ? "top-1/2 -left-3"
      : direction === "top"
      ? "left-1/2 -bottom-3"
      : "left-1/2 -top-3";

  return (
    <div
      className={`relative bg-gray-800 text-white transition-all duration-300 ${
        collapsed
          ? direction === "left" || direction === "right"
            ? "w-0 overflow-hidden"
            : "h-0 overflow-hidden"
          : ""
      } ${className}`}
    >
      {/* Panel content */}
      {!collapsed && <div className="p-4">{children}</div>}

      {/* Collapse/Expand button */}
      <button
        onClick={toggle}
        className={`absolute ${buttonPosition} transform -translate-y-1/2 -translate-x-1/2 bg-purple-600 hover:bg-purple-700 p-1 rounded-full shadow`}
      >
        {getIcon()}
      </button>
    </div>
  );
}
