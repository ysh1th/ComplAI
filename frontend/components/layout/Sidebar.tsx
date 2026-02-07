"use client";

import { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Shield,
  Activity,
  BookOpen,
  ChevronLeft,
  ChevronRight,
} from "lucide-react";
import { ThemeToggle } from "./ThemeToggle";
import { cn } from "@/lib/utils";

const navItems = [
  {
    label: "Live Monitor",
    href: "/monitor",
    icon: Activity,
  },
  {
    label: "Regulatory Hub",
    href: "/regulatory",
    icon: BookOpen,
  },
];

export function Sidebar() {
  const [collapsed, setCollapsed] = useState(false);
  const pathname = usePathname();

  return (
    <aside
      className={cn(
        "h-screen flex flex-col border-r transition-all duration-300",
        "bg-deriv-dark-card border-deriv-dark-border",
        "[data-theme='light']_&:bg-light-card [data-theme='light']_&:border-light-border",
        collapsed ? "w-16" : "w-60"
      )}
      style={{
        width: collapsed ? 64 : 240,
        minWidth: collapsed ? 64 : 240,
      }}
    >
      {/* Logo */}
      <div className="flex items-center gap-3 px-4 h-16 border-b border-deriv-dark-border">
        <Shield className="w-8 h-8 text-deriv-red shrink-0" />
        {!collapsed && (
          <div className="overflow-hidden">
            <span className="text-base font-bold text-white whitespace-nowrap">
              ComplAi
            </span>
            <span className="block text-xs text-deriv-grey whitespace-nowrap">
              Compliance Manager
            </span>
          </div>
        )}
      </div>

      {/* Navigation */}
      <nav className="flex-1 py-4 space-y-1 px-2">
        {navItems.map((item) => {
          const isActive = pathname.startsWith(item.href);
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center gap-3 px-3 py-2.5 rounded-lg transition-colors text-sm",
                isActive
                  ? "bg-deriv-red/10 text-deriv-red font-semibold"
                  : "text-deriv-grey hover:text-white hover:bg-white/5"
              )}
            >
              <item.icon className="w-5 h-5 shrink-0" />
              {!collapsed && <span>{item.label}</span>}
            </Link>
          );
        })}
      </nav>

      {/* Footer */}
      <div className="border-t border-deriv-dark-border p-3 space-y-2">
        <ThemeToggle collapsed={collapsed} />
        <button
          onClick={() => setCollapsed(!collapsed)}
          className="flex items-center gap-2 w-full px-2 py-1.5 rounded text-deriv-grey hover:text-white text-xs transition-colors"
        >
          {collapsed ? (
            <ChevronRight className="w-4 h-4 mx-auto" />
          ) : (
            <>
              <ChevronLeft className="w-4 h-4" />
              <span>Collapse</span>
            </>
          )}
        </button>
      </div>
    </aside>
  );
}
