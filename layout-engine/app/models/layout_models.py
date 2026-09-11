from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field, model_validator


class CodeType(str, Enum):
    HUMAN_READABLE = "human-readable"
    DATAMATRIX = "datamatrix"
    BARCODE = "barcode"


class MarkingSide(str, Enum):
    FRONT = "front"
    BACK = "back"
    BOTH = "both"


class MarkingMethod(str, Enum):
    EMBOSS = "emboss"
    DEBOSS = "deboss"
    INKJET = "inkjet"
    LASER = "laser"
    OTHER = "other"


class ElementType(str, Enum):
    TEXT = "text"
    CODE = "code"
    RECTANGLE = "rectangle"
    TABLET_CAVITY = "tablet_cavity"


class PackageModel(BaseModel):
    package_width_mm: float = Field(gt=0, description="Package physical width in millimeters")
    package_height_mm: float = Field(gt=0, description="Package physical height in millimeters")
    printing_area_width_mm: float = Field(gt=0, description="Printing area width in millimeters")
    printing_area_height_mm: float = Field(gt=0, description="Printing area height in millimeters")
    margin_left_mm: float = Field(default=0.0, ge=0, description="Left margin in millimeters")
    margin_right_mm: float = Field(default=0.0, ge=0, description="Right margin in millimeters")
    margin_top_mm: float = Field(default=0.0, ge=0, description="Top margin in millimeters")
    margin_bottom_mm: float = Field(default=0.0, ge=0, description="Bottom margin in millimeters")
    printing_area_x_mm: float = Field(default=0.0, ge=0, description="Printing area X offset in millimeters")
    printing_area_y_mm: float = Field(default=0.0, ge=0, description="Printing area Y offset in millimeters")

    @model_validator(mode="after")
    def validate_bounds(self) -> "PackageModel":
        if self.printing_area_width_mm > self.package_width_mm:
            raise ValueError(
                f"Printing area width ({self.printing_area_width_mm}mm) cannot exceed package width ({self.package_width_mm}mm)"
            )
        if self.printing_area_height_mm > self.package_height_mm:
            raise ValueError(
                f"Printing area height ({self.printing_area_height_mm}mm) cannot exceed package height ({self.package_height_mm}mm)"
            )

        # Set default offsets from margins if offsets were not provided
        if self.printing_area_x_mm == 0.0 and self.margin_left_mm > 0.0:
            object.__setattr__(self, "printing_area_x_mm", self.margin_left_mm)
        if self.printing_area_y_mm == 0.0 and self.margin_top_mm > 0.0:
            object.__setattr__(self, "printing_area_y_mm", self.margin_top_mm)

        # Validate total margin + printing area consistency
        if self.margin_left_mm + self.margin_right_mm + self.printing_area_width_mm > self.package_width_mm:
            raise ValueError("Sum of left margin, right margin, and printing area width exceeds package width")
        if self.margin_top_mm + self.margin_bottom_mm + self.printing_area_height_mm > self.package_height_mm:
            raise ValueError("Sum of top margin, bottom margin, and printing area height exceeds package height")

        if self.printing_area_x_mm + self.printing_area_width_mm > self.package_width_mm:
            raise ValueError("Printing area width + X offset exceeds package width")
        if self.printing_area_y_mm + self.printing_area_height_mm > self.package_height_mm:
            raise ValueError("Printing area height + Y offset exceeds package height")

        return self


class TabletCavityPosition(BaseModel):
    x_mm: float = Field(ge=0, description="X coordinate of cavity center or top-left in mm")
    y_mm: float = Field(ge=0, description="Y coordinate of cavity center or top-left in mm")
    width_mm: Optional[float] = Field(default=None, gt=0, description="Optional cavity width in mm")
    height_mm: Optional[float] = Field(default=None, gt=0, description="Optional cavity height in mm")
    id: Optional[str] = None


# Alias for backwards compatibility
TabletPosition = TabletCavityPosition


