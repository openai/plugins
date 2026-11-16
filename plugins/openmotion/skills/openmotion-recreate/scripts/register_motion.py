"""Measure a planar reference region in original pixel coordinates.

Run through vision-tools.mjs for pinned Python, NumPy and OpenCV. This reads reference frames and
writes observation data. The maker still chooses material, geometry and edits.
"""

import argparse
import json
from pathlib import Path


def estimate_transform(anchor, current, roi, excluded=(), max_width=960):
    import cv2
    import numpy as np

    x, y, width, height = roi
    scale = min(1.0, max_width / width)
    size = (round(width * scale), round(height * scale))
    if min(size) < 2:
        return {'status': 'unresolved', 'reason': 'The selected region is too small for feature registration after resizing.'}
    coordinate_scale = np.array([size[0] / width, size[1] / height])
    images = [cv2.resize(image[y:y + height, x:x + width], size)
              for image in [anchor, current]]
    mask = np.full((size[1], size[0]), 255, np.uint8)
    for left, top, box_width, box_height in excluded:
        x0, y0 = round((left - x) * scale), round((top - y) * scale)
        x1, y1 = round((left + box_width - x) * scale), round((top + box_height - y) * scale)
        mask[max(0, y0):max(0, min(size[1], y1)), max(0, x0):max(0, min(size[0], x1))] = 0
    detector = cv2.ORB_create(nfeatures=6000, fastThreshold=10)
    features = [detector.detectAndCompute(cv2.cvtColor(image, cv2.COLOR_BGR2GRAY), mask)
                for image in images]
    if any(descriptors is None for _, descriptors in features):
        return {'status': 'unresolved', 'reason': 'No recoverable features in the selected region.'}
    (keys_a, descriptors_a), (keys_b, descriptors_b) = features
    pairs = cv2.BFMatcher(cv2.NORM_HAMMING).knnMatch(descriptors_a, descriptors_b, k=2)
    matches = [pair[0] for pair in pairs if len(pair) == 2 and pair[0].distance < .75 * pair[1].distance]
    if len(matches) < 12:
        return {'status': 'unresolved', 'reason': 'Fewer than 12 distinctive matches.', 'matches': len(matches)}
    # Convert local, resized feature coordinates before fitting. Matrices and
    # residuals therefore use original full-frame pixels, including the ROI offset.
    origin = np.array([x, y], dtype=float)
    points_a = np.float32([keys_a[match.queryIdx].pt for match in matches]) / coordinate_scale + origin
    points_b = np.float32([keys_b[match.trainIdx].pt for match in matches]) / coordinate_scale + origin
    matrix, selected = cv2.findHomography(points_a, points_b, cv2.RANSAC, 3 / scale,
                                         maxIters=5000, confidence=.995)
    if matrix is None or selected is None or not np.isfinite(matrix).all() or abs(matrix[2, 2]) < 1e-10:
        return {'status': 'unresolved', 'reason': 'A finite projective transform could not be fitted.'}
    selected = selected.ravel().astype(bool)
    inliers = int(selected.sum())
    ratio = inliers / len(matches)
    if inliers < 12 or ratio < .3:
        return {'status': 'unresolved', 'reason': 'Matches do not support one coherent plane.',
                'inliers': inliers, 'inlierRatio': ratio}
    matrix /= matrix[2, 2]
    projected = cv2.perspectiveTransform(points_a.reshape(-1, 1, 2), matrix).reshape(-1, 2)
    residuals = np.linalg.norm(projected[selected] - points_b[selected], axis=1)
    corners = np.float32([[x, y], [x + width, y], [x + width, y + height], [x, y + height]])
    denominator = corners @ matrix[2, :2] + matrix[2, 2]
    transformed = cv2.perspectiveTransform(corners.reshape(-1, 1, 2), matrix).reshape(-1, 2)
    if (np.min(denominator) * np.max(denominator) <= 0 or not np.isfinite(transformed).all()
            or not cv2.isContourConvex(transformed.astype('float32'))):
        return {'status': 'unresolved', 'reason': 'The fitted region folds or crosses a projection singularity.'}
    support = cv2.contourArea(cv2.convexHull(points_a[selected].astype('float32'))) / (width * height)
    indices = np.flatnonzero(selected)
    indices = indices[np.linspace(0, len(indices) - 1, min(24, len(indices))).astype(int)]
    return {
        'status': 'measured', 'anchorToFrame': matrix.tolist(),
        'matches': len(matches), 'inliers': inliers, 'inlierRatio': ratio,
        'medianResidualPx': float(np.median(residuals)), 'p95ResidualPx': float(np.percentile(residuals, 95)),
        'supportAreaRatio': float(support), 'projectedRegionCorners': transformed.tolist(),
        'pointPairs': [{'anchor': points_a[index].tolist(), 'frame': points_b[index].tolist()}
                       for index in indices],
    }


