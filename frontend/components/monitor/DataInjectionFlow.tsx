"use client";

import { useState, useRef, useEffect, useMemo } from "react";
import type { UserWithState, IngestBatchRequest } from "@/lib/types";
import { LoadingSpinner } from "@/components/shared/LoadingSpinner";
import { getCountryName } from "@/lib/utils";
import {
  ChevronUp,
  ChevronDown,
  Syringe,
  Zap,
  X,
} from "lucide-react";

interface DataInjectionFlowProps {
  user: UserWithState;
  allUsers: UserWithState[];
  loading: boolean;
  onInject: (request: IngestBatchRequest) => Promise<void>;
}

const CURRENCIES = [
  { code: "", label: "Random" },
  { code: "USDT", label: "USDT" },
  { code: "BTC", label: "BTC" },
  { code: "ETH", label: "ETH" },
  { code: "SOL", label: "SOL" },
  { code: "XMR", label: "XMR" },
];

export function DataInjectionFlow({
  user,
  allUsers,
  loading,
  onInject,
}: DataInjectionFlowProps) {
  const [open, setOpen] = useState(false);
  const [numTx, setNumTx] = useState(5);
  const [minAmount, setMinAmount] = useState("");
  const [maxAmount, setMaxAmount] = useState("");
  const [variance, setVariance] = useState("");
  const [selectedCountries, setSelectedCountries] = useState<string[]>([]);
  const [countryDropdownOpen, setCountryDropdownOpen] = useState(false);
  const [currencyOverride, setCurrencyOverride] = useState("");
  const countryDropdownRef = useRef<HTMLDivElement>(null);

  // Build country list from ALL users' historical_countries (deduplicated)
  const availableCountries = useMemo(() => {
    const codes = new Set<string>();
    allUsers.forEach((u) => {
      u.profile.historical_countries.forEach((c) => codes.add(c));
    });
    return Array.from(codes)
      .sort((a, b) => getCountryName(a).localeCompare(getCountryName(b)))
      .map((code) => ({ code, label: getCountryName(code) }));
  }, [allUsers]);

  // Close dropdown on outside click
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (countryDropdownRef.current && !countryDropdownRef.current.contains(event.target as Node)) {
        setCountryDropdownOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const toggleCountry = (code: string) => {
    setSelectedCountries((prev) =>
      prev.includes(code)
        ? prev.filter((c) => c !== code)
        : [...prev, code]
    );
  };

  const removeCountry = (code: string) => {
    setSelectedCountries((prev) => prev.filter((c) => c !== code));
  };

  const handleSubmit = async () => {
    const request: IngestBatchRequest = {
      user_id: user.profile.user_id,
      num_transactions: numTx,
    };

    if (minAmount) request.min_amount = Number.parseFloat(minAmount);
    if (maxAmount) request.max_amount = Number.parseFloat(maxAmount);
    if (variance) request.variance = Number.parseFloat(variance);
    if (selectedCountries.length > 0) request.countries = selectedCountries;

    const overrides: NonNullable<IngestBatchRequest["overrides"]> = {};
    if (currencyOverride) overrides.transaction_currency = currencyOverride;
    if (Object.keys(overrides).length > 0) request.overrides = overrides;

    await onInject(request);
  };

  const hint = `Historical range: $${user.baseline.min_tx_amount_usd?.toFixed(0) ?? "?"} – $${user.baseline.max_tx_amount_usd?.toFixed(0) ?? "?"}`;

  return (
    <div className="bg-deriv-dark-card rounded-xl border border-deriv-dark-border">
      {/* Toggle header */}
      <button
        onClick={() => setOpen(!open)}
        className="w-full flex items-center justify-between gap-2 px-5 py-3.5 text-left hover:bg-white/5 rounded-xl transition-colors"
      >
        <div className="flex items-center gap-2">
          <Syringe className="w-5 h-5 text-deriv-red" />
          <span className="text-sm font-semibold text-white">Data Injection</span>
          <span className="text-xs text-deriv-grey">{hint}</span>
        </div>
        {open ? (
          <ChevronDown className="w-4 h-4 text-deriv-grey" />
        ) : (
          <ChevronUp className="w-4 h-4 text-deriv-grey" />
        )}
      </button>

      {/* Collapsible body */}
      {open && (
        <div className="px-5 pb-5 space-y-4">
          {/* Row 1: Transactions + Amount controls */}
          <div className="grid grid-cols-2 lg:grid-cols-5 gap-3">
            <div>
              <label className="text-xs text-deriv-grey block mb-1.5 uppercase tracking-wider">
                # Transactions
              </label>
              <input
                type="number"
                min={1}
                value={numTx}
                onChange={(e) => setNumTx(Number.parseInt(e.target.value) || 5)}
                className="w-full bg-deriv-black border border-deriv-dark-border rounded-lg px-3 py-2 text-sm text-white outline-none focus:border-deriv-red"
              />
            </div>
            <div>
              <label className="text-xs text-deriv-grey block mb-1.5 uppercase tracking-wider">
                Min Amount ($)
              </label>
              <input
                type="number"
                placeholder="e.g. 100"
                value={minAmount}
                onChange={(e) => setMinAmount(e.target.value)}
                className="w-full bg-deriv-black border border-deriv-dark-border rounded-lg px-3 py-2 text-sm text-white outline-none focus:border-deriv-red placeholder-deriv-grey/50"
              />
            </div>
            <div>
              <label className="text-xs text-deriv-grey block mb-1.5 uppercase tracking-wider">
                Max Amount ($)
              </label>
              <input
                type="number"
                placeholder="e.g. 55000"
                value={maxAmount}
                onChange={(e) => setMaxAmount(e.target.value)}
                className="w-full bg-deriv-black border border-deriv-dark-border rounded-lg px-3 py-2 text-sm text-white outline-none focus:border-deriv-red placeholder-deriv-grey/50"
              />
            </div>
            <div>
              <label className="text-xs text-deriv-grey block mb-1.5 uppercase tracking-wider">
                Variance (σ)
              </label>
              <input
                type="number"
                placeholder="e.g. 5000"
                value={variance}
                onChange={(e) => setVariance(e.target.value)}
                className="w-full bg-deriv-black border border-deriv-dark-border rounded-lg px-3 py-2 text-sm text-white outline-none focus:border-deriv-red placeholder-deriv-grey/50"
              />
            </div>
            <div>
              <label className="text-xs text-deriv-grey block mb-1.5 uppercase tracking-wider">
                Currency
              </label>
              <select
                value={currencyOverride}
                onChange={(e) => setCurrencyOverride(e.target.value)}
                className="w-full bg-deriv-black border border-deriv-dark-border rounded-lg px-3 py-2 text-sm text-white outline-none focus:border-deriv-red"
              >
                {CURRENCIES.map((c) => (
                  <option key={c.code} value={c.code}>
                    {c.label}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Row 2: Country multi-select */}
          <div ref={countryDropdownRef}>
            <label className="text-xs text-deriv-grey block mb-1.5 uppercase tracking-wider">
              Countries (leave empty for user defaults)
            </label>
            <div className="relative">
              <button
                type="button"
                onClick={() => setCountryDropdownOpen(!countryDropdownOpen)}
                className="w-full bg-deriv-black border border-deriv-dark-border rounded-lg px-3 py-2 text-sm text-white outline-none focus:border-deriv-red text-left flex items-center justify-between min-h-[38px]"
              >
                <span className="flex flex-wrap gap-1.5 flex-1">
                  {selectedCountries.length === 0 ? (
                    <span className="text-deriv-grey/50">From user history...</span>
                  ) : (
                    selectedCountries.map((code) => (
                      <span
                        key={code}
                        className="inline-flex items-center gap-1 bg-deriv-red/20 text-deriv-red border border-deriv-red/30 rounded px-2 py-0.5 text-xs font-medium"
                      >
                        {getCountryName(code)}
                        <X
                          className="w-3.5 h-3.5 cursor-pointer hover:text-white"
                          onClick={(e) => {
                            e.stopPropagation();
                            removeCountry(code);
                          }}
                        />
                      </span>
                    ))
                  )}
                </span>
                <ChevronDown className="w-4 h-4 text-deriv-grey ml-2 flex-shrink-0" />
              </button>

              {countryDropdownOpen && (
                <div className="absolute bottom-full mb-1 left-0 right-0 bg-deriv-black border border-deriv-dark-border rounded-lg shadow-xl max-h-52 overflow-y-auto z-50">
                  {availableCountries.map((c) => {
                    const isSelected = selectedCountries.includes(c.code);
                    return (
                      <button
                        key={c.code}
                        type="button"
                        onClick={() => toggleCountry(c.code)}
                        className={`w-full text-left px-3 py-2 text-sm hover:bg-deriv-dark-border/50 flex items-center gap-2.5 transition-colors ${
                          isSelected ? "text-deriv-red bg-deriv-red/5" : "text-white"
                        }`}
                      >
                        <span
                          className={`w-4 h-4 rounded border flex items-center justify-center flex-shrink-0 ${
                            isSelected
                              ? "bg-deriv-red border-deriv-red"
                              : "border-deriv-dark-border"
                          }`}
                        >
                          {isSelected && (
                            <svg className="w-3 h-3 text-white" viewBox="0 0 12 12" fill="none">
                              <path d="M2 6l3 3 5-5" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                            </svg>
                          )}
                        </span>
                        <span className="font-medium">{c.code}</span>
                        <span className="text-deriv-grey">{c.label}</span>
                      </button>
                    );
                  })}
                </div>
              )}
            </div>
          </div>

          {/* Inject button */}
          <button
            onClick={handleSubmit}
            disabled={loading}
            className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-deriv-red text-white font-bold text-sm rounded-lg hover:bg-deriv-red/90 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {loading ? (
              <>
                <LoadingSpinner text="" size="sm" />
                <span>Agents Working...</span>
              </>
            ) : (
              <>
                <Zap className="w-4 h-4" />
                <span>Inject Batch</span>
              </>
            )}
          </button>
        </div>
      )}
    </div>
  );
}