class TabletConfig(BaseModel):
    tablet_count: int = Field(ge=1, description="Total count of tablets in packaging")
    tablet_width_mm: Optional[float] = Field(default=None, gt=0, description="Tablet width in mm")
    tablet_height_mm: Optional[float] = Field(default=None, gt=0, description="Tablet height in mm")
    tablet_diameter_mm: Optional[float] = Field(default=None, gt=0, description="Tablet diameter for round tablets in mm")
    positions: Optional[List[TabletCavityPosition]] = Field(default=None, description="Pre-defined cavity positions")

    @model_validator(mode="after")
    def validate_tablet_shape(self) -> "TabletConfig":
        has_diameter = self.tablet_diameter_mm is not None
        has_rect = self.tablet_width_mm is not None and self.tablet_height_mm is not None

        if not has_diameter and not has_rect:
            if (self.tablet_width_mm is not None and self.tablet_height_mm is None) or (
                self.tablet_height_mm is not None and self.tablet_width_mm is None
            ):
                raise ValueError("Both 'tablet_width_mm' and 'tablet_height_mm' must be provided for non-round tablets")
            raise ValueError(
                "Tablet dimensions must be specified: either 'tablet_diameter_mm' for round tablets "
                "or both 'tablet_width_mm' and 'tablet_height_mm' for non-round tablets"
            )

        if self.positions is not None and len(self.positions) > self.tablet_count:
            raise ValueError(
                f"Number of cavity positions ({len(self.positions)}) exceeds specified tablet_count ({self.tablet_count})"
            )

        return self

    @property
    def effective_width_mm(self) -> float:
        if self.tablet_width_mm is not None:
            return self.tablet_width_mm
        return self.tablet_diameter_mm or 0.0

    @property
    def effective_height_mm(self) -> float:
        if self.tablet_height_mm is not None:
            return self.tablet_height_mm
        return self.tablet_diameter_mm or 0.0


class TabletMarkingConfig(BaseModel):
    marking_enabled: bool = Field(default=False, description="Whether human-readable marking on tablet is enabled")
    marking_side: MarkingSide = Field(default=MarkingSide.FRONT, description="Tablet marking side (front, back, both)")
    marking_method: MarkingMethod = Field(
        default=MarkingMethod.INKJET, description="Marking method (emboss, deboss, inkjet, laser, other)"
    )
    code_value: Optional[str] = Field(default=None, description="Human-readable code marked on tablet (e.g. MED001)")

    @model_validator(mode="after")
    def validate_marking(self) -> "TabletMarkingConfig":
        if self.marking_enabled:
            if not self.code_value or not self.code_value.strip():
                raise ValueError("Tablet marking is enabled but no 'code_value' was provided")
        return self


class CodeConfig(BaseModel):
    code_value: Optional[str] = Field(default=None, description="Batch-linked code value, e.g. MED001")
    value: Optional[str] = Field(default=None, description="Alias for code_value")
    code_type: CodeType = Field(default=CodeType.HUMAN_READABLE, description="Code type: human-readable, datamatrix, barcode")
    type: Optional[CodeType] = Field(default=None, description="Alias for code_type")
    minimum_code_size_mm: Optional[float] = Field(default=None, gt=0, description="Minimum code dimension in mm")
    min_size_mm: Optional[float] = Field(default=None, gt=0, description="Alias for minimum_code_size_mm")
    code_width_mm: Optional[float] = Field(default=None, gt=0, description="Code physical width in mm")
    code_height_mm: Optional[float] = Field(default=None, gt=0, description="Code physical height in mm")
    orientation: Optional[float] = Field(default=None, description="Orientation angle in degrees")
    orientation_deg: float = Field(default=0.0, description="Orientation in degrees")

    @model_validator(mode="after")
    def sync_and_validate(self) -> "CodeConfig":
        # Synchronize aliases
        if self.type is not None:
            object.__setattr__(self, "code_type", self.type)
        else:
            object.__setattr__(self, "type", self.code_type)

        actual_val = self.code_value if self.code_value is not None else self.value
        if actual_val is not None:
            if not actual_val.strip():
                raise ValueError("Code value cannot be empty string")
            object.__setattr__(self, "code_value", actual_val)
            object.__setattr__(self, "value", actual_val)

        actual_min_size = self.minimum_code_size_mm if self.minimum_code_size_mm is not None else self.min_size_mm
        if actual_min_size is not None:
            object.__setattr__(self, "minimum_code_size_mm", actual_min_size)
            object.__setattr__(self, "min_size_mm", actual_min_size)

        actual_orient = self.orientation if self.orientation is not None else self.orientation_deg
        object.__setattr__(self, "orientation_deg", actual_orient)
        object.__setattr__(self, "orientation", actual_orient)

        return self


