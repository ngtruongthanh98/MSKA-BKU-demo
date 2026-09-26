"""Build a single-video src_input.pkl for the live demo's inference path
(sign-language-translator/mska_translator.py expects one at
frames2keypoints/<video_name>/src_input.pkl).

train.py's evaluate_one_item() passes this pickle straight into model(src_input),
so it must be the fully collated batch dict S2T_Dataset.collate_fn() produces
(padded/masked keypoints, tokenized gloss_input, tokenized translation_inputs)
-- not just a raw keypoint tensor. Rather than reimplementing that tokenization/
padding/masking by hand and risking a subtle mismatch, this script builds a
one-entry dataset file and runs it through the project's own S2T_Dataset and
collate_fn, so it's exercising the exact same tested code path training uses.

Usage:
    python build_src_input.py \
        --video-name test/03February_2010_Wednesday_heute-2356 \
        --frames-dir /path/to/frames/for/this/one/video \
        --config ../model/baseline-MSKA/configs/phoenix-2014t_s2t.yaml \
        --out-dir .. \
        --pose2d wholebody

Must run in the same environment as the rest of the demo: baseline-MSKA's
GlossTokenizer/TextTokenizer need configs/*.yaml, data/*/gloss2ids.pkl, and
pretrained_models/mBart_de to already be in place, same as running
train.py --eval directly -- this script doesn't add any new dependency on
top of what the demo already requires.
"""
import argparse
import os
import pickle
import sys

import yaml

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "model", "baseline-MSKA"))
from Tokenizer import GlossTokenizer_S2G  # noqa: E402
from datasets import S2T_Dataset  # noqa: E402

from extract_keypoints_rtmpose import list_frame_paths, extract_video_keypoints  # noqa: E402

# Placeholder gloss/text: at pure inference time there's no ground truth to put
# here, and model(src_input) still needs translation_inputs of the right shape
# (it computes a translation loss during forward() even though we only care
# about generate_txt()'s output afterwards). A single-token placeholder --
# rather than "" -- avoids the zero-length edge case in GlossTokenizer_S2G's
# and TextTokenizer's batch padding.
PLACEHOLDER_GLOSS = "unk"
PLACEHOLDER_TEXT = "unk"


def build_single_sample_dataset_file(video_name, keypoint_tensor, num_frames, tmp_path):
    sample = {
        video_name: {
            "name": video_name,
            "gloss": PLACEHOLDER_GLOSS,
            "text": PLACEHOLDER_TEXT,
            "num_frames": num_frames,
            "keypoint": keypoint_tensor,
        }
    }
    with open(tmp_path, "wb") as f:
        pickle.dump(sample, f)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--video-name", required=True, help='e.g. "test/03February_2010_Wednesday_heute-2356"')
    parser.add_argument("--frames-dir", required=True, help="directory of this one video's frame images")
    parser.add_argument("--config", required=True, help="e.g. ../model/baseline-MSKA/configs/phoenix-2014t_s2t.yaml")
    parser.add_argument("--out-dir", default="..", help="src_input.pkl is written to <out-dir>/<video_name>/")
    parser.add_argument("--pose2d", default="wholebody",
                         help="MMPose alias (e.g. 'wholebody') or explicit config path for RTMW")
    args = parser.parse_args()

    with open(args.config, "r+", encoding="utf-8") as f:
        config = yaml.load(f, Loader=yaml.FullLoader)

    import torch
    from mmpose.apis import MMPoseInferencer  # imported lazily: only needed on the GPU machine

    inferencer = MMPoseInferencer(pose2d=args.pose2d)
    frame_paths = list_frame_paths(args.frames_dir)
    if not frame_paths:
        raise FileNotFoundError(f"no frames found in {args.frames_dir}")
    keypoints = extract_video_keypoints(inferencer, frame_paths)
    keypoint_tensor = torch.from_numpy(keypoints)

    tmp_pkl = os.path.join(args.out_dir, f".tmp_{args.video_name.replace('/', '-')}.pkl")
    build_single_sample_dataset_file(args.video_name, keypoint_tensor, keypoints.shape[0], tmp_pkl)
    try:
        tokenizer = GlossTokenizer_S2G(config["gloss"])
        dataset = S2T_Dataset(path=tmp_pkl, tokenizer=tokenizer, config=config,
                               args=argparse.Namespace(), phase="test")
        src_input = dataset.collate_fn([dataset[0]])
    finally:
        os.remove(tmp_pkl)

    out_dir = os.path.join(args.out_dir, args.video_name)
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "src_input.pkl")
    with open(out_path, "wb") as f:
        pickle.dump(src_input, f)
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
