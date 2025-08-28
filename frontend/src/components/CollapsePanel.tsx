import { useState } from "react";
import { ChevronLeft, ChevronRight } from "lucide-react";

type CollapsePanelProps = {
  direction: "left" | "right";
  children: React.ReactNode;
  className?: string;
};

export default function CollapsePanel({ direction, children, className }: CollapsePanelProps) {
  const [collapsed, setCollapsed] = useState(false);

  return (
    <div
      className={`relative flex transition-all duration-300 ${
        collapsed ? "w-6" : className ?? "w-1/3"
      }`}
    >
      {/* Content (hidden when collapsed) */}
      {!collapsed && (
        <div className="flex-1 overflow-auto bg-midnight">
          {children}
        </div>
      )}

      {/* Collapse / Expand Button */}
      <button
        onClick={() => setCollapsed(!collapsed)}
        className={`absolute top-1/2 -translate-y-1/2 bg-gray-800 text-white p-1 rounded-full shadow-md hover:bg-gray-700 ${
          direction === "left" ? "right-0 translate-x-1/2" : "left-0 -translate-x-1/2"
        }`}
      >
        {collapsed
          ? direction === "left"
            ? <ChevronRight size={16} />
            : <ChevronLeft size={16} />
          : direction === "left"
            ? <ChevronLeft size={16} />
            : <ChevronRight size={16} />}
      </button>
    </div>
  );
}
