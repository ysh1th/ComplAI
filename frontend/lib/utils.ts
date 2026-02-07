import type { RiskBand } from "./types";

export function cn(...classes: (string | boolean | undefined | null)[]) {
  return classes.filter(Boolean).join(" ");
}

export function getRiskColor(band: RiskBand): string {
  switch (band) {
    case "HIGH":
      return "#FF444F";
    case "MEDIUM":
      return "#F5A623";
    case "LOW":
      return "#00A79E";
    case "CLEAN":
      return "#6B7280";
  }
}

export function getRiskBgClass(band: RiskBand): string {
  switch (band) {
    case "HIGH":
      return "bg-deriv-red";
    case "MEDIUM":
      return "bg-deriv-amber";
    case "LOW":
      return "bg-deriv-teal";
    case "CLEAN":
      return "bg-deriv-grey";
  }
}

export function getStatusColor(status: string): string {
  switch (status) {
    case "success":
      return "#00A79E";
    case "alert":
      return "#F5A623";
    case "high":
      return "#FF444F";
    case "complete":
      return "#00A79E";
    case "error":
      return "#FF444F";
    default:
      return "#6B7280";
  }
}

export function getCountryFlag(code: string): string {
  const flags: Record<string, string> = {
    MT: "🇲🇹",
    AE: "🇦🇪",
    KY: "🇰🇾",
    IT: "🇮🇹",
    DE: "🇩🇪",
    GB: "🇬🇧",
    SA: "🇸🇦",
    BH: "🇧🇭",
    PK: "🇵🇰",
    US: "🇺🇸",
    KP: "🇰🇵",
    IR: "🇮🇷",
    SY: "🇸🇾",
    CU: "🇨🇺",
    RU: "🇷🇺",
    CN: "🇨🇳",
    JP: "🇯🇵",
    IN: "🇮🇳",
  };
  return flags[code] || "🏳️";
}

export function getJurisdictionName(code: string): string {
  return getCountryName(code);
}

export function getCountryName(code: string): string {
  const names: Record<string, string> = {
    MT: "Malta",
    AE: "UAE",
    KY: "Cayman Islands",
    IT: "Italy",
    DE: "Germany",
    GB: "United Kingdom",
    SA: "Saudi Arabia",
    BH: "Bahrain",
    PK: "Pakistan",
    US: "United States",
    KP: "North Korea",
    IR: "Iran",
    SY: "Syria",
    CU: "Cuba",
    RU: "Russia",
    CN: "China",
    JP: "Japan",
    IN: "India",
    SG: "Singapore",
    NG: "Nigeria",
    ZA: "South Africa",
    JM: "Jamaica",
    QA: "Qatar",
    FR: "France",
    ES: "Spain",
  };
  return names[code] || code;
}

export const INCOME_RANGES: Record<string, string> = {
  low: "$15,000 – $35,000",
  medium: "$35,000 – $80,000",
  high: "$80,000+",
};

export function formatCurrency(amount: number): string {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(amount);
}

export function formatNumber(num: number): string {
  return new Intl.NumberFormat("en-US").format(num);
}

export function getInitials(name: string): string {
  return name
    .split(" ")
    .map((n) => n[0])
    .join("")
    .toUpperCase()
    .slice(0, 2);
}
