from typing import Optional, List, Literal
from pydantic import BaseModel, Field

class SoilState(BaseModel):
    organic_carbon_pct: Optional[float] = Field(None, ge=0.0, le=100.0, description="Soil Organic Carbon (SOC) percentage")
    ph: Optional[float] = Field(None, ge=0.0, le=14.0, description="Soil pH level")
    moisture_pct: Optional[float] = Field(None, ge=0.0, le=100.0, description="Volumetric soil moisture percentage")
    nitrogen_ppm: Optional[float] = Field(None, ge=0.0, description="Soil available nitrogen in ppm")
    phosphorus_ppm: Optional[float] = Field(None, ge=0.0, description="Soil available phosphorus in ppm")
    potassium_ppm: Optional[float] = Field(None, ge=0.0, description="Soil available potassium in ppm")
    texture: Optional[str] = Field(None, description="Soil texture class, e.g. sandy loam, clay loam, clay")

class LandState(BaseModel):
    region: Optional[str] = Field(None, description="Geographic/agro-climatic region (e.g. semi-arid Karnataka)")
    land_use: Optional[str] = Field(None, description="Land use type, e.g. monoculture, polyculture, agroforestry")
    land_cover: Optional[str] = Field(None, description="Land cover type (e.g. cropland, shrubland)")
    crop: Optional[str] = Field(None, description="Primary crop cultivated (e.g. wheat, cotton, rice)")
    is_monoculture: Optional[bool] = Field(None, description="Whether land is cultivated under monoculture")
    tree_cover_pct: Optional[float] = Field(None, ge=0.0, le=100.0, description="Tree canopy cover percentage")
    habitat_fragmentation: Optional[str] = Field(None, description="Degree of habitat fragmentation")

class BiodiversityState(BaseModel):
    species_richness: Optional[str] = Field(None, description="Species richness level or count")
    habitat_diversity: Optional[str] = Field(None, description="Structural habitat diversity")
    pollinator_presence: Optional[str] = Field(None, description="Observed pollinator abundance")
    native_species_ratio: Optional[float] = Field(None, ge=0.0, le=1.0, description="Proportion of native species present")
    biodiversity_indicators: List[str] = Field(default_factory=list, description="Key indicator taxa observed")

class ClimateState(BaseModel):
    rainfall: Optional[str] = Field(None, description="Rainfall classification")
    rainfall_variability: Optional[str] = Field(None, description="Rainfall variability/erraticness")
    annual_rainfall_mm: Optional[float] = Field(None, ge=0.0, description="Annual precipitation in mm")
    temperature_celsius: Optional[float] = Field(None, description="Mean temperature in Celsius")
    drought_frequency: Optional[str] = Field(None, description="Drought occurrence frequency")
    water_availability: Optional[str] = Field(None, description="Surface and groundwater access")

class HumanImpactState(BaseModel):
    pesticide_use: Optional[str] = Field(None, description="Chemical pesticide application intensity")
    pollution_level: Optional[str] = Field(None, description="Soil and runoff chemical pollution")
    water_extraction: Optional[str] = Field(None, description="Groundwater extraction status")
    deforestation_proximity: Optional[str] = Field(None, description="Proximity to recent land clearing")
    urbanization_pressure: Optional[str] = Field(None, description="Urban encroachment level")

class EnvironmentalState(BaseModel):
    soil: SoilState = Field(default_factory=SoilState)
    land: LandState = Field(default_factory=LandState)
    biodiversity: BiodiversityState = Field(default_factory=BiodiversityState)
    climate: ClimateState = Field(default_factory=ClimateState)
    human_impact: HumanImpactState = Field(default_factory=HumanImpactState)

    def is_empty(self) -> bool:
        """Returns True if no environmental variables have been specified."""
        return self.count_specified_variables() == 0

    def count_specified_variables(self) -> int:
        """Counts how many environmental variables across all 5 classes are provided."""
        count = 0
        for sub_state in [self.soil, self.land, self.biodiversity, self.climate, self.human_impact]:
            for k, v in sub_state.model_dump(exclude_none=True).items():
                if v != [] and v != {} and v != "" and v is not None:
                    count += 1
        return count

    def merge_with(self, other: "EnvironmentalState") -> "EnvironmentalState":
        """Merges another EnvironmentalState into this one, overwriting with non-null values."""
        def merge_sub(base_obj, update_obj, cls):
            d = base_obj.model_dump()
            for k, v in update_obj.model_dump().items():
                if v is not None and v != [] and v != {}:
                    d[k] = v
            return cls(**d)

        return EnvironmentalState(
            soil=merge_sub(self.soil, other.soil, SoilState),
            land=merge_sub(self.land, other.land, LandState),
            biodiversity=merge_sub(self.biodiversity, other.biodiversity, BiodiversityState),
            climate=merge_sub(self.climate, other.climate, ClimateState),
            human_impact=merge_sub(self.human_impact, other.human_impact, HumanImpactState),
        )
