from enum import Enum
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class CodeType(str, Enum):
    HUMAN_READABLE = "human-readable"
    DATAMATRIX = "datamatrix"
    BARCODE = "barcode"
    QR = "qr"


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
    code_type: CodeType = Field(default=CodeType.HUMAN_READABLE, description="Code type: human-readable, datamatrix, barcode, qr")
    type: Optional[Any] = Field(default=None, description="Alias for code_type")
    minimum_code_size_mm: Optional[float] = Field(default=None, gt=0, description="Minimum code dimension in mm")
    min_size_mm: Optional[float] = Field(default=None, gt=0, description="Alias for minimum_code_size_mm")
    code_width_mm: Optional[float] = Field(default=None, gt=0, description="Code physical width in mm")
    code_height_mm: Optional[float] = Field(default=None, gt=0, description="Code physical height in mm")
    orientation: Optional[float] = Field(default=None, description="Orientation angle in degrees")
    orientation_deg: float = Field(default=0.0, description="Orientation in degrees")
    serial_number: Optional[str] = Field(default=None, description="Human-readable serial number associated with code")

    @field_validator("code_type", "type", mode="before")
    @classmethod
    def normalize_code_type(cls, v: Any) -> Any:
        if isinstance(v, str):
            v_norm = v.strip().lower().replace("_", "-")
            if v_norm in ("qr", "qrcode", "qr-code"):
                return CodeType.QR
            if v_norm in ("datamatrix", "data-matrix"):
                return CodeType.DATAMATRIX
            if v_norm in ("barcode", "bar-code"):
                return CodeType.BARCODE
            if v_norm in ("human-readable", "humanreadable"):
                return CodeType.HUMAN_READABLE
        return v

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

        # Ensure square dimensions for 2D matrix codes when min_size is supplied and width or height is missing
        if self.code_type in (CodeType.DATAMATRIX, CodeType.QR):
            min_dim = actual_min_size
            if min_dim:
                if self.code_width_mm is None and self.code_height_mm is None:
                    object.__setattr__(self, "code_width_mm", min_dim)
                    object.__setattr__(self, "code_height_mm", min_dim)
                elif self.code_width_mm is not None and self.code_height_mm is None:
                    object.__setattr__(self, "code_height_mm", self.code_width_mm)
                elif self.code_height_mm is not None and self.code_width_mm is None:
                    object.__setattr__(self, "code_width_mm", self.code_height_mm)

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
    serial_number: Optional[str] = None
    dosage: Optional[str] = None
    batch_number: Optional[str] = None
    manufacturing_date: Optional[str] = None
    expiry_date: Optional[str] = None

    @model_validator(mode="after")
    def map_backend_fields(self) -> "MedicineInformation":
        if not self.strength and self.dosage:
            object.__setattr__(self, "strength", self.dosage)
        if not self.batch and self.batch_number:
            object.__setattr__(self, "batch", self.batch_number)
        if not self.mfg and self.manufacturing_date:
            object.__setattr__(self, "mfg", self.manufacturing_date)
        if not self.exp and self.expiry_date:
            object.__setattr__(self, "exp", self.expiry_date)
        return self


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


class StructuredPrintDataRequest(BaseModel):
    """Adapter model accepting backend-style structured print data or standard layout inputs."""

    model_config = ConfigDict(extra="allow")

    package: Optional[Union[PackageModel, Dict[str, Any]]] = None
    tablet: Optional[Union[TabletConfig, Dict[str, Any]]] = None
    marking: Optional[TabletMarkingConfig] = None
    code: Optional[Any] = None
    codes: Optional[List[Dict[str, Any]]] = None
    medicine: Optional[Dict[str, Any]] = None
    batch: Optional[Dict[str, Any]] = None
    information: Optional[MedicineInformation] = None
    dosage: Optional[str] = None
    batch_number: Optional[str] = None
    manufacturing_date: Optional[str] = None
    expiry_date: Optional[str] = None
    serial_number: Optional[str] = None
    constraints: PrintingConstraints = Field(default_factory=PrintingConstraints)
    min_margin_mm: Optional[float] = None
    optimization_target: Optional[str] = "RECOMMEND"

    def to_layout_request(self) -> LayoutRequest:
        return parse_print_data_to_layout_request(self.model_dump())


