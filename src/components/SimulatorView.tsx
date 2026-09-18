import React, { useState } from 'react';
import {
  Sliders,
  Play,
  RotateCcw,
  Sparkles,
  Sprout,
  CloudRain,
  MapPin,
  Bug,
  ShieldAlert,
  Layers,
} from 'lucide-react';
import { EnvironmentalState, RecommendationOutput } from '../types';
import { analyzeState } from '../api';
import { RecommendationCard } from './RecommendationCard';

export const SimulatorView: React.FC = () => {
  // Configurable Parameters State
  const [soc, setSoc] = useState<number>(0.3);
  const [ph, setPh] = useState<number>(7.9);
  const [moisture, setMoisture] = useState<number>(14);
  const [texture, setTexture] = useState<string>('Sandy loam');

  const [region, setRegion] = useState<string>('semi-arid Karnataka');
  const [crop, setCrop] = useState<string>('Wheat');
  const [isMonoculture, setIsMonoculture] = useState<boolean>(true);

  const [annualRainfall, setAnnualRainfall] = useState<number>(450);
  const [rainfallCategory, setRainfallCategory] = useState<string>('low');
  const [temperature, setTemperature] = useState<number>(34);

  const [pollinators, setPollinators] = useState<string>('low');
  const [pesticideUse, setPesticideUse] = useState<string>('high');

  const [recommendations, setRecommendations] = useState<RecommendationOutput[]>([]);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [hasRun, setHasRun] = useState(false);

  const handleRunSimulation = async () => {
    setIsAnalyzing(true);
    try {
      const state: EnvironmentalState = {
        soil: {
          organic_carbon_pct: soc,
          ph: ph,
          moisture_pct: moisture,
          texture: texture,
        },
        land: {
          region: region,
          crop: crop,
          is_monoculture: isMonoculture,
        },
        climate: {
          annual_rainfall_mm: annualRainfall,
          rainfall: rainfallCategory,
          temperature_celsius: temperature,
        },
        biodiversity: {
          pollinator_presence: pollinators,
          biodiversity_indicators: [],
        },
        human_impact: {
          pesticide_use: pesticideUse,
        },
      };

      const recs = await analyzeState(state);
      setRecommendations(recs);
      setHasRun(true);
    } catch (err: any) {
      alert(err.message || 'Simulation execution failed');
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleResetToBenchmark = () => {
    setSoc(0.3);
    setPh(7.9);
    setMoisture(14);
    setTexture('Sandy loam');
    setRegion('semi-arid Karnataka');
    setCrop('Wheat');
    setIsMonoculture(true);
    setAnnualRainfall(450);
    setRainfallCategory('low');
    setTemperature(34);
    setPollinators('low');
    setPesticideUse('high');
    setRecommendations([]);
    setHasRun(false);
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6">
      {/* Header Banner */}
      <div className="flex flex-wrap items-center justify-between gap-4 bg-slate-900/90 p-4 rounded-2xl border border-slate-800">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-teal-500/15 border border-teal-500/30 flex items-center justify-center text-teal-400">
            <Sliders className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-sm font-semibold text-white">Multi-Metric Scenario Simulator</h2>
            <p className="text-xs text-slate-400">
              Perturb soil metrics, rainfall, and cropping systems to stress-test deterministic reasoning
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={handleResetToBenchmark}
            className="flex items-center gap-1.5 text-xs px-3 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl border border-slate-700 transition-colors"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span>Reset to Benchmark</span>
          </button>

          <button
            id="btn-run-simulation"
            onClick={handleRunSimulation}
            disabled={isAnalyzing}
            className="flex items-center gap-2 text-xs font-semibold px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl shadow-md shadow-emerald-950/40 transition-all disabled:opacity-50"
          >
            {isAnalyzing ? (
              <Sparkles className="w-4 h-4 animate-spin" />
            ) : (
              <Play className="w-4 h-4 fill-white" />
            )}
            <span>Execute Reasoning</span>
          </button>
        </div>
      </div>

      {/* Methodological Notice */}
      <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-3 text-xs text-slate-300 leading-relaxed flex items-start gap-2.5">
        <ShieldAlert className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
        <div>
          <span className="font-semibold text-amber-300">Methodology Notice: </span>
          Scenario outputs evaluate multi-variable rule activations and RAG evidence grounding. Projected metrics and response intervals are <strong className="text-white">literature-informed heuristic projections</strong> derived from published field agronomy literature (FAO, ICRISAT, ICRAF). They are not physical sensor measurements or site-specific biogeochemical model forecasts.
        </div>
      </div>

      {/* Simulator Inputs Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Soil Matrix Controls */}
        <div className="bg-slate-900/90 rounded-2xl border border-slate-800 p-4 space-y-3.5">
          <div className="text-xs font-semibold text-amber-400 flex items-center gap-1.5 border-b border-slate-800 pb-2">
            <Sprout className="w-4 h-4" />
            <span>Soil Matrix</span>
          </div>

          <div>
            <div className="flex justify-between text-xs text-slate-400 mb-1">
              <span>Soil Organic Carbon</span>
              <span className="font-bold text-amber-300">{soc}%</span>
            </div>
            <input
              type="range"
              min="0.1"
              max="2.5"
              step="0.05"
              value={soc}
              onChange={(e) => setSoc(parseFloat(e.target.value))}
              className="w-full accent-amber-400"
            />
            <div className="flex justify-between text-[10px] text-slate-500 mt-0.5">
              <span>0.1% (Degraded)</span>
              <span>0.5% (Threshold)</span>
              <span>2.5% (Optimal)</span>
            </div>
          </div>

          <div>
            <div className="flex justify-between text-xs text-slate-400 mb-1">
              <span>Soil pH</span>
              <span className="font-bold text-slate-200">{ph}</span>
            </div>
            <input
              type="range"
              min="5.0"
              max="9.5"
              step="0.1"
              value={ph}
              onChange={(e) => setPh(parseFloat(e.target.value))}
              className="w-full accent-slate-400"
            />
          </div>

          <div>
            <div className="flex justify-between text-xs text-slate-400 mb-1">
              <span>Soil Moisture (%)</span>
              <span className="font-bold text-slate-200">{moisture}%</span>
            </div>
            <input
              type="range"
              min="5"
              max="40"
              step="1"
              value={moisture}
              onChange={(e) => setMoisture(parseInt(e.target.value))}
              className="w-full accent-teal-400"
            />
          </div>

          <div>
            <label className="text-xs text-slate-400 block mb-1">Texture</label>
            <select
              value={texture}
              onChange={(e) => setTexture(e.target.value)}
              className="w-full bg-slate-950 text-white text-xs p-2 rounded-lg border border-slate-800"
            >
              <option value="Sandy loam">Sandy loam</option>
              <option value="Clay loam">Clay loam</option>
              <option value="Black cotton soil">Black cotton soil (Vertisol)</option>
              <option value="Red sandy soil">Red sandy soil (Alfisol)</option>
            </select>
          </div>
        </div>

        {/* Climate & Water Hydrology */}
        <div className="bg-slate-900/90 rounded-2xl border border-slate-800 p-4 space-y-3.5">
          <div className="text-xs font-semibold text-sky-400 flex items-center gap-1.5 border-b border-slate-800 pb-2">
            <CloudRain className="w-4 h-4" />
            <span>Climate & Hydrology</span>
          </div>

          <div>
            <div className="flex justify-between text-xs text-slate-400 mb-1">
              <span>Annual Rainfall</span>
              <span className="font-bold text-sky-300">{annualRainfall} mm</span>
            </div>
            <input
              type="range"
              min="200"
              max="1500"
              step="25"
              value={annualRainfall}
              onChange={(e) => setAnnualRainfall(parseInt(e.target.value))}
              className="w-full accent-sky-400"
            />
            <div className="flex justify-between text-[10px] text-slate-500 mt-0.5">
              <span>200mm (Arid)</span>
              <span>550mm (Semi-arid)</span>
              <span>1500mm</span>
            </div>
          </div>

          <div>
            <label className="text-xs text-slate-400 block mb-1">Rainfall Pattern</label>
            <select
              value={rainfallCategory}
              onChange={(e) => setRainfallCategory(e.target.value)}
              className="w-full bg-slate-950 text-white text-xs p-2 rounded-lg border border-slate-800"
            >
              <option value="low">Low / Erratic (Semi-arid)</option>
              <option value="moderate">Moderate Seasonality</option>
              <option value="high">Abundant / Humid</option>
            </select>
          </div>

          <div>
            <div className="flex justify-between text-xs text-slate-400 mb-1">
              <span>Avg Summer Temp</span>
              <span className="font-bold text-slate-200">{temperature}°C</span>
            </div>
            <input
              type="range"
              min="15"
              max="45"
              step="1"
              value={temperature}
              onChange={(e) => setTemperature(parseInt(e.target.value))}
              className="w-full accent-rose-400"
            />
          </div>
        </div>

        {/* Cropping & Land System */}
        <div className="bg-slate-900/90 rounded-2xl border border-slate-800 p-4 space-y-3.5">
          <div className="text-xs font-semibold text-emerald-400 flex items-center gap-1.5 border-b border-slate-800 pb-2">
            <MapPin className="w-4 h-4" />
            <span>Land & Crop System</span>
          </div>

          <div>
            <label className="text-xs text-slate-400 block mb-1">Agro-Ecological Region</label>
            <input
              type="text"
              value={region}
              onChange={(e) => setRegion(e.target.value)}
              className="w-full bg-slate-950 text-white text-xs p-2 rounded-lg border border-slate-800"
            />
          </div>

          <div>
            <label className="text-xs text-slate-400 block mb-1">Primary Crop</label>
            <input
              type="text"
              value={crop}
              onChange={(e) => setCrop(e.target.value)}
              className="w-full bg-slate-950 text-white text-xs p-2 rounded-lg border border-slate-800"
            />
          </div>

          <div className="pt-2">
            <label className="text-xs text-slate-400 block mb-1.5">Cropping Diversity</label>
            <div className="grid grid-cols-2 gap-2">
              <button
                type="button"
                onClick={() => setIsMonoculture(true)}
                className={`py-1.5 text-xs font-medium rounded-lg border transition-all ${
                  isMonoculture
                    ? 'bg-rose-950/80 text-rose-300 border-rose-700'
                    : 'bg-slate-950 text-slate-400 border-slate-800'
                }`}
              >
                Monoculture
              </button>
              <button
                type="button"
                onClick={() => setIsMonoculture(false)}
                className={`py-1.5 text-xs font-medium rounded-lg border transition-all ${
                  !isMonoculture
                    ? 'bg-emerald-950/80 text-emerald-300 border-emerald-700'
                    : 'bg-slate-950 text-slate-400 border-slate-800'
                }`}
              >
                Polyculture / Mixed
              </button>
            </div>
          </div>
        </div>

        {/* Biodiversity & Chemical Pressures */}
        <div className="bg-slate-900/90 rounded-2xl border border-slate-800 p-4 space-y-3.5">
          <div className="text-xs font-semibold text-teal-400 flex items-center gap-1.5 border-b border-slate-800 pb-2">
            <Bug className="w-4 h-4" />
            <span>Ecosystem Pressures</span>
          </div>

          <div>
            <label className="text-xs text-slate-400 block mb-1">Pollinator Presence</label>
            <select
              value={pollinators}
              onChange={(e) => setPollinators(e.target.value)}
              className="w-full bg-slate-950 text-white text-xs p-2 rounded-lg border border-slate-800"
            >
              <option value="low">Low / Collapsing</option>
              <option value="moderate">Moderate</option>
              <option value="high">Healthy / Diverse</option>
            </select>
          </div>

          <div>
            <label className="text-xs text-slate-400 block mb-1">Chemical Pesticide Pressure</label>
            <select
              value={pesticideUse}
              onChange={(e) => setPesticideUse(e.target.value)}
              className="w-full bg-slate-950 text-white text-xs p-2 rounded-lg border border-slate-800"
            >
              <option value="high">High (Synthetic Organophosphates)</option>
              <option value="moderate">Moderate</option>
              <option value="low">Low / Targeted IPM</option>
              <option value="none">None / Bio-pesticides</option>
            </select>
          </div>

          <div className="p-2.5 rounded-lg bg-slate-950 border border-slate-800/80 text-[11px] text-slate-400 leading-relaxed">
            <span className="font-semibold text-teal-300">Coupled Feedback: </span>
            Combining High Chemical Use with Low Pollinators triggers Agroforestry & Bio-buffer interventions.
          </div>
        </div>
      </div>

      {/* Simulation Results Section */}
      {hasRun && (
        <div className="space-y-4 pt-4 border-t border-slate-800">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold uppercase tracking-wider text-emerald-400 flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-emerald-400" />
              Simulated Deterministic Interventions ({recommendations.length})
            </h3>
            <span className="text-xs text-slate-400">
              Cross-checked with FAO & CGIAR empirical research
            </span>
          </div>

          {recommendations.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {recommendations.map((rec) => (
                <RecommendationCard key={rec.id} recommendation={rec} />
              ))}
            </div>
          ) : (
            <div className="text-center py-8 text-slate-400 bg-slate-900/60 rounded-xl border border-slate-800 text-xs">
              No acute stressors triggered for this benign parameter set. Try lowering SOC &lt; 0.5% or setting monoculture in semi-arid conditions.
            </div>
          )}
        </div>
      )}
    </div>
  );
};
