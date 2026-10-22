from dataclasses import dataclass, field
from typing import Dict, Any, List

def create_text_material(text_id: str, content: str) -> Dict[str, Any]:
    """Tạo text material object chuẩn cho CapCut PC draft."""
    return {
        "id": text_id,
        "content": content,
        "type": "text",
        "font_path": "",
        "font_size": 10.0,
        "alignment": 1,
        "styles": []
    }

def create_text_segment(segment_id: str, material_id: str, start_us: int, duration_us: int) -> Dict[str, Any]:
    """Tạo text timeline segment khớp với animation."""
    return {
        "id": segment_id,
        "material_id": material_id,
        "source_timerange": None,
        "target_timerange": {
            "duration": duration_us,
            "start": start_us
        }
    }