def parse_print_data_to_layout_request(
    data: Union[LayoutRequest, StructuredPrintDataRequest, Dict[str, Any]]
) -> LayoutRequest:
    """Lightweight adapter that converts backend structured print data or existing requests into a LayoutRequest."""
    if isinstance(data, LayoutRequest):
        return data

    if isinstance(data, StructuredPrintDataRequest):
        data = data.model_dump()

    if not isinstance(data, dict):
        raise ValueError("Print data must be a dictionary or LayoutRequest instance.")

    data_dict = dict(data)

    # Resolve medicine information
    med_info_dict: Dict[str, Any] = {}
    if data_dict.get("information"):
        if isinstance(data_dict["information"], MedicineInformation):
            med_info_dict = data_dict["information"].model_dump()
        elif isinstance(data_dict["information"], dict):
            med_info_dict = dict(data_dict["information"])

    # If backend provided 'medicine' dict (e.g. from backend API /api/v1/medicines)
    if "medicine" in data_dict and isinstance(data_dict["medicine"], dict):
        med = data_dict["medicine"]
        if "name" in med and not med_info_dict.get("medicine_name"):
            med_info_dict["medicine_name"] = med["name"]
        if "dosage" in med and not med_info_dict.get("dosage") and not med_info_dict.get("strength"):
            med_info_dict["dosage"] = med["dosage"]
        if "manufacturer" in med and not med_info_dict.get("manufacturer"):
            med_info_dict["manufacturer"] = med["manufacturer"]
        for k, v in med.items():
            if k not in med_info_dict:
                med_info_dict[k] = v

    # If backend provided 'batch' dict (e.g. from backend API /api/v1/batches)
    if "batch" in data_dict and isinstance(data_dict["batch"], dict):
        batch = data_dict["batch"]
        if "batch_number" in batch and not med_info_dict.get("batch_number") and not med_info_dict.get("batch"):
            med_info_dict["batch_number"] = batch["batch_number"]
        if "manufacturing_date" in batch and not med_info_dict.get("manufacturing_date") and not med_info_dict.get("mfg"):
            med_info_dict["manufacturing_date"] = batch["manufacturing_date"]
        if "expiry_date" in batch and not med_info_dict.get("expiry_date") and not med_info_dict.get("exp"):
            med_info_dict["expiry_date"] = batch["expiry_date"]
        for k, v in batch.items():
            if k not in med_info_dict:
                med_info_dict[k] = v

    # Top-level direct fields mapping if provided
    for field_name in (
        "dosage",
        "batch_number",
        "manufacturing_date",
        "expiry_date",
        "serial_number",
        "medicine_name",
        "strength",
        "batch",
        "mfg",
        "exp",
    ):
        val = data_dict.get(field_name)
        if val is not None and isinstance(val, str) and field_name not in med_info_dict:
            med_info_dict[field_name] = val

    # If backend provided 'code' dict
    code_config_dict: Optional[Dict[str, Any]] = None
    if "code" in data_dict and isinstance(data_dict["code"], dict):
        code_input = dict(data_dict["code"])
        c_val = (
            code_input.get("code_data")
            or code_input.get("verification_url")
            or code_input.get("value")
            or code_input.get("code_value")
        )
        c_type = code_input.get("code_type") or code_input.get("type") or "datamatrix"
        c_serial = code_input.get("serial_number")
        if c_serial and not med_info_dict.get("serial_number"):
            med_info_dict["serial_number"] = c_serial

        code_config_dict = {
            "code_value": c_val,
            "code_type": c_type,
            "minimum_code_size_mm": code_input.get("min_size_mm") or code_input.get("minimum_code_size_mm"),
            "code_width_mm": code_input.get("code_width_mm"),
            "code_height_mm": code_input.get("code_height_mm"),
            "orientation_deg": code_input.get("orientation_deg") or code_input.get("orientation") or 0.0,
            "serial_number": c_serial,
        }
    elif "code" in data_dict and data_dict["code"] is not None:
        if isinstance(data_dict["code"], CodeConfig):
            code_config_dict = data_dict["code"].model_dump()
        else:
            code_config_dict = data_dict["code"]

    # Also handle 'codes' list from /api/v1/codes/generate
    if (
        not code_config_dict
        and "codes" in data_dict
        and isinstance(data_dict["codes"], list)
        and len(data_dict["codes"]) > 0
    ):
        first_code = data_dict["codes"][0]
        c_val = first_code.get("code_data") or first_code.get("verification_url") or first_code.get("code_value")
        c_serial = first_code.get("serial_number")
        if c_serial and not med_info_dict.get("serial_number"):
            med_info_dict["serial_number"] = c_serial
        c_type = data_dict.get("code_type") or first_code.get("code_type") or "datamatrix"
        code_config_dict = {
            "code_value": c_val,
            "code_type": c_type,
            "minimum_code_size_mm": first_code.get("min_size_mm") or 12.0,
            "serial_number": c_serial,
        }

    # Resolve package
    pkg_input = data_dict.get("package") or data_dict.get("packaging")
    if not pkg_input and "package_width_mm" in data_dict and "package_height_mm" in data_dict:
        pkg_input = {
            "package_width_mm": data_dict["package_width_mm"],
            "package_height_mm": data_dict["package_height_mm"],
            "printing_area_width_mm": data_dict.get("printing_area_width_mm", data_dict["package_width_mm"]),
            "printing_area_height_mm": data_dict.get("printing_area_height_mm", data_dict["package_height_mm"]),
            "printing_area_x_mm": data_dict.get("printing_area_x_mm", 0.0),
            "printing_area_y_mm": data_dict.get("printing_area_y_mm", 0.0),
        }

    # Resolve tablet
    tbl_input = data_dict.get("tablet") or data_dict.get("tablets")
    if not tbl_input and "tablet_count" in data_dict and "tablet_diameter_mm" in data_dict:
        tbl_input = {
            "tablet_count": data_dict["tablet_count"],
            "tablet_diameter_mm": data_dict["tablet_diameter_mm"],
        }

    return LayoutRequest(
        package=pkg_input,
        tablet=tbl_input,
        marking=data_dict.get("marking"),
        code=code_config_dict,
        information=MedicineInformation(**med_info_dict),
        constraints=data_dict.get("constraints") or PrintingConstraints(),
        min_margin_mm=data_dict.get("min_margin_mm"),
        optimization_target=data_dict.get("optimization_target") or "RECOMMEND",
    )
