"""Extract 133-point COCO-WholeBody keypoints from per-video frame folders using
MMPose, as a drop-in replacement for the deleted HRNet-based extraction stage.

Requires (on the Colab/GPU machine that runs this, not in this sandbox):
    pip install mmengine mmcv mmdet mmpose

Frame layout expected (matches the official PHOENIX-2014T release and this
project's own frame-serving convention, e.g. backend/controllers/videoToFramesController.js):
    <frames_root>/<video_name>/images0001.png, images0002.png, ...

Usage:
    python extract_keypoints_rtmpose.py \
        --frames-root data/Phoenix-2014T/frames/test \
        --split test \
        --out-dir data/Phoenix-2014T/keypoints \
        --pose2d wholebody

Output sample names are prefixed "{split}/{video_name}" to match this
project's existing convention (data/results.json, data/reg_results.json) and
what build_dataset_pkl.py's annotation parser produces.

--pose2d accepts either the documented, version-stable MMPose alias
"wholebody" (-> rtmpose-m, ~65 AP on COCO-WholeBody, safe default) or an
explicit config path if you want the stronger RTMW-l/x checkpoints (~70 AP).
Check the current config/checkpoint names in MMPose's model zoo before
passing a custom path -- exact filenames change across MMPose releases:
https://mmpose.readthedocs.io/en/latest/model_zoo/wholebody_2d_keypoint.html
"""
import argparse
import os
import pickle
import tempfile

import numpy as np
import torch
from PIL import Image

# PHOENIX-2014T's native frame resolution. S2T_Dataset.augment_preprocess_inputs
# divides keypoint x/y coordinates by exactly these numbers (self.w, self.h) to
# normalize them, so keypoints must be extracted in that same pixel space -- a
# frame at any other resolution silently mis-normalizes (doesn't error, just
# feeds the model coordinates in the wrong range). The official PHOENIX-2014T
# frames already are this size, so resizing to it is a no-op there; it's
# required for any other video, e.g. a live demo upload, which will essentially
# never already be 210x260.
TARGET_FRAME_SIZE = (210, 260)  # (width, height)


def list_frame_paths(video_dir):
    names = sorted(f for f in os.listdir(video_dir) if f.lower().endswith((".png", ".jpg", ".jpeg")))
    return [os.path.join(video_dir, f) for f in names]


def resize_frame(frame_path, out_path, size=TARGET_FRAME_SIZE):
    with Image.open(frame_path) as img:
        img.convert("RGB").resize(size, Image.BILINEAR).save(out_path)


def extract_video_keypoints(inferencer, frame_paths, target_size=TARGET_FRAME_SIZE):
    """Returns an (T, 133, 3) float32 array: [:, :, :2]=xy, [:, :, 2]=confidence."""
    T = len(frame_paths)
    keypoints = np.zeros((T, 133, 3), dtype=np.float32)
    last_valid = None
    with tempfile.TemporaryDirectory() as tmp_dir:
        for t, frame_path in enumerate(frame_paths):
            resized_path = os.path.join(tmp_dir, f"{t:06d}.png")
            resize_frame(frame_path, resized_path, target_size)

            result_generator = inferencer(resized_path)
            result = next(result_generator)
            instances = result["predictions"][0]
            if not instances:
                # no person detected in this frame: carry forward the last valid pose
                # rather than zeroing it out, since a dropped detection is far more
                # likely than the signer actually vanishing from a weather-forecast clip
                if last_valid is not None:
                    keypoints[t] = last_valid
                continue
            best = max(instances, key=lambda inst: float(np.mean(inst["keypoint_scores"])))
            xy = np.asarray(best["keypoints"], dtype=np.float32)         # (133, 2)
            scores = np.asarray(best["keypoint_scores"], dtype=np.float32)  # (133,)
            frame_kp = np.concatenate([xy, scores[:, None]], axis=1)     # (133, 3)
            keypoints[t] = frame_kp
            last_valid = frame_kp
    return keypoints


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--frames-root", required=True,
                         help="directory containing one subfolder of frames per video, for this split only")
    parser.add_argument("--split", required=True, choices=["train", "dev", "test"])
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--pose2d", default="wholebody",
                         help="MMPose alias (e.g. 'wholebody') or explicit config path for RTMW")
    args = parser.parse_args()

    from mmpose.apis import MMPoseInferencer  # imported lazily: only needed on the GPU machine
    inferencer = MMPoseInferencer(pose2d=args.pose2d)

    os.makedirs(args.out_dir, exist_ok=True)
    folder_names = sorted(d for d in os.listdir(args.frames_root)
                           if os.path.isdir(os.path.join(args.frames_root, d)))

    for folder_name in folder_names:
        video_name = f"{args.split}/{folder_name}"
        video_dir = os.path.join(args.frames_root, folder_name)
        frame_paths = list_frame_paths(video_dir)
        if not frame_paths:
            print(f"skip {video_name}: no frames found")
            continue
        keypoints = extract_video_keypoints(inferencer, frame_paths)

        out_path = os.path.join(args.out_dir, f"{folder_name}.pkl")
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with open(out_path, "wb") as f:
            # stored as (T, J, C); S2T_Dataset.__getitem__ does .permute(2, 0, 1) -> (C, T, J),
            # and it calls .permute() directly, so this must be a torch.Tensor, not a numpy array
            pickle.dump({"name": video_name, "num_frames": keypoints.shape[0],
                         "keypoint": torch.from_numpy(keypoints)}, f)
        print(f"{video_name}: {keypoints.shape[0]} frames -> {out_path}")


if __name__ == "__main__":
    main()
