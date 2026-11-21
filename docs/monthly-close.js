"use strict";

// Compare the source ledger before allocation. All additions use integer cents.
function monthlyAreas(month) {
  const areas = new Map();
  for (const row of BANK_DATA.custos) {
    if (row.mes !== month) continue;
    if (!areas.has(row.area_dona_id)) areas.set(row.area_dona_id, new Map());
    const entries = areas.get(row.area_dona_id);
    if (!entries.has(row.custo_id)) {
      entries.set(row.custo_id, { id: row.custo_id, contract: row.contrato_id, label: row.descricao, orcado: 0, realizado: 0 });
    }
    entries.get(row.custo_id)[row.cenario] += Math.round(Number(row.valor_total_brl) * 100);
  }
  return Array.from(areas, ([id, entries]) => {
    const rows = Array.from(entries.values());
    const budget = rows.reduce((sum, row) => sum + row.orcado, 0);
    const actual = rows.reduce((sum, row) => sum + row.realizado, 0);
    return { id, rows, budget, actual, delta: actual - budget };
  });
}

const areaLabels = {
  A01: ["Card operations", "Operações de cartões"],
  A02: ["Payment operations", "Operações de pagamentos"],
  A03: ["Credit operations", "Operações de crédito"],
  A04: ["Digital platforms", "Plataformas digitais"],
  A05: ["Infrastructure and networks", "Infraestrutura e redes"],
  A06: ["Facilities", "Facilities"],
  A07: ["Corporate management", "Diretoria corporativa"]
};
const closeMonth = document.getElementById("close-month");
const closeArea = document.getElementById("close-area");
const months = [...new Set(BANK_DATA.custos.map(row => row.mes))].sort();

function renderMonthlyClose(language) {
  const pt = language === "pt";
  const locale = pt ? "pt-BR" : "en-US";
  const money = cents => (cents / 100).toLocaleString(locale, { style: "currency", currency: "BRL" });
  const period = closeMonth.value || months[months.length - 1];
  const selection = closeArea.value || "leading";
  const monthFormat = new Intl.DateTimeFormat(locale, { month: "long", year: "numeric", timeZone: "UTC" });
  closeMonth.replaceChildren(...months.map(key => new Option(monthFormat.format(new Date(key + "-01T00:00:00Z")), key)));
  closeMonth.value = period;
  const areas = monthlyAreas(period);
  const totalDelta = areas.reduce((sum, area) => sum + area.delta, 0);
  // Rank contributions in the direction of the consolidated variance.
  areas.sort((a, b) => (Math.sign(totalDelta) || 1) * (b.delta - a.delta) || a.id.localeCompare(b.id));
  const name = area => areaLabels[area.id]?.[pt ? 1 : 0] || area.id;
  closeArea.replaceChildren(new Option(pt ? "Maior contribuição" : "Largest contribution", "leading"),
    ...areas.map(area => new Option(name(area), area.id)));
  closeArea.value = selection;
  const area = areas.find(item => item.id === selection) || areas[0];
  const percent = (area.delta / area.budget).toLocaleString(locale, { style: "percent", maximumFractionDigits: 1 });
  const result = pt
    ? `Desvio total do mês: ${money(totalDelta)}. ${name(area)}: ${money(area.actual)} realizados para ${money(area.budget)} orçados. Diferença de ${money(area.delta)} (${percent}).`
    : `Net monthly variance: ${money(totalDelta)}. ${name(area)}: ${money(area.actual)} actual against ${money(area.budget)} budget. Difference: ${money(area.delta)} (${percent}).`;
  document.getElementById("close-result").textContent = result;
  document.getElementById("close-entries").replaceChildren(...area.rows.map(row => {
    const li = document.createElement("li");
    const contract = row.contract ? (pt ? "contrato " : "contract ") + row.contract : (pt ? "interno" : "internal");
    li.textContent = `${row.id} · ${row.label} · ${contract} · ${money(row.realizado)} − ${money(row.orcado)} = ${money(row.realizado - row.orcado)}`;
    return li;
  }));
}
for (const select of [closeMonth, closeArea]) {
  select.addEventListener("change", () => renderMonthlyClose(document.documentElement.lang.startsWith("pt") ? "pt" : "en"));
}
