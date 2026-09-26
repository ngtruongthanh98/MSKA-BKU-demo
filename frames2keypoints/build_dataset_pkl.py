"""Combine per-video keypoint .pkl files (from extract_keypoints_rtmpose.py) with
the official PHOENIX-2014T gloss/text annotations into one split-level pickle,
in the exact schema model/baseline-MSKA/datasets.py:S2T_Dataset expects:

    { video_name: {"name": str, "gloss": str, "text": str,
                   "num_frames": int, "keypoint": np.ndarray[T,133,3]} , ... }

load_annotations() below is a STUB: PHOENIX-2014T's official annotation file
format was not verified against this repo's actual data, so plug in your own
parser for whatever annotation file the release gives you (an
"id|name|...|annotation"-style delimited file per the RWTH-PHOENIX-2014-T
release) rather than trusting a hardcoded column layout here.
"""
import argparse
import glob
import os
import pickle


def load_annotations(annotation_path):
    """Return {video_name: {"gloss": str, "text": str}}.

    Replace this with a real parser for your annotation file -- format not
    verified here, see module docstring.
    """
    raise NotImplementedError(
        "Plug in a parser for your PHOENIX-2014T annotation file: "
        f"{annotation_path} -> {{video_name: {{'gloss': ..., 'text': ...}}}}"
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--keypoints-dir", required=True, help="output dir from extract_keypoints_rtmpose.py")
    parser.add_argument("--annotation-path", required=True)
    parser.add_argument("--out-path", required=True, help="e.g. data/Phoenix-2014T/Phoenix-2014T.train")
    args = parser.parse_args()

    annotations = load_annotations(args.annotation_path)

    dataset = {}
    for kp_path in sorted(glob.glob(os.path.join(args.keypoints_dir, "*.pkl"))):
        with open(kp_path, "rb") as f:
            sample = pickle.load(f)
        video_name = sample["name"]
        if video_name not in annotations:
            print(f"skip {video_name}: no annotation found")
            continue
        ann = annotations[video_name]
        dataset[video_name] = {
            "name": video_name,
            "gloss": ann["gloss"],
            "text": ann["text"],
            "num_frames": sample["num_frames"],
            "keypoint": sample["keypoint"],
        }

    with open(args.out_path, "wb") as f:
        pickle.dump(dataset, f)
    print(f"wrote {len(dataset)} samples -> {args.out_path}")


if __name__ == "__main__":
    main()
