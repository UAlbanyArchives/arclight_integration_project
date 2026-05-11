import os
import urllib.parse
from iiif_prezi3 import Annotation, AnnotationPage
from ..utils import get_media_info


def _add_audio_alternative_annotation(
    annotation_page,
    resource_path,
    obj_url_root,
    manifest_url_root,
    page_count,
    duration,
):
    audio_filename, audio_ext = os.path.splitext(os.path.basename(resource_path))
    obj_path = os.path.dirname(os.path.dirname(resource_path))
    ogg_path = os.path.join(obj_path, "ogg")
    mp3_path = os.path.join(obj_path, "mp3")

    if audio_ext == ".ogg" and os.path.isdir(mp3_path):
        audio_url = f"{obj_url_root}/mp3/{urllib.parse.quote(audio_filename)}.mp3"
        annotation_ogg = Annotation(
            id=f"{obj_url_root}/canvas/{page_count}/page/annotation/mp3",
            motivation="painting",
            body={
                "id": audio_url,
                "type": "Sound",
                "format": "audio/mpeg",
                "duration": duration
            },
            target=f"{manifest_url_root}/canvas/p{page_count}"
        )
        annotation_page.items.append(annotation_ogg)
    elif audio_ext == ".mp3" and os.path.isdir(ogg_path):
        audio_url = f"{obj_url_root}/ogg/{urllib.parse.quote(audio_filename)}.ogg"
        annotation_mp3 = Annotation(
            id=f"{obj_url_root}/canvas/{page_count}/page/annotation/ogg",
            motivation="painting",
            body={
                "id": audio_url,
                "type": "Sound",
                "format": "audio/ogg",
                "duration": duration
            },
            target=f"{obj_url_root}/canvas/p{page_count}"
        )
        annotation_page.items.append(annotation_mp3)


def _attach_vtt_annotation_if_present(canvas, resource_path, obj_url_root, page_count, lang_code):
    vtt_file = os.path.join(
        os.path.dirname(os.path.dirname(resource_path)),
        "vtt",
        f"{os.path.splitext(os.path.basename(resource_path))[0]}.vtt",
    )
    if not os.path.exists(vtt_file):
        return

    canvas.annotations = [{
        "id": f"{obj_url_root}/canvas/{page_count}/supplementing",
        "type": "AnnotationPage",
        "items": [
            {
                "id": f"{obj_url_root}/canvas/{page_count}/annotation",
                "type": "Annotation",
                "motivation": "supplementing",
                "body": [
                    {
                        "id": f"{obj_url_root}/vtt/{os.path.basename(vtt_file)}",
                        "type": "Text",
                        "format": "text/vtt",
                        "label": {lang_code: ["WebVTT (captions)"]}
                    }
                ],
                "target": f"{obj_url_root}/canvas/p{page_count}"
            }
        ]
    }]


def _attach_hocr_rendering_if_present(canvas, resource_path, obj_url_root):
    hocr_file = os.path.join(
        os.path.dirname(os.path.dirname(resource_path)),
        "hocr",
        f"{os.path.splitext(os.path.basename(resource_path))[0]}.hocr",
    )
    if not os.path.exists(hocr_file):
        return

    canvas.rendering = [{
        "id": f"{obj_url_root}/hocr/{urllib.parse.quote(os.path.basename(hocr_file))}",
        "label": "HOCR data (OCR)",
        "type": "Text",
        "format": "text/vnd.hocr+html",
        "profile": "http://kba.cloud/hocr-spec/1.2/"
    }]


def create_iiif_canvas(manifest, manifest_url_root, obj_url_root, label, resource_type, resource_path, page_count, thumbnail_data, **kwargs):
    """Create a IIIF Canvas for images, videos, or audio, with optional thumbnail."""
    height = kwargs.get("height", None)
    width = kwargs.get("width", None)
    lang_code = kwargs["lang_code"]

    if resource_type == "Image":
        canvas = manifest.make_canvas(id=f"{obj_url_root}/canvas/p{page_count}", label={lang_code: [label]}, height=height, width=width)
        service = [{
            "id": kwargs["image_url"],
            "profile": "level1",
            "type": "ImageService3"
        }]
        if kwargs.get("resource_format", None) == "ptif":
            image_mime = "image/tiff"
        else:
            image_mime = "image/jpeg"
        canvas.add_image(
            image_url=kwargs["image_url"] + "/full/max/0/default.jpg",
            anno_page_id=f"{obj_url_root}/page/p{page_count}/{page_count}",
            anno_id=f"{obj_url_root}/annotation/{kwargs['filename']}",
            format=image_mime,
            height=height,
            width=width,
            service=service,
        )
        _attach_hocr_rendering_if_present(canvas, resource_path, obj_url_root)

    else:
        duration, mimetype, video_width, video_height = get_media_info(resource_path)

        canvas = manifest.make_canvas(id=f"{obj_url_root}/canvas/p{page_count}", label=label)
        canvas.duration = duration

        anno_page_id = f"{obj_url_root}/canvas/page/p{page_count}{page_count}"
        annotation_page = AnnotationPage(id=anno_page_id)

        annotation = Annotation(
            id=f"{obj_url_root}/canvas/{page_count}/page/annotation",
            motivation="painting",
            body={
                "id": kwargs["media_url"],
                "type": "Video" if resource_type == "Video" else "Sound",
                "format": mimetype,
                "duration": duration,
                "width": video_width,
                "height": video_height
            },
            target=f"{obj_url_root}/canvas/p{page_count}"
        )
        annotation_page.items.append(annotation)

        if resource_type == "Audio":
            _add_audio_alternative_annotation(
                annotation_page,
                resource_path,
                obj_url_root,
                manifest_url_root,
                page_count,
                duration,
            )

        canvas.items.append(annotation_page)
        _attach_vtt_annotation_if_present(canvas, resource_path, obj_url_root, page_count, lang_code)

    if page_count == 1 and "url" in thumbnail_data:
        thumbnail_width = thumbnail_data.get("width", None)
        thumbnail_height = thumbnail_data.get("height", None)

        thumbnail = {
            "id": thumbnail_data["url"],
            "type": "Image",
            "format": "image/jpeg",
        }

        if thumbnail_width and thumbnail_height:
            thumbnail["width"] = thumbnail_width
            thumbnail["height"] = thumbnail_height

        canvas.thumbnail = [thumbnail]

    return canvas
