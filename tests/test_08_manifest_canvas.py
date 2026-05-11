import os

from iiiflow.manifest_builders.canvas import create_iiif_canvas
from test_utils import create_temp_fixture_config


class DummyCanvas:
    def __init__(self, canvas_id, label=None, height=None, width=None):
        self.id = canvas_id
        self.label = label
        self.height = height
        self.width = width
        self.duration = None
        self.items = []
        self.annotations = None
        self.rendering = None
        self.thumbnail = None
        self.added_images = []

    def add_image(self, **kwargs):
        self.added_images.append(kwargs)


class DummyManifest:
    def __init__(self):
        self.canvases = []

    def make_canvas(self, id, label=None, height=None, width=None):
        canvas = DummyCanvas(id, label=label, height=height, width=width)
        self.canvases.append(canvas)
        return canvas


def test_create_iiif_canvas_image_adds_hocr_rendering_from_fixture(tmp_path):
    temp_discovery_storage_root, _ = create_temp_fixture_config(tmp_path)
    object_path = os.path.join(temp_discovery_storage_root, "ua200", "fd198d1a2ebfdddad630c9698a38df29")
    resource_path = os.path.join(object_path, "ptif", "fd198d1a2ebfdddad630c9698a38df29-1.ptif")

    manifest = DummyManifest()
    obj_url_root = "https://media.archives.albany.edu/ua200/fd198d1a2ebfdddad630c9698a38df29"

    canvas = create_iiif_canvas(
        manifest,
        "https://media.archives.albany.edu",
        obj_url_root,
        "fd198d1a2ebfdddad630c9698a38df29-1.ptif",
        "Image",
        resource_path,
        1,
        {"url": f"{obj_url_root}/thumbnail.jpg", "width": 300, "height": 225},
        resource_format="ptif",
        height=1125,
        width=1500,
        image_url="https://media.archives.albany.edu/iiif/3/ua200%2Ffd198d1a2ebfdddad630c9698a38df29%2Fptif%2Ffd198d1a2ebfdddad630c9698a38df29-1.ptif",
        filename="fd198d1a2ebfdddad630c9698a38df29-1",
        lang_code="en",
    )

    assert canvas.added_images, "Expected canvas image payload to be added."
    assert canvas.added_images[0]["format"] == "image/tiff"
    assert canvas.rendering and canvas.rendering[0]["format"] == "text/vnd.hocr+html"
    assert canvas.thumbnail and canvas.thumbnail[0]["width"] == 300 and canvas.thumbnail[0]["height"] == 225


def test_create_iiif_canvas_audio_adds_alternate_audio_and_vtt_from_fixture(tmp_path):
    temp_discovery_storage_root, _ = create_temp_fixture_config(tmp_path)
    object_path = os.path.join(temp_discovery_storage_root, "apap401", "56b3ab1c00ac03862ef0f47650905013")
    resource_path = os.path.join(object_path, "ogg", "George Edwards.ogg")

    manifest = DummyManifest()
    obj_url_root = "https://media.archives.albany.edu/apap401/56b3ab1c00ac03862ef0f47650905013"

    canvas = create_iiif_canvas(
        manifest,
        "https://media.archives.albany.edu",
        obj_url_root,
        "George Edwards.ogg",
        "Audio",
        resource_path,
        1,
        {"url": f"{obj_url_root}/thumbnail.jpg", "width": 442, "height": 442},
        media_url=f"{obj_url_root}/ogg/George%20Edwards.ogg",
        filename="George%20Edwards",
        lang_code="en",
    )

    assert canvas.items and canvas.items[0].items, "Expected painting annotations for audio canvas."
    painting_bodies = [item.body for item in canvas.items[0].items]
    formats = {
        (body.get("format") if isinstance(body, dict) else str(getattr(body, "format", "")))
        for body in painting_bodies
    }
    assert "audio/ogg" in formats
    assert "audio/mpeg" in formats

    assert canvas.annotations and canvas.annotations[0]["items"][0]["body"], "Expected VTT supplementing annotation."
    assert canvas.annotations[0]["items"][0]["body"][0]["format"] == "text/vtt"
