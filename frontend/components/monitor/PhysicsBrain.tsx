"use client";

import type { PreprocessedTransaction } from "@/lib/types";
import { formatNumber, getCountryFlag } from "@/lib/utils";
import { MapPin, Clock, Zap, AlertTriangle } from "lucide-react";

interface PhysicsBrainProps {
  preprocessed: PreprocessedTransaction;
}

export function PhysicsBrain({ preprocessed }: PhysicsBrainProps) {
  const speed =
    preprocessed.actual_travel_hours > 0
      ? preprocessed.distance_km / preprocessed.actual_travel_hours
      : 0;
  const isViolation = speed > 800;
  const minTravelHours =
    preprocessed.distance_km > 0
      ? (preprocessed.distance_km / 800).toFixed(1)
      : "0";

  return (
    <div className="bg-deriv-dark-card rounded-xl border border-deriv-dark-border p-5">
      <div className="flex items-center gap-2 mb-4">
        <Zap className="w-5 h-5 text-deriv-amber" />
        <h4 className="text-sm font-semibold text-white">Geo-Velocity Check</h4>
        {isViolation && (
          <span className="flex items-center gap-1 text-xs font-bold text-deriv-red ml-auto bg-deriv-red/10 px-2.5 py-1 rounded-full">
            <AlertTriangle className="w-3.5 h-3.5" />
            VIOLATION
          </span>
        )}
      </div>

      <div className="space-y-4">
        <div className="flex items-center gap-2.5">
          <MapPin className="w-4 h-4 text-deriv-grey" />
          <div className="flex-1">
            <span className="text-xs text-deriv-grey block">Route</span>
            <span className="text-sm text-white">
              {getCountryFlag(preprocessed.previous_country)}{" "}
              {preprocessed.previous_country || "–"} → {getCountryFlag(preprocessed.transaction_country)}{" "}
              {preprocessed.transaction_country}
            </span>
          </div>
          <span className="text-sm font-medium text-white">
            {formatNumber(Math.round(preprocessed.distance_km))} km
          </span>
        </div>

        <div className="flex items-center gap-2.5">
          <Clock className="w-4 h-4 text-deriv-grey" />
          <div className="flex-1">
            <span className="text-xs text-deriv-grey block">Time Between Transactions</span>
            <span className="text-sm text-white">
              {preprocessed.time_since_last_sec > 0
                ? `${formatNumber(preprocessed.time_since_last_sec)}s (${preprocessed.actual_travel_hours.toFixed(1)}h)`
                : "First transaction"}
            </span>
          </div>
        </div>

        <div className="flex items-center gap-2.5">
          <Zap className="w-4 h-4 text-deriv-grey" />
          <div className="flex-1">
            <span className="text-xs text-deriv-grey block">
              Calculated Speed
            </span>
            <span
              className="text-sm font-medium"
              style={{ color: isViolation ? "#FF444F" : "#00A79E" }}
            >
              {speed > 0 ? `${formatNumber(Math.round(speed))} km/h` : "N/A"}
            </span>
          </div>
          <span className="text-xs text-deriv-grey">
            min: {minTravelHours}h (at 800 km/h)
          </span>
        </div>

        {preprocessed.is_new_country && (
          <div className="flex items-center gap-2.5 px-3 py-2 bg-deriv-amber/10 rounded-lg border border-deriv-amber/20">
            <AlertTriangle className="w-4 h-4 text-deriv-amber" />
            <span className="text-xs text-deriv-amber font-medium">
              New country: {preprocessed.transaction_country} not in user history
            </span>
          </div>
        )}
      </div>
    </div>
  );
}
