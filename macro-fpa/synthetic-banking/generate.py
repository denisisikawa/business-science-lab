"""Generate a reproducible banking cost allocation dataset using synthetic inputs."""
import argparse
import csv
from collections import defaultdict
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from random import Random

AREAS = (
    ("A01", "Operacoes de Cartoes"), ("A02", "Operacoes de Pagamentos"),
    ("A03", "Operacoes de Credito"), ("A04", "Plataformas Digitais"),
    ("A05", "Infraestrutura e Redes"), ("A06", "Facilities"),
    ("A07", "Diretoria Corporativa"),
)
PRODUCTS = (
    ("P01", "Cartoes", "A01"), ("P02", "Conta e Pagamentos", "A02"),
    ("P03", "Credito Pessoal", "A03"),
)
# Volume mensal de referência e, para contestação, minutos ativos padrão.
EVENTS = (
    ("P01", "APP", "AUTORIZACAO_CARTAO", 380000, ""),
    ("P01", "WEB", "AUTORIZACAO_CARTAO", 62000, ""),
    ("P01", "APP", "CONTESTACAO_SIMPLES", 2000, "2.0"),
    ("P01", "CENTRAL", "CONTESTACAO_COMPLEXA", 1000, "5.0"),
    ("P02", "APP", "PIX_ENVIADO", 320000, ""),
    ("P02", "WEB", "PIX_ENVIADO", 56000, ""),
    ("P02", "APP", "PAGAMENTO_BOLETO", 78000, ""),
    ("P03", "APP", "ANALISE_PROPOSTA", 14500, ""),
    ("P03", "AGENCIA", "ANALISE_PROPOSTA", 6800, ""),
    ("P03", "APP", "CONTRATACAO_CREDITO", 5800, ""),
)
SCENARIOS = ("orcado", "realizado")
CENT = Decimal("0.01")


@dataclass(frozen=True)
class CostRule:
    id: str
    area: str
    category: str
    description: str
    nature: str
    product: str
    driver: str
    fixed: str
    unit_rate: str = "0"
    variable_event: str = ""


CONTRACTS = (
    CostRule("C01", "A01", "sistemas", "Processador de cartoes", "direto",
             "P01", "apropriacao_direta", "48000", "0.055", "AUTORIZACAO_CARTAO"),
    CostRule("C02", "A02", "sistemas", "Motor de pagamentos instantaneos", "direto",
             "P02", "apropriacao_direta", "36000", "0.028", "PIX_ENVIADO"),
    CostRule("C03", "A03", "sistemas", "Motor de credito", "direto",
             "P03", "apropriacao_direta", "42000", "0.410", "ANALISE_PROPOSTA"),
    CostRule("C04", "A04", "cloud", "Infraestrutura cloud compartilhada", "indireto",
             "", "horas_computacao", "54000"),
    CostRule("C05", "A04", "licencas", "Suite interna de produtividade", "indireto",
             "", "licencas_ativas", "17500"),
    CostRule("C06", "A05", "telecom", "Links WAN compartilhados", "indireto",
             "", "links_ativos", "28500"),
    CostRule("C07", "A06", "aluguel", "Espaco das operacoes bancarias", "indireto",
             "", "area_ocupada_m2", "76000"),
    CostRule("C08", "A01", "telecom", "Tronco dedicado a Cartoes", "direto",
             "P01", "apropriacao_direta", "6300"),
    CostRule("C09", "A07", "aluguel", "Escritorio corporativo", "corporativo",
             "", "centro_corporativo", "31000"),
)
INTERNAL = (
    CostRule("I01", "A01", "pessoal", "Equipe compartilhada de contestacao", "indireto",
             "", "minutos_tdabc", "120000"),
    CostRule("I02", "A06", "facilities", "Utilidades das operacoes", "indireto",
             "", "area_ocupada_m2", "12500"),
    CostRule("I03", "A07", "pessoal", "Equipe da diretoria corporativa", "corporativo",
             "", "centro_corporativo", "88000"),
)


def money(value):
    return value.quantize(CENT, rounding=ROUND_HALF_UP)