class MedicineInformation(BaseModel):
    """Configurable medicine packaging information allowing dynamic extra fields."""

    model_config = ConfigDict(extra="allow")

    medicine_name: Optional[str] = None
    strength: Optional[str] = None
    ingredients: Optional[str] = None
    healthcare_use: Optional[str] = None
    batch: Optional[str] = None
    mfg: Optional[str] = None
    exp: Optional[str] = None
    manufacturer: Optional[str] = None
    mrp: Optional[str] = None
    storage: Optional[str] = None
    warnings: Optional[str] = None
    code: Optional[str] = None


class PrintingConstraints(BaseModel):
    """Physical printing constraints in millimeters and DPI."""

    printer_resolution_dpi: Optional[float] = Field(default=None, gt=0, description="Printer resolution in DPI")
    minimum_text_size_mm: Optional[float] = Field(default=None, ge=0, description="Minimum text font height in mm")
    minimum_element_spacing_mm: float = Field(default=1.0, ge=0, description="Minimum spacing between elements in mm")
    minimum_margin_mm: float = Field(default=1.0, ge=0, description="Minimum margin to printing area in mm")


class LayoutElement(BaseModel):
    id: str
    type: ElementType
    content: Optional[str] = None
    x_mm: float
    y_mm: float
    width_mm: float = Field(gt=0)
    height_mm: float = Field(gt=0)
    font_size_mm: Optional[float] = Field(default=None, gt=0)
    rotation_deg: float = Field(default=0.0)
    code_type: Optional[CodeType] = None


class ValidationResult(BaseModel):
    valid: bool
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)


class LayoutAlternative(BaseModel):
    strategy: str = Field(description="Strategy name: COST, BALANCED, ACCESSIBILITY")
    layout: Optional[Dict[str, Any]] = Field(default=None, description="Physical layout details and element positions")
    score: float = Field(ge=0.0, le=1.0, description="Normalized common score [0.0, 1.0]")
    space_utilization: float = Field(ge=0.0, le=1.0, description="Physical element packing density")
    readability: float = Field(ge=0.0, le=1.0, description="Font scale and text clearance metric")
    print_efficiency: float = Field(ge=0.0, le=1.0, description="Printable area coverage efficiency")
    cost_efficiency: float = Field(ge=0.0, le=1.0, description="Cost efficiency metric")
    scan_reliability: float = Field(ge=0.0, le=1.0, description="Physical code orientation and quiet-zone reliability")
    warnings: List[str] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)


class LayoutPlan(BaseModel):
    id: Optional[str] = None
    package: Optional[PackageModel] = None
    elements: List[LayoutElement] = Field(default_factory=list)
    validation: Optional[ValidationResult] = None
    success: bool = True
    warnings: List[str] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)
    cost_efficiency: Optional[float] = None
    used_printable_area: Optional[float] = None
    unused_printable_area: Optional[float] = None
    balanced_score: Optional[float] = None
    space_utilization: Optional[float] = None
    readability: Optional[float] = None
    print_efficiency: Optional[float] = None
    code_reliability: Optional[float] = None
    accessibility_score: Optional[float] = None
    spacing_quality: Optional[float] = None
    whitespace_quality: Optional[float] = None
    optimization_strategy: Optional[str] = None
    candidates_evaluated: Optional[int] = None
    score: Optional[float] = None
    scan_reliability: Optional[float] = None
    recommended_strategy: Optional[str] = None
    recommended_layout: Optional[Dict[str, Any]] = None
    alternatives: Optional[List[LayoutAlternative]] = None
    layout: Optional[Dict[str, Any]] = None

    @model_validator(mode="after")
    def populate_layout_dict(self) -> "LayoutPlan":
        if self.layout is None and self.package is not None:
            object.__setattr__(
                self,
                "layout",
                {
                    "package_width_mm": self.package.package_width_mm,
                    "package_height_mm": self.package.package_height_mm,
                    "elements": [e.model_dump() for e in self.elements],
                    "cost_efficiency": self.cost_efficiency,
                    "used_printable_area": self.used_printable_area,
                    "unused_printable_area": self.unused_printable_area,
                    "balanced_score": self.balanced_score,
                    "space_utilization": self.space_utilization,
                    "readability": self.readability,
                    "print_efficiency": self.print_efficiency,
                    "code_reliability": self.code_reliability,
                    "accessibility_score": self.accessibility_score,
                    "spacing_quality": self.spacing_quality,
                    "whitespace_quality": self.whitespace_quality,
                    "score": self.score,
                    "scan_reliability": self.scan_reliability,
                },
            )
        elif self.layout is not None:
            self.sync_layout_dict()
        return self

    def sync_layout_dict(self) -> None:
        if self.layout is not None:
            self.layout["cost_efficiency"] = self.cost_efficiency
            self.layout["used_printable_area"] = self.used_printable_area
            self.layout["unused_printable_area"] = self.unused_printable_area
            self.layout["balanced_score"] = self.balanced_score
            self.layout["space_utilization"] = self.space_utilization
            self.layout["readability"] = self.readability
            self.layout["print_efficiency"] = self.print_efficiency
            self.layout["code_reliability"] = self.code_reliability
            self.layout["accessibility_score"] = self.accessibility_score
            self.layout["spacing_quality"] = self.spacing_quality
            self.layout["whitespace_quality"] = self.whitespace_quality
            self.layout["score"] = self.score
            self.layout["scan_reliability"] = self.scan_reliability
            self.layout["elements"] = [e.model_dump() for e in self.elements]


