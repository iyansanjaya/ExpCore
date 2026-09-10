"""Desktop smoke checks. Run with a working Tcl/Tk installation; no source PDFs change."""

import tempfile
import sys
import threading
import time
from pathlib import Path
from unittest.mock import patch

import customtkinter as ctk
from ExpCore import ExpCore
from expcore_updates import APP_VERSION, RELEASES_URL, UpdateResult


def check_scrolling(app):
    app.geometry("960x620")
    for key in app.pages:
        app._navigate(key)
        app.update()
        scroll = app._scrolls[key]
        canvas = scroll._parent_canvas
        canvas.yview_moveto(0)
        assert canvas.bbox("all")[3] > canvas.winfo_height(), key
        assert canvas.cget("scrollregion"), f"{key}: missing scrollregion"
        # Generate input on the actual widget, not a direct call to yview/handler.
        targets = [app.hero_title._label, *(card._canvas for card in app._home_cards)] if key == "home" else [
            app._views[key]["browse"]._canvas, app._views[key]["entry"]._entry,
            app._views[key]["status"]._label, app._views[key]["summary"]._label,
        ]
        for target in targets:
            hidden_positions = {name: frame._parent_canvas.yview() for name, frame in app._scrolls.items() if name != key}
            target.event_generate("<MouseWheel>", delta=-120)
            app.update()
            assert canvas.yview()[0] > 0, f"{key}: mouse wheel did not scroll {target}"
            target.event_generate("<MouseWheel>", delta=120)
            app.update()
            assert canvas.yview()[0] == 0, f"{key}: upward wheel did not return to top"
            assert hidden_positions == {name: app._scrolls[name]._parent_canvas.yview() for name in hidden_positions}
        # The scrollbar itself must work, not only programmatic scrolling.
        bar = scroll._scrollbar._canvas
        bar.event_generate("<Button-1>", x=bar.winfo_width() // 2, y=bar.winfo_height() - 5)
        app.update()
        assert canvas.yview()[0] > 0, f"{key}: scrollbar click failed"
        bar.event_generate("<ButtonRelease-1>")
        canvas.yview_moveto(0)
        app.nav[key]._canvas.focus_force()
        app.nav[key]._canvas.event_generate("<Next>")
        app.update()
        assert canvas.yview()[0] > 0, f"{key}: Page Down failed"
        app.nav[key]._canvas.event_generate("<Prior>")
        app.update()
        assert canvas.yview()[0] == 0, f"{key}: Page Up failed"
        if key != "home":
            box = app._views[key]["log"]
            # A short/empty log must not trap wheel input meant for the page.
            box._textbox.event_generate("<MouseWheel>", delta=-120)
            app.update()
            assert canvas.yview()[0] > 0, f"{key}: empty log trapped scroll"
            canvas.yview_moveto(0)
            box._canvas.event_generate("<MouseWheel>", delta=-120)
            app.update()
            assert canvas.yview()[0] > 0, f"{key}: log padding trapped scroll"
            box.configure(state="normal")
            box.insert("end", "\n" + "A log line for scrolling\n" * 80)
            box.configure(state="disabled")
            box.yview_moveto(0)
            canvas.yview_moveto(0)
            app.update()
            box._textbox.event_generate("<MouseWheel>", delta=-120)
            app.update()
            assert box.yview()[0] > 0, f"{key}: long log did not scroll"
            assert canvas.yview()[0] == 0, f"{key}: log and page scrolled together"
            box.yview_moveto(1)
            box._textbox.event_generate("<MouseWheel>", delta=-120)
            app.update()
            assert canvas.yview()[0] > 0, f"{key}: end of log trapped scroll"
            box.configure(state="normal")
            box.delete("1.0", "end")
            box.configure(state="disabled")
            canvas.yview_moveto(0)
    print("Scroll: wheel, child controls, scrollbar, Page Up/Down and nested logs OK on all five pages")


def wait_for(app, predicate, timeout=8):
    deadline = time.monotonic() + timeout
    while not predicate():
        assert time.monotonic() < deadline, "UI/worker did not finish within timeout"
        app.update()
        time.sleep(0.01)
    app.update()


def check_updates(app):
    started, release = threading.Event(), threading.Event()
    worker_threads = []
    ui_thread = threading.get_ident()

    def check(force=False):
        worker_threads.append(threading.get_ident())
        started.set()
        assert release.wait(3)
        return UpdateResult("available", "v1.7.0")

    with patch.object(app._update_checker, "check", side_effect=check) as worker, \
            patch("expcore_ui.messagebox.showinfo") as info, patch("expcore_ui.messagebox.showwarning") as warning:
        app._start_update_check()
        wait_for(app, started.is_set)
        assert app.update_check_button.cget("state") == "disabled"
        app._start_update_check(True)
        assert worker.call_count == 1, "Concurrent update checks must be coalesced"
        app._navigate("pm")
        app.update()
        assert app._current == "pm" and app._busy is None
        release.set()
        wait_for(app, lambda: not app._update_checking)
        info.assert_not_called()
        warning.assert_not_called()
    assert worker_threads == [worker_threads[0]] and worker_threads[0] != ui_thread
    assert app.update_banner.winfo_ismapped()
    assert APP_VERSION in app.update_notice.cget("text")
    assert app.update_check_button.cget("state") == "normal"
    for size in ("960x620", "1180x800"):
        app.geometry(size)
        app.update()
        assert app.update_download.winfo_rootx() + app.update_download.winfo_width() <= app.winfo_rootx() + app.winfo_width()
        assert app.update_later.winfo_rootx() + app.update_later.winfo_width() <= app.winfo_rootx() + app.winfo_width()
        assert app.update_notice.winfo_rootx() + app.update_notice.winfo_width() <= app.update_download.winfo_rootx()
        assert app.update_check_button.winfo_rootx() + app.update_check_button.winfo_width() <= app.winfo_rootx() + app.winfo_width()
        assert app._views["pm"]["run"].winfo_rooty() + app._views["pm"]["run"].winfo_height() <= app.winfo_rooty() + app.winfo_height()
    with patch("expcore_ui.webbrowser.open", return_value=True) as browser:
        app.update_download.invoke()
        browser.assert_called_once_with(f"{RELEASES_URL}/tag/v1.7.0", new=2)
    with patch("expcore_ui.webbrowser.open", return_value=False), patch("expcore_ui.messagebox.showerror") as error:
        app._open_update()
        error.assert_called_once()
    app.update_later.invoke()
    app.update()
    assert not app.update_banner.winfo_ismapped()
    # Manual checks can redisplay a dismissed notice; background failures never interrupt.
    with patch.object(app._update_checker, "check", return_value=UpdateResult("available", "v1.7.0")):
        app._start_update_check(True)
        wait_for(app, lambda: not app._update_checking)
    assert app.update_banner.winfo_ismapped()
    for result in (UpdateResult("current", "v1.6.0"), UpdateResult("unpublished"),
                   UpdateResult("pending", "v1.7.0"), UpdateResult("error", error="network")):
        with patch.object(app._update_checker, "check", return_value=result), \
                patch("expcore_ui.messagebox.showinfo") as info, patch("expcore_ui.messagebox.showwarning") as warning:
            app._start_update_check()
            wait_for(app, lambda: not app._update_checking)
            info.assert_not_called()
            warning.assert_not_called()
            app._start_update_check(True)
            wait_for(app, lambda: not app._update_checking)
            if result.status == "error":
                warning.assert_called_once()
            else:
                info.assert_called_once()
    with patch.object(app._update_checker, "check", side_effect=RuntimeError("worker failure")), \
            patch("expcore_ui.logging.exception"):
        app._start_update_check()
        wait_for(app, lambda: not app._update_checking)
    assert app.update_check_button.cget("state") == "normal"
    print("Update UI: background worker, one check at a time, banner, dismiss, official link, offline and recovery OK")


def check_update_shutdown(app):
    # The startup check is scheduled once, and closing never waits for networking.
    started, release, finished = threading.Event(), threading.Event(), threading.Event()
    def check(force=False):
        started.set()
        assert release.wait(3)
        finished.set()
        return UpdateResult("available", "v1.7.0")
    try:
        with patch.object(app._update_checker, "check", side_effect=check):
            app._start_update_check()
            wait_for(app, started.is_set)
            assert app._auto_update_id is None
            app._close()
            release.set()
            assert finished.wait(3)
    finally:
        release.set()
        if not app._closing:
            app._close()
    print("Update shutdown: scheduled check cancelled; app closes while network worker is pending")


def main():
    scale = float(sys.argv[sys.argv.index("--scale") + 1]) if "--scale" in sys.argv else 1.0
    ctk.set_widget_scaling(scale)
    ctk.set_window_scaling(scale)
    app = ExpCore()
    assert app._auto_update_id is not None
    callback_errors = []
    app.report_callback_exception = lambda *error: callback_errors.append(error)
    try:
        check_updates(app)
        check_scrolling(app)
        # Resize in both directions so stale scroll regions/reflow are detected.
        for size in ("1180x800", "960x700", "960x620", "1180x800", "960x620"):
            app.geometry(size)
            for key in app.pages:
                app._navigate(key)
                app.update()
                page = app.pages[key]
                assert page.winfo_width() > 500
                scroll = app._scrolls[key]
                canvas = scroll._parent_canvas
                region = tuple(float(v) for v in canvas.cget("scrollregion").split())
                assert region == canvas.bbox("all"), f"{key}: scroll region is stale after resizing"
                assert scroll.winfo_width() <= canvas.winfo_width() + 2, f"{key}: horizontal overflow"
                if key == "home":
                    for card in app._home_cards:
                        assert card.winfo_x() + card.winfo_width() <= card.master.winfo_width() + 2
                if key in app._views:
                    view = app._views[key]
                    button = view["run"]
                    assert button.winfo_rooty() + button.winfo_height() <= app.winfo_rooty() + app.winfo_height()
                    assert button.winfo_rootx() + button.winfo_width() <= app.winfo_rootx() + app.winfo_width()
                    assert view["log"].winfo_height() >= 120

        with tempfile.TemporaryDirectory() as folder:
            app._navigate("bupot")
            app.update()
            app._folders["bupot"].set(folder)
            view = app._views["bupot"]
            canvas = view["scroll"]._parent_canvas
            canvas.yview_moveto(0)
            view["copy"]._canvas.event_generate("<FocusIn>")
            app.update()
            assert canvas.yview()[0] > 0, "Keyboard focus should reveal controls below the fold"
            view["copy"]._canvas.focus_force()
            view["copy"]._canvas.event_generate("<Return>")
            app.update()
            assert view["copy"].cget("text") == "Disalin ✓"
            assert view["run"].cget("state") == "normal"
            app._start_task("bupot")
            wait_for(app, lambda: app._busy is None)
            assert view["status"].cget("text") == "PERLU DIPERIKSA"
            assert "Tidak ada PDF" in view["log"].get("1.0", "end")
            assert view["open"].cget("state") == "disabled"

            started, release = threading.Event(), threading.Event()
            worker_ids = []
            output = Path(folder) / "output.csv"

            def worker(path):
                worker_ids.append(threading.get_ident())
                started.set()
                assert release.wait(3)
                output.write_text("result\nok\n", encoding="utf-8")
                app.log_bupot("Dokumen uji diproses.")
                app._progress(0, 1)
                return str(output), "Selesai — 1 baris."

            with patch.object(app, "process_bupot", side_effect=worker):
                app._start_task("bupot")
                wait_for(app, started.is_set)
                assert view["run"].cget("state") == "disabled"
                assert all(v["browse"].cget("state") == "disabled" for v in app._views.values())
                app._navigate("pm")
                app.update()
                assert app._current == "pm", "Navigation must work during processing"
                with patch("expcore_ui.messagebox.showinfo") as notice:
                    app._close()
                    notice.assert_called_once()
                    assert app.winfo_exists()
                app._start_task("pm")  # A second concurrent job must not start.
                assert app._busy == "bupot"
                release.set()
                wait_for(app, lambda: app._busy is None)
            assert worker_ids == [worker_ids[0]] and worker_ids[0] != threading.get_ident()
            assert view["status"].cget("text") == "SELESAI"
            assert view["open"].cget("state") == "normal"
            with patch("expcore_ui.os.startfile") as open_file:
                app._open_output("bupot")
                open_file.assert_called_once_with(str(output))
            app._folders["bupot"].set(folder + "/changed")
            assert view["open"].cget("state") == "disabled"

            # Existing output requires explicit confirmation before a worker starts.
            app._folders["bupot"].set(folder)
            (Path(folder) / app.MODULES["bupot"]["output"]).write_bytes(b"existing result")
            with patch("expcore_ui.messagebox.askyesno", return_value=False), patch.object(app, "_run_job") as run:
                app._start_task("bupot")
                run.assert_not_called()
                assert app._busy is None

            # Rename apply is unavailable until a completed preview, and resets on folder changes.
            app._folders["rename"].set(folder)
            rename = app._views["rename"]
            assert rename["apply"].cget("state") == "disabled"
            with patch.object(app, "process_rename_bupot", return_value=(str(output), "Pratinjau selesai")):
                app._start_task("rename")
                wait_for(app, lambda: app._busy is None)
            assert rename["apply"].cget("state") == "normal"
            with patch("expcore_ui.messagebox.askyesno", return_value=False), patch.object(app, "_run_job") as run:
                app._start_task("rename", True)
                run.assert_not_called()
            app._folders["rename"].set("")
            assert rename["apply"].cget("state") == "disabled"
            assert not callback_errors, callback_errors
        print(f"Desktop UI at {scale * 100:g}%: resize/reflow, keyboard, worker isolation, error recovery and rename safeguards OK")
        check_update_shutdown(app)
    finally:
        app._busy = None
        if not app._closing:
            app._close()


if __name__ == "__main__":
    main()