def generate(year, seed):
    rng = Random(seed)
    data = defaultdict(list)
    data["areas.csv"].extend(AREAS)
    data["produtos.csv"].extend(PRODUCTS)
    for rule in CONTRACTS:
        data["contratos.csv"].append((rule.id, rule.description, f"Fornecedor Ficticio {rule.id}",
                                      rule.area, rule.category, f"{year}-01", f"{year}-12",
                                      rule.fixed, rule.unit_rate, rule.variable_event))
    for month in range(1, 13):
        period = f"{year}-{month:02d}"
        seasonal = Decimal(100 + month + (12 if month == 11 else 18 if month == 12 else 0)) / 100
        for scenario in SCENARIOS:
            actual = scenario == "realizado"
            transaction_counts = defaultdict(int)
            minutes = Decimal(0)
            for product, channel, event, base, standard in EVENTS:
                factor = Decimal(rng.randint(94, 108)) / 100 if actual else Decimal(1)
                volume = int(base * seasonal * factor)
                per_case = Decimal(standard) if standard else None
                if event == "CONTESTACAO_COMPLEXA" and actual and month in (3, 11, 12):
                    per_case += Decimal("0.5")
                data["volumetria.csv"].append((period, scenario, product, channel, event, volume, per_case))
                transaction_counts[product, event] += volume
                if per_case is not None:
                    minutes += volume * per_case

            for index, (product, _, _) in enumerate(PRODUCTS):
                activity = sum(qty for (owner, _), qty in transaction_counts.items() if owner == product)
                for driver, quantity in (
                    ("horas_computacao", 200 + activity // 120),
                    ("licencas_ativas", (82, 65, 50)[index] + actual * (month // 4)),
                    ("links_ativos", (16, 22, 9)[index] + (actual and month >= 7 and index == 1)),
                    ("area_ocupada_m2", (420, 340, 280)[index]),
                ):
                    data["direcionadores.csv"].append((period, scenario, driver, product, quantity))

            practical = Decimal(12000 if month < 10 else 14500)
            if actual and month >= 10:
                practical += Decimal(600)
            data["capacidade.csv"].append((period, scenario, "I01", practical, minutes))
            data["direcionadores.csv"].append((period, scenario, "minutos_tdabc", "P01", minutes))

            for rule in (*CONTRACTS, *INTERNAL):
                quantity = transaction_counts[rule.product, rule.variable_event] if rule.variable_event else 0
                fixed = Decimal(rule.fixed)
                # Variações sintéticas independentes para análise de preço e consumo.
                if actual and month >= 7 and rule.id in ("C06", "C07"):
                    fixed *= Decimal("1.05")
                if actual and month >= 3 and rule.id == "I01":
                    fixed *= Decimal("1.10")
                variable = money(Decimal(quantity) * Decimal(rule.unit_rate))
                total = money(fixed) + variable
                data["custos.csv"].append((period, scenario, rule.id,
                                          rule.id if rule in CONTRACTS else "", rule.area, rule.category,
                                          rule.description, rule.nature, rule.product, rule.driver,
                                          quantity, money(fixed), variable, total))
    return data


HEADERS = {
    "areas.csv": "area_id nome",
    "produtos.csv": "produto_id nome area_responsavel_id",
    "contratos.csv": "contrato_id objeto fornecedor area_dona_id categoria inicio fim mensalidade_base_brl tarifa_unitaria_brl evento_faturavel",
    "volumetria.csv": "mes cenario produto_id canal evento volume minutos_ativos_por_caso",
    "direcionadores.csv": "mes cenario direcionador produto_id quantidade",
    "capacidade.csv": "mes cenario custo_id capacidade_pratica_minutos minutos_consumidos",
    "custos.csv": "mes cenario custo_id contrato_id area_dona_id categoria descricao natureza produto_direto_id direcionador quantidade_faturavel valor_fixo_brl valor_variavel_brl valor_total_brl",
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--year", type=int, default=2025)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    if not 1900 <= args.year <= 9999:
        parser.error("--year must be between 1900 and 9999")
    args.output.mkdir(parents=True, exist_ok=True)
    for name, rows in generate(args.year, args.seed).items():
        with (args.output / name).open("w", encoding="utf-8", newline="") as file:
            writer = csv.writer(file, lineterminator="\n")
            writer.writerow(HEADERS[name].split())
            writer.writerows(rows)


if __name__ == "__main__":
    main()
