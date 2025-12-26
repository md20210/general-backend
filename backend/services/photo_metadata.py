"""Photo metadata extraction service using Pillow (PIL)."""
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


def extract_photo_metadata(file_path: Path) -> Dict[str, Any]:
    """
    Extract EXIF metadata from a photo file.

    Args:
        file_path: Path to the photo file

    Returns:
        Dictionary with extracted metadata (filename, size, dimensions, EXIF data, GPS)
    """
    metadata = {
        "filename": file_path.name,
        "size_bytes": file_path.stat().st_size if file_path.exists() else 0,
    }

    try:
        with Image.open(file_path) as image:
            # Basic image info
            metadata["width"] = image.width
            metadata["height"] = image.height
            metadata["format"] = image.format
            metadata["mode"] = image.mode

            # EXIF data
            exif = image.getexif()
            if exif:
                # DateTime Original (when photo was taken)
                if 36867 in exif:  # DateTimeOriginal
                    dt_str = exif[36867]
                    try:
                        # Parse EXIF datetime format: "YYYY:MM:DD HH:MM:SS"
                        dt = datetime.strptime(dt_str, "%Y:%m:%d %H:%M:%S")
                        metadata["datetime_original"] = dt.isoformat()
                    except ValueError:
                        metadata["datetime_original"] = dt_str

                # Camera info
                if 271 in exif:  # Make
                    metadata["camera_make"] = exif[271]
                if 272 in exif:  # Model
                    metadata["camera_model"] = exif[272]

                # Orientation
                if 274 in exif:  # Orientation
                    metadata["orientation"] = exif[274]

                # ISO Speed
                if 34855 in exif:  # ISOSpeedRatings
                    metadata["iso"] = exif[34855]

                # Aperture (F-number)
                if 33437 in exif:  # FNumber
                    metadata["f_number"] = float(exif[33437])

                # Exposure Time
                if 33434 in exif:  # ExposureTime
                    metadata["exposure_time"] = str(exif[33434])

                # Focal Length
                if 37386 in exif:  # FocalLength
                    metadata["focal_length"] = float(exif[37386])

                # GPS data
                gps_info = exif.get_ifd(0x8825)  # GPS IFD tag
                if gps_info:
                    gps_data = {}
                    for tag, value in gps_info.items():
                        tag_name = GPSTAGS.get(tag, tag)
                        gps_data[tag_name] = value

                    # Convert GPS to decimal degrees
                    lat = gps_to_decimal(
                        gps_data.get("GPSLatitude"),
                        gps_data.get("GPSLatitudeRef")
                    )
                    lon = gps_to_decimal(
                        gps_data.get("GPSLongitude"),
                        gps_data.get("GPSLongitudeRef")
                    )

                    if lat is not None and lon is not None:
                        metadata["gps"] = {
                            "latitude": lat,
                            "longitude": lon,
                        }

                        # Altitude if available
                        if "GPSAltitude" in gps_data:
                            try:
                                altitude = float(gps_data["GPSAltitude"])
                                metadata["gps"]["altitude"] = altitude
                            except (ValueError, TypeError):
                                pass

    except Exception as e:
        logger.error(f"Failed to extract metadata from {file_path}: {e}")
        metadata["error"] = str(e)

    return metadata


def gps_to_decimal(coords, ref) -> Optional[float]:
    """
    Convert GPS coordinates from degrees/minutes/seconds to decimal degrees.

    Args:
        coords: Tuple of (degrees, minutes, seconds)
        ref: Reference (N/S for latitude, E/W for longitude)

    Returns:
        Decimal degrees or None if conversion fails
    """
    if not coords or not ref:
        return None

    try:
        # coords is a tuple of (degrees, minutes, seconds)
        degrees = float(coords[0])
        minutes = float(coords[1])
        seconds = float(coords[2])

        decimal = degrees + (minutes / 60.0) + (seconds / 3600.0)

        # South and West are negative
        if ref in ["S", "W"]:
            decimal = -decimal

        return round(decimal, 6)  # Round to 6 decimal places (~0.1 meter precision)
    except (ValueError, TypeError, IndexError) as e:
        logger.error(f"Failed to convert GPS coords {coords} {ref}: {e}")
        return None
