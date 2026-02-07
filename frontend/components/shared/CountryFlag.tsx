"use client";

import { getCountryFlag } from "@/lib/utils";

interface CountryFlagProps {
  code: string;
  size?: "sm" | "md" | "lg";
}

export function CountryFlag({ code, size = "md" }: CountryFlagProps) {
  const sizeClass = {
    sm: "text-sm",
    md: "text-lg",
    lg: "text-2xl",
  };

  return <span className={sizeClass[size]}>{getCountryFlag(code)}</span>;
}
