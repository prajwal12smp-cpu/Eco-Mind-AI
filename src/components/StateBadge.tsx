import React from 'react';
import {
  Sprout,
  MapPin,
  CloudRain,
  Bug,
  AlertTriangle,
  CheckCircle,
  HelpCircle,
} from 'lucide-react';
import { EnvironmentalState } from '../types';

interface StateBadgeProps {
  state: EnvironmentalState;
  isComplete?: boolean;
}

export const StateBadge: React.FC<StateBadgeProps> = ({ state, isComplete }) => {
  const hasSoil = state.soil && (state.soil.organic_carbon_pct != null || state.soil.ph != null);
  const hasLand = state.land && (state.land.region != null || state.land.crop != null);
  const hasClimate = state.climate && (state.climate.rainfall != null || state.climate.annual_rainfall_mm != null);
  const hasBiodiversity = state.biodiversity && (state.biodiversity.pollinator_presence != null || state.biodiversity.habitat_diversity != null);
  const hasHumanImpact = state.human_impact && (state.human_impact.pesticide_use != null || state.human_impact.water_extraction != null);

  return (
    <div className="bg-slate-900/90 rounded-xl border border-slate-800 p-4">
      <div className="flex items-center justify-between mb-3 border-b border-slate-800/80 pb-2">
        <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-400">
          Environmental State Extraction
        </h4>
        {isComplete !== undefined && (
          <span
            className={`text-[11px] px-2 py-0.5 rounded-full font-medium flex items-center gap-1 ${
              isComplete
                ? 'bg-emerald-950 text-emerald-300 border border-emerald-800'
                : 'bg-amber-950 text-amber-300 border border-amber-800'
            }`}
          >
            {isComplete ? (
              <>
                <CheckCircle className="w-3 h-3 text-emerald-400" />
                Sufficient for Reasoning
              </>
            ) : (
              <>
                <HelpCircle className="w-3 h-3 text-amber-400" />
                Sparse Indicators
              </>
            )}
          </span>
        )}
      </div>

      <div className="space-y-2.5 text-xs">
        {/* Soil Metrics */}
        <div className="p-2.5 rounded-lg bg-slate-950/70 border border-slate-800/80">
          <div className="flex items-center gap-1.5 font-semibold text-amber-400 mb-1">
            <Sprout className="w-3.5 h-3.5" />
            <span>Soil Matrix</span>
          </div>
          {hasSoil ? (
            <div className="grid grid-cols-2 gap-1 text-slate-300">
              {state.soil.organic_carbon_pct != null && (
                <div>
                  <span className="text-slate-500">SOC: </span>
                  <span className="font-semibold text-amber-300">
                    {state.soil.organic_carbon_pct}%
                  </span>
                </div>
              )}
              {state.soil.ph != null && (
                <div>
                  <span className="text-slate-500">pH: </span>
                  <span className="font-semibold text-slate-200">{state.soil.ph}</span>
                </div>
              )}
              {state.soil.moisture_pct != null && (
                <div>
                  <span className="text-slate-500">Moisture: </span>
                  <span className="font-semibold text-slate-200">
                    {state.soil.moisture_pct}%
                  </span>
                </div>
              )}
              {state.soil.texture && (
                <div>
                  <span className="text-slate-500">Texture: </span>
                  <span className="font-semibold text-slate-200">{state.soil.texture}</span>
                </div>
              )}
            </div>
          ) : (
            <span className="text-slate-500 italic">No soil data detected yet</span>
          )}
        </div>

        {/* Land Matrix */}
        <div className="p-2.5 rounded-lg bg-slate-950/70 border border-slate-800/80">
          <div className="flex items-center gap-1.5 font-semibold text-emerald-400 mb-1">
            <MapPin className="w-3.5 h-3.5" />
            <span>Land & Crop System</span>
          </div>
          {hasLand ? (
            <div className="grid grid-cols-2 gap-1 text-slate-300">
              {state.land.region && (
                <div className="col-span-2">
                  <span className="text-slate-500">Region: </span>
                  <span className="font-medium text-emerald-300">{state.land.region}</span>
                </div>
              )}
              {state.land.crop && (
                <div>
                  <span className="text-slate-500">Crop: </span>
                  <span className="font-medium text-slate-200">{state.land.crop}</span>
                </div>
              )}
              {state.land.is_monoculture != null && (
                <div>
                  <span className="text-slate-500">System: </span>
                  <span
                    className={`font-semibold ${
                      state.land.is_monoculture ? 'text-rose-400' : 'text-emerald-400'
                    }`}
                  >
                    {state.land.is_monoculture ? 'Monoculture' : 'Polyculture'}
                  </span>
                </div>
              )}
            </div>
          ) : (
            <span className="text-slate-500 italic">No land parameters specified</span>
          )}
        </div>

        {/* Climate Matrix */}
        <div className="p-2.5 rounded-lg bg-slate-950/70 border border-slate-800/80">
          <div className="flex items-center gap-1.5 font-semibold text-sky-400 mb-1">
            <CloudRain className="w-3.5 h-3.5" />
            <span>Climate & Hydrology</span>
          </div>
          {hasClimate ? (
            <div className="grid grid-cols-2 gap-1 text-slate-300">
              {state.climate.rainfall && (
                <div>
                  <span className="text-slate-500">Rainfall: </span>
                  <span className="font-medium text-sky-300">{state.climate.rainfall}</span>
                </div>
              )}
              {state.climate.annual_rainfall_mm != null && (
                <div>
                  <span className="text-slate-500">Annual: </span>
                  <span className="font-medium text-sky-300">
                    {state.climate.annual_rainfall_mm} mm
                  </span>
                </div>
              )}
              {state.climate.temperature_celsius != null && (
                <div>
                  <span className="text-slate-500">Temp: </span>
                  <span className="font-medium text-slate-200">
                    {state.climate.temperature_celsius}°C
                  </span>
                </div>
              )}
            </div>
          ) : (
            <span className="text-slate-500 italic">No rainfall or climate data</span>
          )}
        </div>

        {/* Biodiversity & Human Pressures */}
        <div className="p-2.5 rounded-lg bg-slate-950/70 border border-slate-800/80">
          <div className="flex items-center gap-1.5 font-semibold text-teal-400 mb-1">
            <Bug className="w-3.5 h-3.5" />
            <span>Ecological & Human Pressures</span>
          </div>
          {hasBiodiversity || hasHumanImpact ? (
            <div className="space-y-1 text-slate-300">
              {state.biodiversity.pollinator_presence && (
                <div>
                  <span className="text-slate-500">Pollinators: </span>
                  <span className="font-medium text-slate-200">
                    {state.biodiversity.pollinator_presence}
                  </span>
                </div>
              )}
              {state.human_impact.pesticide_use && (
                <div>
                  <span className="text-slate-500">Pesticide: </span>
                  <span className="font-medium text-amber-300">
                    {state.human_impact.pesticide_use}
                  </span>
                </div>
              )}
            </div>
          ) : (
            <span className="text-slate-500 italic">Pressures not registered</span>
          )}
        </div>
      </div>
    </div>
  );
};
