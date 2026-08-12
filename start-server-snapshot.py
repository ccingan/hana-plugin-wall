"""使用当前开发代码读取服务器数据快照，仅监听本机地址。"""

from __future__ import annotations

import argparse
import os
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="启动 Hana 插件墙本地快照")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--data-dir", type=Path)
    parser.add_argument("--check", action="store_true", help="验证快照与服务可启动后立即退出")
    args = parser.parse_args()

    project_dir = Path(__file__).resolve().parent
    if args.data_dir:
        data_dir = args.data_dir.resolve()
    else:
        snapshot_root = project_dir / "_server-snapshot"
        snapshots = sorted((p for p in snapshot_root.iterdir() if p.is_dir()), reverse=True)
        if not snapshots:
            raise SystemExit(f"没有找到服务器快照：{snapshot_root}")
        data_dir = snapshots[0]
    if not data_dir.is_dir():
        raise SystemExit(f"数据快照不存在：{data_dir}")

    os.environ["HANA_WALL_DATA_DIR"] = str(data_dir)

    import server

    server.load_tokens()
    server.load_sensitive()
    host = "127.0.0.1"
    print(f"当前代码：{project_dir}", flush=True)
    print(f"服务器数据快照：{data_dir}", flush=True)
    port = 0 if args.check else args.port
    httpd = server.ThreadingHTTPServer((host, port), server.Handler)
    actual_port = httpd.server_address[1]
    print(f"Hana 插件墙本地快照：http://{host}:{actual_port}/", flush=True)
    if args.check:
        httpd.server_close()
        print("启动自检通过", flush=True)
        return
    httpd.serve_forever()


if __name__ == "__main__":
    main()
