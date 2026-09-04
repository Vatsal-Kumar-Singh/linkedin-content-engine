"""Animated card variants — a seamless looping GIF of one rendered card.

Only the background tracings move. The type never does: a moving headline is
the tell that separates a template pack from an advert, and the whole design
direction is built against looking generated.

No ffmpeg on this machine, so frames are encoded with Pillow. GIF is the safe
target — LinkedIn accepts it and converts to video server-side. If ffmpeg ever
lands, `encode_mp4` below is the only thing that needs writing.

Seamlessness comes from arithmetic, not crossfading: both rings share one
period, so capturing exactly one period at a fixed step means the last frame
hands back to the first.
"""
from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

# Frame pacing. 12fps is deliberate: the motion is a slow drift, and doubling
# the frames doubles the file for no perceptible gain.
DEFAULT_FPS = 12
DEFAULT_SECONDS = 7.0


def _freeze_and_seek(page, seconds: float) -> None:
    """Drive CSS animations by clock rather than by waiting.

    Screenshotting a live animation samples wall-clock time, so two runs of the
    same card produce different files. Setting every animation to a paused,
    explicitly-seeked state makes each frame a pure function of its index —
    which is what makes the output reproducible and the loop exact.
    """
    page.evaluate(
        """(t) => {
            for (const a of document.getAnimations()) {
                a.pause();
                a.currentTime = t * 1000;
            }
        }""",
        seconds,
    )


def capture_frames(html_path: str, out_dir: str, width: int, height: int,
                   seconds: float = DEFAULT_SECONDS, fps: int = DEFAULT_FPS) -> List[str]:
    """Render one loop of the card as PNG frames."""
    import shutil

    from playwright.sync_api import sync_playwright

    # Start from an empty directory. A shorter re-render would otherwise leave
    # the tail of the previous one behind, and encode_mp4 globs the directory by
    # filename pattern rather than taking the returned list — so those orphans
    # would be spliced onto the end of the video the moment ffmpeg is installed.
    shutil.rmtree(out_dir, ignore_errors=True)
    os.makedirs(out_dir, exist_ok=True)
    total = max(2, int(round(seconds * fps)))
    paths: List[str] = []

    with sync_playwright() as p:
        browser = p.chromium.launch(args=["--force-color-profile=srgb",
                                          "--font-render-hinting=none"])
        page = browser.new_page(viewport={"width": width, "height": height},
                                device_scale_factor=1)
        try:
            page.goto("file://" + html_path, wait_until="load")
            try:
                page.evaluate("document.fonts.ready")
            except Exception:
                pass
            page.wait_for_timeout(200)

            for i in range(total):
                # Exclusive of the endpoint: frame `total` would be identical to
                # frame 0 and show as a stutter on loop.
                _freeze_and_seek(page, seconds * (i / float(total)))
                fp = os.path.join(out_dir, "frame_%03d.png" % i)
                page.screenshot(path=fp, clip={"x": 0, "y": 0,
                                               "width": width, "height": height})
                paths.append(fp)
        finally:
            browser.close()
    return paths


def encode_gif(frames: List[str], out_path: str, fps: int = DEFAULT_FPS,
               colors: int = 128) -> Dict[str, Any]:
    """Stitch frames into a looping GIF.

    A near-monochrome navy card quantises well, so 128 colours is generous.
    Dropping below ~96 starts banding the glow.
    """
    from PIL import Image

    if not frames:
        raise ValueError("no frames to encode")

    imgs = [Image.open(f).convert("RGB") for f in frames]
    pal = [im.quantize(colors=colors, method=Image.MEDIANCUT, dither=Image.FLOYDSTEINBERG)
           for im in imgs]
    pal[0].save(out_path, save_all=True, append_images=pal[1:],
                duration=int(round(1000.0 / fps)), loop=0, optimize=True)
    for im in imgs:
        im.close()
    return {"path": out_path, "frames": len(frames), "fps": fps,
            "bytes": os.path.getsize(out_path)}


def encode_mp4(frames: List[str], out_path: str, fps: int = DEFAULT_FPS) -> Optional[Dict[str, Any]]:
    """MP4 via ffmpeg when it is available. LinkedIn prefers it to GIF.

    Returns None when ffmpeg is absent so the caller can fall back to GIF
    rather than fail the run.
    """
    import shutil
    import subprocess

    if not shutil.which("ffmpeg"):
        return None
    pattern = os.path.join(os.path.dirname(frames[0]), "frame_%03d.png")
    cmd = ["ffmpeg", "-y", "-framerate", str(fps), "-i", pattern,
           "-c:v", "libx264", "-pix_fmt", "yuv420p",
           # LinkedIn re-encodes anyway; even dimensions are the only hard
           # requirement of yuv420p.
           "-vf", "scale=trunc(iw/2)*2:trunc(ih/2)*2",
           "-movflags", "+faststart", out_path]
    try:
        subprocess.run(cmd, capture_output=True, check=True, timeout=180)
    except Exception:
        return None
    return {"path": out_path, "frames": len(frames), "fps": fps,
            "bytes": os.path.getsize(out_path)}


def animate_card(html_path: str, out_dir: str, basename: str,
                 width: int, height: int,
                 seconds: float = DEFAULT_SECONDS,
                 fps: int = DEFAULT_FPS,
                 keep_frames: bool = False) -> Dict[str, Any]:
    """Capture one loop and encode it. MP4 when ffmpeg exists, else GIF.

    Frames are discarded afterwards — 84 full-size PNGs per card is ~80 MB of
    run-store per animated post, and once encoded they are reproducible from the
    HTML anyway. `keep_frames` is for debugging a loop that looks wrong.
    """
    import shutil

    frame_dir = os.path.join(out_dir, "_frames")
    frames = capture_frames(html_path, frame_dir, width, height, seconds, fps)
    try:
        out = encode_mp4(frames, os.path.join(out_dir, basename + ".mp4"), fps)
        if out:
            out["format"] = "mp4"
        else:
            out = encode_gif(frames, os.path.join(out_dir, basename + ".gif"), fps)
            out["format"] = "gif"
            out["note"] = ("ffmpeg not found — encoded as GIF. LinkedIn accepts GIF "
                           "and converts it server-side, but MP4 is smaller and "
                           "keeps more of the silver gradient.")
    finally:
        if not keep_frames:
            shutil.rmtree(frame_dir, ignore_errors=True)
    out["seconds"] = seconds
    return out
