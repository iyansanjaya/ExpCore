"""Mesin pemroses ExpCore yang dijalankan aplikasi Electron, satu proses per pekerjaan.

stdout hanya berisi protokol, satu objek JSON per baris:
  {"event": "log", "message": str}
  {"event": "progress", "done": int, "total": int}
  {"event": "done", "path": str | null, "summary": str}   -> exit 0
  {"event": "error", "message": str}                       -> exit 1
Argumen tidak valid -> exit 2 tanpa protokol. Keluaran lain (traceback, print pustaka) ke stderr.
"""

import argparse
import json
import sys
import traceback

JOBS = {
    "bupot": "process_bupot",
    "bupot2024": "process_bupot_2024",
    "pm": "process_pm",
    "rename": "process_rename_bupot",
}


def main(argv=None):
    parser = argparse.ArgumentParser(prog="expcore_engine")
    parser.add_argument("job", choices=JOBS)
    parser.add_argument("folder")
    parser.add_argument("--apply", action="store_true", help="terapkan nama baru (khusus rename)")
    args = parser.parse_args(argv)
    if args.apply and args.job != "rename":
        parser.error("--apply hanya berlaku untuk rename")

    protocol = sys.stdout
    sys.stdout = sys.stderr  # print() dari pustaka tidak boleh mencemari protokol.

    def emit(event, **data):
        # ensure_ascii (bawaan) menjaga keluaran tetap ASCII, aman dari code page Windows.
        protocol.write(json.dumps({"event": event, **data}) + "\n")
        protocol.flush()

    try:
        from ExpCore import ExpCore  # Modul hilang pada build ikut dilaporkan sebagai error.

        engine = ExpCore(log=lambda message: emit("log", message=message),
                         progress=lambda done, total: emit("progress", done=done, total=total))
        method = getattr(engine, JOBS[args.job])
        if args.job == "rename":
            path, summary = method(args.folder, apply_changes=args.apply)
        else:
            path, summary = method(args.folder)
    except Exception as error:
        traceback.print_exc()
        emit("error", message=str(error) or type(error).__name__)
        return 1
    emit("done", path=path, summary=summary)
    return 0


if __name__ == "__main__":
    sys.exit(main())