class LayoutRequest(BaseModel):
    """Complete structured layout input model for physical dimensions and printing requirements."""

    package: PackageModel
    tablet: TabletConfig
    marking: Optional[TabletMarkingConfig] = None
    code: Optional[CodeConfig] = None
    information: MedicineInformation = Field(default_factory=MedicineInformation)
    constraints: PrintingConstraints = Field(default_factory=PrintingConstraints)
    min_margin_mm: Optional[float] = Field(default=None, ge=0, description="Convenience alias for constraints.minimum_margin_mm")
    optimization_target: Optional[str] = Field(default="RECOMMEND", description="Optimization goal: RECOMMEND, COST, BALANCED, ACCESSIBILITY")

    @model_validator(mode="after")
    def validate_layout_request_consistency(self) -> "LayoutRequest":
        # Synchronize min_margin_mm if specified
        if self.min_margin_mm is not None:
            self.constraints.minimum_margin_mm = self.min_margin_mm

        # Validate cavity positions against package boundaries
        if self.tablet.positions:
            w = self.tablet.effective_width_mm
            h = self.tablet.effective_height_mm
            for pos in self.tablet.positions:
                cav_w = pos.width_mm or w
                cav_h = pos.height_mm or h
                if pos.x_mm + cav_w > self.package.package_width_mm:
                    raise ValueError(
                        f"Tablet cavity at x={pos.x_mm}mm + width={cav_w}mm exceeds package width ({self.package.package_width_mm}mm)"
                    )
                if pos.y_mm + cav_h > self.package.package_height_mm:
                    raise ValueError(
                        f"Tablet cavity at y={pos.y_mm}mm + height={cav_h}mm exceeds package height ({self.package.package_height_mm}mm)"
                    )

        # Validate code dimensions against printing area if explicit code size given
        if self.code:
            code_w = self.code.code_width_mm or self.code.minimum_code_size_mm
            code_h = self.code.code_height_mm or self.code.minimum_code_size_mm
            if code_w and code_w > self.package.printing_area_width_mm:
                raise ValueError(
                    f"Code width ({code_w}mm) exceeds printing area width ({self.package.printing_area_width_mm}mm)"
                )
            if code_h and code_h > self.package.printing_area_height_mm:
                raise ValueError(
                    f"Code height ({code_h}mm) exceeds printing area height ({self.package.printing_area_height_mm}mm)"
                )

        return self


# Backward-compatible alias
LayoutRecommendationRequest = LayoutRequest


class LayoutPreviewRequest(BaseModel):
    layout: Optional[LayoutPlan] = None
    request: Optional[LayoutRequest] = None

    @model_validator(mode="after")
    def validate_has_layout_or_request(self) -> "LayoutPreviewRequest":
        if self.layout is None and self.request is None:
            raise ValueError("Either 'layout' or 'request' must be provided for preview")
        return self
