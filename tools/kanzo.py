# -*- coding: utf-8 -*-
"""Client dùng chung cho API Kanzo (hiện thực U098).

Mọi agent/tập lệnh gọi Kanzo PHẢI qua module này thay vì tự viết retry:
thử lại tối đa 3 lần, timeout 30s, giãn cách 5s giữa các lần thử.
Lỗi 5xx/timeout/mất kết nối thì thử lại; lỗi 4xx là sai từ phía mình
(sai shape body...) nên dừng ngay để sửa.

Dùng như thư viện:
    from kanzo import lay_bang, binh_luan, chuyen_the
    b = lay_bang("esp32-securitykey")

Dùng như CLI:
    python tools/kanzo.py board --project esp32-securitykey
    python tools/kanzo.py comment 203 --file binh-luan.txt
    python tools/kanzo.py move 203 done
Mã thoát: 0 xong · 1 lỗi chạy · 2 sai cách dùng (theo bảng NCKH-052).
"""
import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request

API_MAC_DINH = "http://100.101.100.100:4242/api"
TIMEOUT = 30      # giây cho mỗi lần gọi
SO_LAN_THU = 3    # 1 lần chính + 2 lần thử lại
GIAN_CACH = 5     # giây giữa các lần thử


class KanzoLoi(Exception):
    """Lỗi gọi Kanzo sau khi đã thử hết quota."""


def api_goc(api=None):
    """Chuẩn hóa gốc API (ưu tiên tham số, rồi env KANZO_API)."""
    return (api or os.environ.get("KANZO_API") or API_MAC_DINH).rstrip("/")


def _ghep_url(goc, path):
    return goc.rstrip("/") + "/" + path.lstrip("/")


def nen_thu_lai(trang_thai=None):
    """Có nên thử lại không: mất kết nối/timeout (None) và 5xx thì có."""
    if trang_thai is None:
        return True
    return trang_thai >= 500


def body_comment(noi_dung):
    """Shape body đúng cho endpoint comment (field `body`, text thuần)."""
    return {"body": noi_dung}


def body_move(trang_thai):
    """Shape body cho endpoint move."""
    return {"status": trang_thai}


