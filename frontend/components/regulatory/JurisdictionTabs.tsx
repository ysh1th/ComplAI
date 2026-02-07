"use client";

import { CountryFlag } from "@/components/shared/CountryFlag";
import { cn } from "@/lib/utils";

interface JurisdictionTabsProps {
  active: string;
  onSelect: (code: string) => void;
}

const tabs = [
  { code: "MT", label: "Malta" },
  { code: "AE", label: "UAE" },
  { code: "KY", label: "Cayman Islands" },
];

export function JurisdictionTabs({ active, onSelect }: JurisdictionTabsProps) {
  return (
    <div className="flex gap-1 bg-deriv-dark-card rounded-xl p-1 border border-deriv-dark-border">
      {tabs.map((tab) => (
        <button
          key={tab.code}
          onClick={() => onSelect(tab.code)}
          className={cn(
            "flex items-center gap-2 px-5 py-3 rounded-lg text-sm font-medium transition-all flex-1 justify-center",
            active === tab.code
              ? "bg-deriv-red/10 text-deriv-red border border-deriv-red/20"
              : "text-deriv-grey hover:text-white hover:bg-white/5 border border-transparent"
          )}
        >
          <CountryFlag code={tab.code} size="sm" />
          <span>{tab.label}</span>
        </button>
      ))}
    </div>
  );
}
