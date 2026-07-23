from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DB_PATH = Path("data/generation_history.db")


def init_db() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS generations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,

                product_description TEXT NOT NULL,
                style TEXT NOT NULL,
                background TEXT NOT NULL,
                lighting TEXT NOT NULL,
                camera_angle TEXT NOT NULL,
                aspect_ratio TEXT NOT NULL,
                extra_details TEXT NOT NULL,

                prompt TEXT NOT NULL,
                negative_prompt TEXT NOT NULL,

                seed INTEGER NOT NULL,
                steps INTEGER NOT NULL,
                cfg REAL NOT NULL,

                width INTEGER NOT NULL,
                height INTEGER NOT NULL,
                image_count INTEGER NOT NULL,

                generation_time REAL,

                backend TEXT NOT NULL,
                status TEXT NOT NULL,

                images_json TEXT NOT NULL
            )
            """
        )


def save_generation(record: dict[str, Any]) -> int:
    init_db()

    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.execute(
            """
            INSERT INTO generations (
                created_at,
                product_description,
                style,
                background,
                lighting,
                camera_angle,
                aspect_ratio,
                extra_details,
                prompt,
                negative_prompt,
                seed,
                steps,
                cfg,
                width,
                height,
                image_count,
                generation_time,
                backend,
                status,
                images_json
            )
            VALUES (
                ?,?,?,?,?,?,?,?,?,?,
                ?,?,?,?,?,?,?,?,?,?
            )
            """,
            (
                datetime.now(timezone.utc).isoformat(),
                record["product_description"],
                record["style"],
                record["background"],
                record["lighting"],
                record["camera_angle"],
                record["aspect_ratio"],
                record["extra_details"],
                record["prompt"],
                record["negative_prompt"],
                record["seed"],
                record["steps"],
                record["cfg"],
                record["width"],
                record["height"],
                record["image_count"],
                record.get("generation_time"),
                record["backend"],
                record["status"],
                json.dumps(record.get("images", [])),
            ),
        )

        return int(cur.lastrowid)


def list_generations(limit: int = 30) -> list[dict[str, Any]]:
    init_db()

    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row

        rows = conn.execute(
            """
            SELECT *
            FROM generations
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()

    generations: list[dict[str, Any]] = []

    for row in rows:
        generation = dict(row)

        generation["images"] = json.loads(generation.pop("images_json"))

        generations.append(generation)

    return generations
