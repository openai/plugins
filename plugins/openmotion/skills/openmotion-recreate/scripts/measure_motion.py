"""Observe source feature travel or compare corresponding source/output regions.

Optional helper using managed NumPy and OpenCV. Tracks a continuous interval at
each video's native frame rate. It reports observations and possible suppression,
with unresolved tracking kept explicit. It does not grade semantic fidelity.
"""

import argparse
import json
from pathlib import Path

from register_motion import rectangle


def track_frames(frames, roi, max_width=640):
    import cv2
    import numpy as np

    x, y, width, height = roi
    size = (min(width, max_width), max(1, round(height * min(1, max_width / width))))
    scale = np.array([size[0] / width, size[1] / height])
    rows = []
    previous = points = origins = None
    initial_count = 0
    for time, image in frames:
        crop = image[y:y + height, x:x + width]
        if crop.shape[:2] != (height, width):
            return {'status': 'unresolved', 'reason': 'The region extends outside a decoded frame.', 'samples': rows}
        gray = cv2.cvtColor(cv2.resize(crop, size), cv2.COLOR_BGR2GRAY)
        if previous is None:
            points = cv2.goodFeaturesToTrack(gray, 160, .02, 6)
            if points is None or len(points) < 8:
                return {'status': 'unresolved', 'reason': 'Fewer than eight trackable features.', 'samples': []}
            origins = points.copy()
            initial_count = len(points)
        else:
            current, forward_ok, _ = cv2.calcOpticalFlowPyrLK(previous, gray, points, None)
            if current is None or forward_ok is None:
                return {'status': 'unresolved', 'reason': 'Forward tracking failed.', 'samples': rows}
            back, backward_ok, _ = cv2.calcOpticalFlowPyrLK(gray, previous, current, None)
            if back is None or backward_ok is None:
                return {'status': 'unresolved', 'reason': 'Backward tracking failed.', 'samples': rows}
            valid = (forward_ok.ravel() == 1) & (backward_ok.ravel() == 1)
            valid &= np.linalg.norm(back - points, axis=2).ravel() <= 1.25
            points, origins = current[valid], origins[valid]
            if len(points) < 8:
                return {'status': 'unresolved', 'reason': 'Fewer than eight features remain reliably tracked.', 'samples': rows}
        displacement = (points - origins).reshape(-1, 2) / scale
        median = np.median(displacement, axis=0)
        rows.append({'time': time, 'retainedFeatures': len(points),
                     'medianDxPx': float(median[0]), 'medianDyPx': float(median[1]),
                     'p25DisplacementPx': np.percentile(displacement, 25, axis=0).tolist(),
                     'p75DisplacementPx': np.percentile(displacement, 75, axis=0).tolist()})
        previous = gray
    if len(rows) < 2:
        return {'status': 'unresolved', 'reason': 'At least two decoded frames are needed.', 'samples': rows}
    positions = np.array([[row['medianDxPx'], row['medianDyPx']] for row in rows])
    indices = np.linspace(0, len(points) - 1, min(12, len(points))).astype(int)
    return {'status': 'measured', 'initialFeatures': initial_count, 'retainedFeatures': len(points),
            'spanPx': np.ptp(positions, axis=0).tolist(),
            'pathLengthPx': float(np.linalg.norm(np.diff(positions, axis=0), axis=1).sum()),
            'pointPairs': [{'start': (origins[index, 0] / scale + [x, y]).tolist(),
                           'end': (points[index, 0] / scale + [x, y]).tolist()} for index in indices],
            'samples': rows}


def measure_video(filename, start, end, roi, max_width):
    import cv2
    import numpy as np

    capture = cv2.VideoCapture(str(filename))
    width, height = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH)), int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = capture.get(cv2.CAP_PROP_FPS)
    if not capture.isOpened() or min(width, height) <= 0 or not np.isfinite(fps) or fps <= 0:
        capture.release()
        return {'status': 'unresolved', 'reason': 'No decodable video with a usable frame rate.'}
    region = roi or [0, 0, width, height]
    capture.set(cv2.CAP_PROP_POS_FRAMES, round(start * fps))

    def frames():
        while True:
            ok, image = capture.read()
            if not ok:
                break
            time = capture.get(cv2.CAP_PROP_POS_MSEC) / 1000
            if time > end + .5 / fps:
                break
            yield time, image

    try:
        result = track_frames(frames(), region, max_width)
        rows = result.get('samples', [])
        if result['status'] == 'measured' and (rows[0]['time'] > start + 1 / fps or rows[-1]['time'] < end - 1 / fps):
            result.update(status='unresolved', reason='Decoded samples do not cover the requested interval.')
        return {**result, 'width': width, 'height': height, 'fps': fps, 'roi': region}
    finally:
        capture.release()


def suppression_warning(reference, output):
    import numpy as np

    if reference['status'] != 'measured' or output['status'] != 'measured':
        return None
    a = np.linalg.norm(np.array(reference['spanPx']) / [reference['width'], reference['height']])
    b = np.linalg.norm(np.array(output['spanPx']) / [output['width'], output['height']])
    return bool(a > .003 and b < a * .5)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('reference', type=Path)
    parser.add_argument('output', type=Path, nargs='?', help='Output video. Omit it to observe source motion before authoring.')
    parser.add_argument('--start', type=float, required=True)
    parser.add_argument('--end', type=float, required=True)
    parser.add_argument('--roi', type=rectangle, help='Reference region in original pixels.')
    parser.add_argument('--output-roi', type=rectangle, help='Output region in its original pixels. Supply this when --roi needs different output coordinates.')
    parser.add_argument('--max-width', type=int, default=640)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    try:
        import numpy as np
        import cv2
    except ImportError:
        parser.exit(2, 'Run this helper through node vision-tools.mjs register or measure to prepare its managed Python dependencies.\n')
    if not np.isfinite([args.start, args.end]).all() or args.start < 0 or args.end <= args.start or args.max_width < 64:
        parser.error('Use finite times with 0 <= start < end and --max-width of at least 64.')
    if args.output is None and args.output_roi is not None:
        parser.error('--output-roi requires an output video.')
    reference = measure_video(args.reference, args.start, args.end, args.roi, args.max_width)
    report = {'reference': reference, 'output': None, 'comparisonPerformed': False, 'possibleSuppressedMotion': None,
              'limits': 'Source-only observations require an output comparison after rendering. Comparisons use corresponding continuous intervals on the same clock. Select a region belonging to the feature being checked. Mixed stationary and moving content, occlusion, material changes and uncertain tracking need visual review. Object identity and semantic fidelity require visual inspection.'}
    summary = {'output': str(args.out), 'referenceStatus': reference['status'], 'outputStatus': None,
               'referenceSpanPx': reference.get('spanPx'), 'outputSpanPx': None,
               'comparisonPerformed': False, 'possibleSuppressedMotion': None}
    failed = reference['status'] != 'measured'
    if args.output is not None:
        output = measure_video(args.output, args.start, args.end, args.output_roi or args.roi, args.max_width)
        warning = suppression_warning(reference, output)
        report.update(output=output, comparisonPerformed=True, possibleSuppressedMotion=warning)
        summary.update(outputStatus=output['status'], outputSpanPx=output.get('spanPx'),
                       comparisonPerformed=True, possibleSuppressedMotion=warning)
        failed = failed or output['status'] != 'measured' or warning is True
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(summary))
    return 2 if failed else 0


if __name__ == '__main__':
    raise SystemExit(main())
