// FRONTEND: muestra las citas y llama al backend. No tiene reglas de negocio:
// las reglas viven en el backend (patrón State) y los avisos también (patrón Observer).

const $ = (id) => document.getElementById(id);

async function cargar() {
  const r = await fetch("/api/citas");
  const datos = await r.json();
  if (!$("reloj").value) $("reloj").value = datos.t0;   // reloj inicial = T0 (26/10/2026 08:00)
  pintarCitas(datos.citas);
  pintarAvisos(datos.avisos);
  pintarHistorial(datos.historial);
}

function pintarCitas(citas) {
  $("tablaCitas").innerHTML = citas.map(c => `
    <tr>
      <td><strong>${c.id}</strong></td>
      <td>${c.paciente}<br><small>Canal: ${c.canal}</small></td>
      <td>${c.medico}</td>
      <td>${c.fecha}</td>
      <td><span class="estado ${c.estado.toLowerCase()}">${c.estado}</span>${c.tardia ? '<br><small>Cambio tardío</small>' : ''}</td>
      <td>
        <button onclick="accion('${c.id}','cancelar')">Cancelar</button>
        <button class="secundario" onclick="accion('${c.id}','atender')">Atender</button>
      </td>
    </tr>`).join("");
}

function pintarAvisos(avisos) {
  $("avisos").innerHTML = avisos.length
    ? avisos.map(a => `<li><strong>${a.para}</strong> · ${a.canal} a ${a.destino}<br>${a.texto}</li>`).join("")
    : '<li class="vacio">Todavía no hay avisos.</li>';
}

function pintarHistorial(registros) {
  $("historial").innerHTML = registros.length
    ? registros.map(t => `<li>${t}</li>`).join("")
    : '<li class="vacio">Todavía no hay cambios.</li>';
}

// Los botones NO revisan el estado: siempre envían la acción.
// Así se ve que es el backend (State) quien acepta o rechaza.
async function accion(id, tipo) {
  const r = await fetch(`/api/citas/${id}/${tipo}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ ahora: $("reloj").value }),
  });
  const res = await r.json();
  const caja = $("respuesta");
  caja.hidden = false;
  caja.className = "respuesta " + (res.ok ? "bien" : "mal");
  const avisos = res.avisos_nuevos && res.avisos_nuevos.length
    ? ` Se enviaron ${res.avisos_nuevos.length} avisos.` : " No se enviaron avisos.";
  caja.textContent = `${id}: ${res.mensaje}` + (tipo === "cancelar" ? avisos : "");
  cargar();
}

$("btnReiniciar").onclick = async () => {
  await fetch("/api/reiniciar", { method: "POST" });
  $("respuesta").hidden = true;
  cargar();
};

cargar();
