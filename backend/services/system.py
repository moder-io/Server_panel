import platform
import subprocess
import time
import psutil


DEFAULT_SERVICES = [
    "ssh",
    "pihole-FTL",
    "wg-quick@wg0",
    "smbd",
]


def systemctl_available() -> bool:
    return platform.system().lower() == "linux"


def get_stats() -> dict:
    cpu = psutil.cpu_percent(interval=0.25)

    ram = psutil.virtual_memory()
    disk = psutil.disk_usage(
        psutil.disk_partitions(all=False)[0].mountpoint
        if psutil.disk_partitions(all=False)
        else "/"
    )

    boot = psutil.boot_time()
    uptime_seconds = int(time.time() - boot)

    return {
        "cpu_percent": cpu,
        "ram_percent": ram.percent,
        "ram_used_gb": round(ram.used / (1024**3), 2),
        "ram_total_gb": round(ram.total / (1024**3), 2),
        "disk_percent": disk.percent,
        "disk_used_gb": round(disk.used / (1024**3), 2),
        "disk_total_gb": round(disk.total / (1024**3), 2),
        "uptime_seconds": uptime_seconds,
    }


def list_services(services: list[str] = DEFAULT_SERVICES) -> dict:
    """
    Devuelve:
    {
      "available": bool,
      "services": [
        {"name": "ssh", "status": "active|inactive|not-found|unknown"}
      ]
    }
    """

    if not systemctl_available():
        return {
            "available": False,
            "services": [{"name": s, "status": "unsupported"} for s in services],
        }

    out = []

    for s in services:
        try:
            r = subprocess.run(
                ["systemctl", "is-active", s],
                capture_output=True,
                text=True,
                check=False,
            )

            status = (r.stdout or "").strip()

            if r.returncode != 0:
                # Servicio no existe
                if "could not be found" in (r.stderr or "").lower():
                    status = "not-found"
                elif status == "":
                    status = "unknown"

            if not status:
                status = "unknown"

        except Exception:
            status = "unknown"

        out.append({"name": s, "status": status})

    return {"available": True, "services": out}


def service_action(service: str, action: str) -> dict:
    """
    action: start | stop | restart
    """

    if action not in {"start", "stop", "restart"}:
        return {"ok": False, "error": "invalid_action"}

    if not systemctl_available():
        return {"ok": False, "error": "unsupported_platform"}

    try:
        r = subprocess.run(
            ["sudo", "systemctl", action, service],
            capture_output=True,
            text=True,
            check=False,
        )

        if r.returncode != 0:
            err = (r.stderr or "").strip() or "systemctl_failed"
            return {"ok": False, "error": err}

        return {"ok": True}

    except Exception as e:
        return {"ok": False, "error": str(e)}