def goi_api(method, path, body=None, api=None, timeout=TIMEOUT,
            so_lan=SO_LAN_THU, gian_cach=GIAN_CACH):
    """Gọi 1 endpoint Kanzo kèm thử lại. Trả về JSON đã parse (dict/list)."""
    goc = api_goc(api)
    url = _ghep_url(goc, path)
    du_lieu = None
    if body is not None:
        du_lieu = json.dumps(body, ensure_ascii=False).encode("utf-8")
    loi_cuoi = None
    for lan in range(1, so_lan + 1):
        try:
            req = urllib.request.Request(url, data=du_lieu, method=method,
                                         headers={"Accept": "application/json",
                                                  "Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                tho = resp.read().decode("utf-8").strip()
                return json.loads(tho) if tho else {"ok": True}
        except urllib.error.HTTPError as e:
            loi_cuoi = f"HTTP {e.code}: {e.read().decode('utf-8', 'replace')[:200]}"
            if not nen_thu_lai(e.code):
                raise KanzoLoi(loi_cuoi)
        except Exception as e:  # noqa: BLE001 - timeout/mất mạng đều thử lại
            loi_cuoi = f"{type(e).__name__}: {e}"
        if lan < so_lan:
            time.sleep(gian_cach)
    raise KanzoLoi(f"hỏng sau {so_lan} lần: {loi_cuoi}")


# ---- Các thao tác mức cao (mọi tool Viện dùng các hàm này) ----

def lay_bang(project, **kw):
    """GET /board?project=... Trả về list thẻ (mảng tasks)."""
    from urllib.parse import quote
    du_lieu = goi_api("GET", f"/board?project={quote(project)}", **kw)
    if isinstance(du_lieu, dict):
        return du_lieu.get("tasks", [])
    return du_lieu


def lay_the(task_id, **kw):
    """GET 1 thẻ theo id (kèm comments)."""
    return goi_api("GET", f"/tasks/{task_id}", **kw)


def tao_the(project, tieu_de, mo_ta="", **kw):
    """POST /tasks. Trả về thẻ mới (có id)."""
    return goi_api("POST", "/tasks",
                   {"project": project, "title": tieu_de,
                    "description": mo_ta}, **kw)


def sua_the(task_id, tieu_de=None, mo_ta=None, tags=None, **kw):
    """PATCH 1 thẻ."""
    body = {}
    if tieu_de is not None:
        body["title"] = tieu_de
    if mo_ta is not None:
        body["description"] = mo_ta
    if tags is not None:
        body["tags"] = tags
    return goi_api("PATCH", f"/tasks/{task_id}", body, **kw)


def chuyen_the(task_id, trang_thai, **kw):
    """POST /tasks/<id>/move {status}."""
    return goi_api("POST", f"/tasks/{task_id}/move",
                   body_move(trang_thai), **kw)


def binh_luan(task_id, noi_dung, **kw):
    """POST /tasks/<id>/comments {body}."""
    return goi_api("POST", f"/tasks/{task_id}/comments",
                   body_comment(noi_dung), **kw)


def xoa_the(task_id, **kw):
    """DELETE 1 thẻ. CHỈ Viện trưởng được gọi (có --yes ở CLI)."""
    return goi_api("DELETE", f"/tasks/{task_id}", **kw)


def _in_bang(tasks):
    tu_trang_thai = {}
    for t in tasks:
        tu_trang_thai.setdefault(t.get("status", "?"), []).append(t)
    print(f"tổng: {len(tasks)}")
    for trang_thai in ("todo", "doing", "review", "done"):
        ds = tu_trang_thai.get(trang_thai, [])
        if ds:
            print(f"  {trang_thai}: {len(ds)}")
    for t in sorted(tasks, key=lambda x: x.get("id", 0)):
        print(f"  id={t.get('id')} [{t.get('status')}] "
              f"cmt={t.get('comments', 0)} {(t.get('title') or '')[:80]}")


def tu_kiem():
    """Self-test offline: bảng thử lại, shape body, ghép URL."""
    assert nen_thu_lai(None) is True
    assert nen_thu_lai(500) is True and nen_thu_lai(503) is True
    assert nen_thu_lai(400) is False and nen_thu_lai(404) is False
    assert body_comment("x") == {"body": "x"}
    assert body_move("done") == {"status": "done"}
    assert _ghep_url("http://a/api/", "/tasks/1") == "http://a/api/tasks/1"
    assert _ghep_url("http://a/api", "tasks/1") == "http://a/api/tasks/1"
    print("self-test ok: retry 5xx/timeout, dừng 4xx, shape comment/move, ghép URL.")
    return 0


def main(argv=None):
    p = argparse.ArgumentParser(description="Client CLI cho API Kanzo.")
    p.add_argument("--api", default=None, help="gốc API (mặc định env/bảng Viện)")
    p.add_argument("--self-test", action="store_true", help="tự kiểm offline")
    sub = p.add_subparsers(dest="lenh")
    b = sub.add_parser("board", help="liệt kê thẻ 1 bảng")
    b.add_argument("--project", required=True)
    b.add_argument("--json", action="store_true", help="in JSON thô")
    g = sub.add_parser("get", help="đọc 1 thẻ")
    g.add_argument("id", type=int)
    c = sub.add_parser("create", help="tạo thẻ")
    c.add_argument("--project", required=True)
    c.add_argument("--title", required=True)
    c.add_argument("--desc", default="")
    m = sub.add_parser("move", help="chuyển cột thẻ")
    m.add_argument("id", type=int)
    m.add_argument("status", choices=["backlog", "todo", "doing", "review", "done"])
    k = sub.add_parser("comment", help="bình luận vào thẻ")
    k.add_argument("id", type=int)
    k.add_argument("--body", default=None, help="nội dung (ngắn)")
    k.add_argument("--file", default=None, help="đọc nội dung từ file")
    d = sub.add_parser("delete", help="XÓA thẻ (chỉ Viện trưởng)")
    d.add_argument("id", type=int)
    d.add_argument("--yes", action="store_true", help="xác nhận xóa")
    args = p.parse_args(argv)
    if args.self_test:
        return tu_kiem()
    kw = {"api": args.api} if args.api else {}
    try:
        if args.lenh == "board":
            tasks = lay_bang(args.project, **kw)
            if args.json:
                print(json.dumps(tasks, ensure_ascii=False))
            else:
                _in_bang(tasks)
        elif args.lenh == "get":
            print(json.dumps(lay_the(args.id, **kw), ensure_ascii=False, indent=1))
        elif args.lenh == "create":
            the = tao_the(args.project, args.title, args.desc, **kw)
            print(f"đã tạo thẻ id={the.get('id')}")
        elif args.lenh == "move":
            chuyen_the(args.id, args.status, **kw)
            print(f"thẻ {args.id} -> {args.status}")
        elif args.lenh == "comment":
            if args.file:
                noi_dung = open(args.file, encoding="utf-8-sig").read()
            elif args.body is not None:
                noi_dung = args.body
            else:
                print("thiếu --body hoặc --file", file=sys.stderr)
                return 2
            binh_luan(args.id, noi_dung, **kw)
            print(f"đã bình luận thẻ {args.id}")
        elif args.lenh == "delete":
            if not args.yes:
                print("xóa thẻ cần --yes (chỉ Viện trưởng)", file=sys.stderr)
                return 2
            xoa_the(args.id, **kw)
            print(f"đã xóa thẻ {args.id}")
        else:
            p.print_help()
            return 2
    except KanzoLoi as e:
        print(f"lỗi Kanzo: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