def rectangle(value):
    try:
        values = [int(part) for part in value.split(',')]
        if len(values) != 4 or min(values[:2]) < 0 or min(values[2:]) <= 0:
            raise ValueError()
        return values
    except ValueError:
        raise argparse.ArgumentTypeError('Use x,y,width,height with nonnegative origin and positive dimensions.') from None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('video', type=Path)
    parser.add_argument('--anchor', type=float, required=True, help='Anchor time in seconds.')
    parser.add_argument('--times', required=True, help='Comma-separated observation times in seconds.')
    parser.add_argument('--roi', type=rectangle, help='Planar region in original pixels. Defaults to the full frame.')
    parser.add_argument('--exclude', type=rectangle, action='append', default=[], help='Screen-space overlay box to exclude in every sample. Repeatable.')
    parser.add_argument('--max-width', type=int, default=960)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    try:
        import cv2
        import numpy as np
    except ImportError:
        parser.exit(2, 'Run this helper through node vision-tools.mjs register or measure to prepare its managed Python dependencies.\n')
    try:
        times = sorted(set(float(value) for value in args.times.split(',')))
    except ValueError:
        parser.error('Observation times must be numbers.')
    if not times or min(times + [args.anchor]) < 0 or not np.isfinite(times + [args.anchor]).all() or args.max_width < 64:
        parser.error('Use finite nonnegative times and --max-width of at least 64.')
    capture = cv2.VideoCapture(str(args.video))
    if not capture.isOpened():
        parser.error('The reference video could not be opened.')
    fps = capture.get(cv2.CAP_PROP_FPS)
    width, height = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH)), int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
    if not np.isfinite(fps) or fps <= 0 or min(width, height) <= 0:
        parser.error('The reference has no usable frame geometry or frame rate.')
    roi = args.roi or [0, 0, width, height]
    if roi[0] + roi[2] > width or roi[1] + roi[3] > height:
        parser.error('The selected region extends outside the reference frame.')

    def read(time):
        index = round(time * fps)
        capture.set(cv2.CAP_PROP_POS_FRAMES, index)
        ok, image = capture.read()
        if not ok:
            raise ValueError(f'Frame at requested time {time} could not be decoded.')
        return image, {'requestedTime': time, 'frame': int(capture.get(cv2.CAP_PROP_POS_FRAMES)) - 1,
                       'decodedTime': capture.get(cv2.CAP_PROP_POS_MSEC) / 1000}

    try:
        anchor, anchor_identity = read(args.anchor)
        samples = []
        for time in times:
            image, identity = read(time)
            samples.append({**identity, **estimate_transform(anchor, image, roi, args.exclude, args.max_width)})
    except ValueError as error:
        parser.exit(2, str(error) + '\n')
    finally:
        capture.release()
    report = {
        'video': str(args.video.resolve()), 'width': width, 'height': height, 'fps': fps,
        'anchor': anchor_identity, 'roi': roi, 'excluded': args.exclude,
        'coordinates': 'Original full-frame pixels. anchorToFrame maps anchor points to each observed frame.',
        'limits': 'One planar region. Inspect inlier coverage and intermediate output. Parallax, deformation, cuts and moving overlays can invalidate this model. Frame selection uses the reported rate; decoded timestamps identify the actual samples.',
        'samples': samples,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + '\n')
    unresolved = sum(sample['status'] != 'measured' for sample in samples)
    print(json.dumps({'output': str(args.out), 'samples': len(samples), 'unresolved': unresolved}))
    return 2 if unresolved else 0


if __name__ == '__main__':
    raise SystemExit(main())
