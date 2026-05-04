"""Orquestração do pipeline end-to-end."""
from __future__ import annotations
import argparse
from . import data_ingestion, preprocessing, evaluate, register
from .model import download_model


STAGES = ["ingest", "preprocess", "download_model", "register", "evaluate", "all"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", choices=STAGES, default="all")
    ap.add_argument("--split", default="test")
    args = ap.parse_args()

    if args.stage in ("ingest", "all"):
        print("==> ingest")
        data_ingestion.build_index()
    if args.stage in ("preprocess", "all"):
        print("==> preprocess")
        preprocessing.run()
    if args.stage in ("download_model", "all"):
        print("==> download_model")
        download_model()
    if args.stage in ("register", "all"):
        print("==> register")
        register.run()
    if args.stage in ("evaluate", "all"):
        print("==> evaluate")
        evaluate.run(split=args.split)


if __name__ == "__main__":
    main()
