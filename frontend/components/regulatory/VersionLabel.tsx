"use client";

interface VersionLabelProps {
  version: string;
}

export function VersionLabel({ version }: VersionLabelProps) {
  return (
    <span className="inline-flex items-center gap-1 px-3 py-1 bg-deriv-red/10 text-deriv-red text-sm font-bold rounded-full border border-deriv-red/20">
      {version}
    </span>
  );
}
