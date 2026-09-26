"""Extract 133-point COCO-WholeBody keypoints from per-video frame folders using
MMPose, as a drop-in replacement for the deleted HRNet-based extraction stage.

Requires (on the Colab/GPU machine that runs this, not in this sandbox):
    pip install mmengine mmcv mmdet mmpose

Frame layout expected (matches the official PHOENIX-2014T release and this
project's own frame-serving convention, e.g. backend/controllers/videoToFramesController.js):
    <frames_root>/<video_name>/images0001.png, images0002.png, ...

Usage:
    python extract_keypoints_rtmpose.py \
        --frames-root data/Phoenix-2014T/frames \
        --out-dir data/Phoenix-2014T/keypoints \
        --pose2d wholebody

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

import numpy as np
import torch


def list_frame_paths(video_dir):
    names = sorted(f for f in os.listdir(video_dir) if f.lower().endswith((".png", ".jpg", ".jpeg")))
    return [os.path.join(video_dir, f) for f in names]


def extract_video_keypoints(inferencer, frame_paths):
    """Returns an (T, 133, 3) float32 array: [:, :, :2]=xy, [:, :, 2]=confidence."""
    T = len(frame_paths)
    keypoints = np.zeros((T, 133, 3), dtype=np.float32)
    last_valid = None
    for t, frame_path in enumerate(frame_paths):
        result_generator = inferencer(frame_path)
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
    parser.add_argument("--frames-root", required=True)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--pose2d", default="wholebody",
                         help="MMPose alias (e.g. 'wholebody') or explicit config path for RTMW")
    args = parser.parse_args()

    from mmpose.apis import MMPoseInferencer  # imported lazily: only needed on the GPU machine
    inferencer = MMPoseInferencer(pose2d=args.pose2d)

    os.makedirs(args.out_dir, exist_ok=True)
    video_names = sorted(d for d in os.listdir(args.frames_root)
                          if os.path.isdir(os.path.join(args.frames_root, d)))

    for video_name in video_names:
        video_dir = os.path.join(args.frames_root, video_name)
        frame_paths = list_frame_paths(video_dir)
        if not frame_paths:
            print(f"skip {video_name}: no frames found")
            continue
        keypoints = extract_video_keypoints(inferencer, frame_paths)

        out_path = os.path.join(args.out_dir, f"{video_name.replace('/', '-')}.pkl")
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with open(out_path, "wb") as f:
            # stored as (T, J, C); S2T_Dataset.__getitem__ does .permute(2, 0, 1) -> (C, T, J),
            # and it calls .permute() directly, so this must be a torch.Tensor, not a numpy array
            pickle.dump({"name": video_name, "num_frames": keypoints.shape[0],
                         "keypoint": torch.from_numpy(keypoints)}, f)
        print(f"{video_name}: {keypoints.shape[0]} frames -> {out_path}")


if __name__ == "__main__":
    main()
