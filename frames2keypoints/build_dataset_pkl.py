"""Combine per-video keypoint .pkl files (from extract_keypoints_rtmpose.py) with
the official PHOENIX-2014T gloss/text annotations into one split-level pickle,
in the exact schema model/baseline-MSKA/datasets.py:S2T_Dataset expects:

    { video_name: {"name": str, "gloss": str, "text": str,
                   "num_frames": int, "keypoint": np.ndarray[T,133,3]} , ... }

load_annotations() parses the official RWTH-PHOENIX-2014-T annotation file,
named PHOENIX-2014-T.{split}.corpus.csv in the release's annotations/manual/
directory: a "|"-delimited CSV with a header row and columns
name|video|start|end|speaker|orth|translation, where "orth" is the gloss
sequence and "translation" is the German sentence. The "video" column looks
like "01April_2010_Thursday_heute-6698/1/*.png" (a camera-view index and a
frame-image glob tacked onto the plain video folder name) -- verified against
the dataset's HuggingFace `datasets` loading script rather than assumed.
"""
import argparse
import csv
import glob
import os
import pickle


def load_annotations(annotation_path, split):
    """Return {video_name: {"gloss": str, "text": str}}, with video_name
    normalized to "{split}/{video_folder_name}" to match this project's
    existing naming convention (see data/results.json, data/reg_results.json)."""
    annotations = {}
    with open(annotation_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="|", quoting=csv.QUOTE_NONE)
        for row in reader:
            base_name = row["video"].split("/1/")[0]
            video_name = base_name if base_name.startswith(f"{split}/") else f"{split}/{base_name}"
            annotations[video_name] = {"gloss": row["orth"], "text": row["translation"]}
    return annotations


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--keypoints-dir", required=True, help="output dir from extract_keypoints_rtmpose.py")
    parser.add_argument("--annotation-path", required=True,
                         help="e.g. annotations/manual/PHOENIX-2014-T.train.corpus.csv")
    parser.add_argument("--split", required=True, choices=["train", "dev", "test"])
    parser.add_argument("--out-path", required=True, help="e.g. data/Phoenix-2014T/Phoenix-2014T.train")
    args = parser.parse_args()

    annotations = load_annotations(args.annotation_path, args.split)

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
