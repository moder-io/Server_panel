// backend/web/static/app.js

function statusBadge(status) {
  return `<span class="badge">${status}</span>`;
}

async function loadStats() {
  try {
    const res = await fetch("/api/stats", {
      cache: "no-store",
      headers: { "Accept": "application/json" }
    });
    if (!res.ok) return;

    const s = await res.json();

    const cpu = document.getElementById("cpu");
    const ram = document.getElementById("ram");
    const ramSub = document.getElementById("ram-sub");
    const disk = document.getElementById("disk");
    const diskSub = document.getElementById("disk-sub");
    const uptime = document.getElementById("uptime");

    if (cpu) cpu.textContent = `${s.cpu_percent}%`;
    if (ram) ram.textContent = `${s.ram_percent}%`;
    if (ramSub) ramSub.textContent = `${s.ram_used_gb} / ${s.ram_total_gb} GB`;
    if (disk) disk.textContent = `${s.disk_percent}%`;
    if (diskSub) diskSub.textContent = `${s.disk_used_gb} / ${s.disk_total_gb} GB`;
    if (uptime) uptime.textContent = `${s.uptime_seconds} s`;

  } catch (e) {
    console.log("Stats error:", e);
  }
}

async function loadServices() {
  try {
    const res = await fetch("/api/services", {
      cache: "no-store",
      headers: { "Accept": "application/json" }
    });
    if (!res.ok) return;

    const data = await res.json();

    const note = document.getElementById("svc-note");
    const box = document.getElementById("services");
    if (!box) return;

    const isAdmin = (window.USER_ROLE === "admin");

    if (!data.available) {
      if (note) note.textContent = "Servicios no disponibles en este sistema.";
    } else {
      if (note) {
        note.textContent = isAdmin
          ? "Gestiona servicios (start/stop/restart)."
          : "Solo lectura.";
      }
    }

    const rows = data.services.map(s => {
      const actionButtons = isAdmin ? `
        <button onclick="svcAction('${s.name}','start')">Start</button>
        <button onclick="svcAction('${s.name}','stop')">Stop</button>
        <button onclick="svcAction('${s.name}','restart')">Restart</button>
      ` : "";

      return `
        <tr>
          <td><strong>${s.name}</strong></td>
          <td>${statusBadge(s.status)}</td>
          ${isAdmin ? `<td class="actions">${actionButtons}</td>` : ``}
        </tr>
      `;
    }).join("");

    box.innerHTML = `
      <table class="table">
        <thead>
          <tr>
            <th>Servicio</th>
            <th>Estado</th>
            ${isAdmin ? `<th>Acciones</th>` : ``}
          </tr>
        </thead>
        <tbody>${rows}</tbody>
      </table>
    `;

  } catch (e) {
    console.log("Services error:", e);
  }
}

async function svcAction(name, action) {
  try {
    const res = await fetch(`/api/services/${name}/${action}`, {
      method: "POST",
      headers: { "Accept": "application/json" }
    });

    if (!res.ok) {
      const txt = await res.text();
      console.log("Service action failed:", res.status, txt);
    }

    await loadServices();
  } catch (e) {
    console.log("Service action error:", e);
  }
}

window.addEventListener("DOMContentLoaded", () => {
  loadStats();
  loadServices();

  setInterval(loadStats, 2000);
  setInterval(loadServices, 5000);
});
