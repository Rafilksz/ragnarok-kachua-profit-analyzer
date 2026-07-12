from __future__ import annotations

import re
from decimal import Decimal, InvalidOperation
from pathlib import Path

import pandas as pd
import streamlit as st

from src.gnjoy_client import GnjoyClient
from src.html_parser import lowest_offer_price, parse_market_history, parse_trading_offers
from src.kachua_rewards import (
    DEFAULT_KACHUA_REWARDS,
    calculate_coupon_count,
    calculate_redeemable_quantity,
    calculate_reward_total_zeny,
    is_kachua_coupon,
)
from src.parser import parse_drop_text
from src.profit_calculator import (
    calculate_buy_fast_price,
    calculate_best_joycoin_package,
    calculate_zeny_per_real,
    price_drop_items,
    probability_to_rate,
    simulate_profit,
    summarize_profit,
)
from src.url_builder import build_market_price_url, build_trading_url


DEFAULT_DROPS_PATH = Path("data/drops.txt")
DEBUG_DIR = Path("data/debug")
MAX_DROP_ITEMS_ONLINE = 60
REQUEST_DELAY_SECONDS = 1.0


def decimal_from_input(value: str) -> Decimal:
    normalized = value.strip().replace(".", "").replace(",", ".")
    return Decimal(normalized)


def format_brl(value: Decimal) -> str:
    return f"R$ {float(value):,.4f}".replace(",", "X").replace(".", ",").replace("X", ".")


def format_zeny(value: Decimal | int | None) -> str:
    if value is None:
        return "-"

    return f"{int(value):,}".replace(",", ".")


def safe_cache_name(item_name: str, suffix: str) -> str:
    safe_name = re.sub(r"[^A-Za-z0-9_-]+", "_", item_name).strip("_")
    return f"{safe_name}_{suffix}.html"


def append_log(logs: list[str], message: str, log_box) -> None:
    logs.append(message)
    log_box.text_area(
        "Debug das buscas",
        value="\n".join(logs[-250:]),
        height=360,
        disabled=True,
        label_visibility="collapsed",
    )


def analyze_online(
    drops,
    server: str,
    delay_seconds: float,
    save_debug_html: bool,
    max_artifacts: int,
    zeny_per_real: Decimal,
    log_box,
) -> tuple[pd.DataFrame, pd.DataFrame, list[str]]:
    logs: list[str] = []
    table_rows: list[dict[str, object]] = []
    reward_rows: list[dict[str, object]] = []
    prices_by_search_name: dict[str, int] = {}
    random_drops = [item for item in drops if not is_kachua_coupon(item)]
    coupon_count = calculate_coupon_count(drops, max_artifacts)
    progress = st.progress(0)

    def logger(message: str) -> None:
        append_log(logs, message, log_box)

    client = GnjoyClient(
        delay_seconds=delay_seconds,
        logger=logger,
        debug_dir=DEBUG_DIR if save_debug_html else None,
    )

    try:
        total_steps = (len(random_drops) + len(DEFAULT_KACHUA_REWARDS)) * 2
        finished_steps = 0

        for item in random_drops:
            append_log(logs, f"ITEM: {item.original_name} -> {item.search_name}", log_box)

            market_url = build_market_price_url(item.search_name, server=server)
            market_result = client.get(
                market_url,
                cache_name=safe_cache_name(item.search_name, "market_price"),
            )
            finished_steps += 1
            progress.progress(finished_steps / total_steps)
            market_history = parse_market_history(market_result.html, item.search_name)
            append_log(
                logs,
                "MARKET PARSED: "
                f"has_history={market_history.has_history} "
                f"min={market_history.minimum_price} "
                f"avg={market_history.average_price} "
                f"max={market_history.maximum_price} "
                f"volume={market_history.volume}",
                log_box,
            )

            trading_url = build_trading_url(item.search_name, "BUY", server=server)
            trading_result = client.get(
                trading_url,
                cache_name=safe_cache_name(item.search_name, "trading_BUY"),
            )
            finished_steps += 1
            progress.progress(finished_steps / total_steps)
            buy_offers = parse_trading_offers(
                trading_result.html,
                item.search_name,
                "BUY",
            )
            current_price = lowest_offer_price(buy_offers)
            buy_fast_price = calculate_buy_fast_price(current_price)
            append_log(
                logs,
                "TRADING BUY PARSED: "
                f"offers={len(buy_offers)} "
                f"lowest_price={current_price} "
                f"buy_fast_price={buy_fast_price} "
                f"all_prices={[offer.price for offer in buy_offers]}",
                log_box,
            )

            selected_price = buy_fast_price or 0
            prices_by_search_name[item.search_name] = selected_price
            expected_drop_quantity = (
                Decimal(max_artifacts)
                * Decimal(item.quantity)
                * probability_to_rate(item.probability_percent)
            )

            table_rows.append(
                {
                    "Item name": item.original_name,
                    "Nome busca": item.search_name,
                    "Quantidade drop esperado": expected_drop_quantity,
                    "Chance %": item.probability_percent,
                    "Valor min": market_history.minimum_price,
                    "Valor max": market_history.maximum_price,
                    "Valor medio": market_history.average_price,
                    "Volume historico": market_history.volume,
                    "Valor atual BUY": current_price,
                    "Valor BUY FAST (-2%)": buy_fast_price,
                    "Trading BUY retornos": len(buy_offers),
                    "URL market-price": market_url,
                    "URL trading BUY": trading_url,
                }
            )

        priced_items = price_drop_items(
            items=random_drops,
            prices_by_search_name=prices_by_search_name,
            zeny_per_real=zeny_per_real,
            artifact_quantity_for_chance=max_artifacts,
        )
        drop_summary, _drop_simulation = summarize_profit(
            priced_items=priced_items,
            artifact_cost_brl=calculate_best_joycoin_package().artifact_cost_brl,
            zeny_per_real=zeny_per_real,
            max_artifacts=max_artifacts,
        )

        for row, priced in zip(table_rows, priced_items):
            row["EV zeny por ovo"] = priced.expected_value_zeny_per_box
            row["EV BRL por ovo"] = priced.expected_value_brl_per_box
            row[f"Chance >=1 em {max_artifacts}"] = priced.accumulated_chance_percent

        for reward in DEFAULT_KACHUA_REWARDS:
            append_log(
                logs,
                f"CUPOM: {coupon_count} Cupom da Kachua -> {reward.item_name} "
                f"({reward.coupon_cost} cupons cada)",
                log_box,
            )

            market_url = build_market_price_url(reward.item_name, server=server)
            market_result = client.get(
                market_url,
                cache_name=safe_cache_name(reward.item_name, "coupon_market_price"),
            )
            finished_steps += 1
            progress.progress(finished_steps / total_steps)
            market_history = parse_market_history(market_result.html, reward.item_name)
            append_log(
                logs,
                "COUPON MARKET PARSED: "
                f"has_history={market_history.has_history} "
                f"min={market_history.minimum_price} "
                f"avg={market_history.average_price} "
                f"max={market_history.maximum_price} "
                f"volume={market_history.volume}",
                log_box,
            )

            trading_url = build_trading_url(reward.item_name, "BUY", server=server)
            trading_result = client.get(
                trading_url,
                cache_name=safe_cache_name(reward.item_name, "coupon_trading_BUY"),
            )
            finished_steps += 1
            progress.progress(finished_steps / total_steps)
            buy_offers = parse_trading_offers(
                trading_result.html,
                reward.item_name,
                "BUY",
            )
            current_price = lowest_offer_price(buy_offers)
            buy_fast_price = calculate_buy_fast_price(current_price)
            redeemable_quantity = calculate_redeemable_quantity(
                coupon_count,
                reward.coupon_cost,
            )
            used_coupons = redeemable_quantity * reward.coupon_cost
            total_buy_fast_zeny = calculate_reward_total_zeny(
                coupon_count,
                reward.coupon_cost,
                buy_fast_price,
            )
            total_average_zeny = calculate_reward_total_zeny(
                coupon_count,
                reward.coupon_cost,
                market_history.average_price,
            )
            append_log(
                logs,
                "COUPON TRADING BUY PARSED: "
                f"offers={len(buy_offers)} "
                f"lowest_price={current_price} "
                f"buy_fast_price={buy_fast_price} "
                f"redeemable={redeemable_quantity} "
                f"total_buy_fast_zeny={int(total_buy_fast_zeny)} "
                f"all_prices={[offer.price for offer in buy_offers]}",
                log_box,
            )

            reward_rows.append(
                {
                    "Cupons Kachua": coupon_count,
                    "Item de Cupom": reward.item_name,
                    "Cupons por item": reward.coupon_cost,
                    "Quantidade compravel": redeemable_quantity,
                    "Cupons usados": used_coupons,
                    "Cupons sobrando": coupon_count - used_coupons,
                    "Valor min": market_history.minimum_price,
                    "Valor max": market_history.maximum_price,
                    "Valor medio": market_history.average_price,
                    "Volume historico": market_history.volume,
                    "Valor atual BUY": current_price,
                    "Valor BUY FAST (-2%)": buy_fast_price,
                    "Total BUY FAST zeny": total_buy_fast_zeny,
                    "Total media zeny": total_average_zeny,
                    "Trading BUY retornos": len(buy_offers),
                    "URL market-price": market_url,
                    "URL trading BUY": trading_url,
                }
            )

        best_reward_row = max(
            reward_rows,
            key=lambda row: row["Total BUY FAST zeny"],
            default=None,
        )
        coupon_sale_zeny = (
            Decimal(best_reward_row["Total BUY FAST zeny"])
            if best_reward_row is not None
            else Decimal("0")
        )
        coupon_value_zeny_per_artifact = coupon_sale_zeny / Decimal(max_artifacts)
        expected_value_zeny_per_box = (
            drop_summary.expected_value_zeny_per_box + coupon_value_zeny_per_artifact
        )
        simulation = simulate_profit(
            max_artifacts=max_artifacts,
            artifact_cost_brl=drop_summary.artifact_cost_brl,
            expected_value_zeny_per_box=expected_value_zeny_per_box,
            zeny_per_real=zeny_per_real,
        )
        first_profitable_quantity = next(
            (
                row.artifact_quantity
                for row in simulation
                if row.expected_profit_brl > Decimal("0")
            ),
            None,
        )
        sale_zeny = expected_value_zeny_per_box * Decimal(max_artifacts)
        sale_brl = sale_zeny / zeny_per_real
        total_cost_brl = drop_summary.artifact_cost_brl * Decimal(max_artifacts)
        total_profit_brl = sale_brl - total_cost_brl
        expected_value_brl_per_box = expected_value_zeny_per_box / zeny_per_real
        expected_profit_brl_per_box = (
            expected_value_brl_per_box - drop_summary.artifact_cost_brl
        )
        roi_percent = (
            (expected_profit_brl_per_box / drop_summary.artifact_cost_brl)
            * Decimal("100")
            if drop_summary.artifact_cost_brl > 0
            else Decimal("0")
        )

        summary_rows = [
            {"Metrica": "Custo por Artefato", "Valor": format_brl(drop_summary.artifact_cost_brl)},
            {"Metrica": "Custo total", "Valor": format_brl(total_cost_brl)},
            {
                "Metrica": "EV zeny por Artefato (drops)",
                "Valor": format_zeny(drop_summary.expected_value_zeny_per_box),
            },
            {
                "Metrica": "EV zeny por Artefato (melhor cupom)",
                "Valor": format_zeny(coupon_value_zeny_per_artifact),
            },
            {
                "Metrica": "EV zeny por Artefato total",
                "Valor": format_zeny(expected_value_zeny_per_box),
            },
            {
                "Metrica": f"Zeny da venda em {max_artifacts} Artefatos",
                "Valor": format_zeny(sale_zeny),
            },
            {
                "Metrica": f"BRL da venda em {max_artifacts} Artefatos",
                "Valor": format_brl(sale_brl),
            },
            {
                "Metrica": "EV BRL por Artefato",
                "Valor": format_brl(expected_value_brl_per_box),
            },
            {
                "Metrica": "Lucro esperado por Artefato",
                "Valor": format_brl(expected_profit_brl_per_box),
            },
            {"Metrica": "Lucro esperado total", "Valor": format_brl(total_profit_brl)},
            {"Metrica": "ROI", "Valor": f"{float(roi_percent):.2f}%"},
            {
                "Metrica": "Melhor item para Cupom da Kachua",
                "Valor": best_reward_row["Item de Cupom"] if best_reward_row else "-",
            },
            {
                "Metrica": "Zeny do melhor resgate de cupons",
                "Valor": format_zeny(coupon_sale_zeny),
            },
            {
                "Metrica": "Primeira quantidade lucrativa",
                "Valor": first_profitable_quantity or "Nao lucrativo ate o limite",
            },
        ]

        simulation_df = pd.DataFrame(
            [
                {
                    "Artefatos": row.artifact_quantity,
                    "Custo BRL": row.total_cost_brl,
                    "Retorno esperado zeny": row.expected_return_zeny,
                    "Retorno esperado BRL": row.expected_return_brl,
                    "Lucro esperado BRL": row.expected_profit_brl,
                }
                for row in simulation
            ]
        )

        st.session_state["metrics"] = {
            "artifact_cost_brl": drop_summary.artifact_cost_brl,
            "expected_value_zeny_per_box": expected_value_zeny_per_box,
            "expected_value_brl_per_box": expected_value_brl_per_box,
            "expected_profit_brl_per_box": expected_profit_brl_per_box,
            "roi_percent": roi_percent,
        }
        st.session_state["simulation_df"] = simulation_df
        st.session_state["coupon_rewards_df"] = pd.DataFrame(reward_rows).sort_values(
            by="Total BUY FAST zeny",
            ascending=False,
        )
        return pd.DataFrame(table_rows), pd.DataFrame(summary_rows), logs
    finally:
        client.close()


st.set_page_config(
    page_title="Ragnarok Kachua Profit Analyzer",
    page_icon="R",
    layout="wide",
)

st.title("Ragnarok Kachua Profit Analyzer")

drop_text = DEFAULT_DROPS_PATH.read_text(encoding="utf-8") if DEFAULT_DROPS_PATH.exists() else ""

with st.sidebar:
    st.header("Configuracao")

    server = st.selectbox("Servidor", options=["FREYA"], index=0)
    reference_zeny = st.number_input(
        "Zeny de referencia",
        min_value=1,
        value=1_000_000,
        step=100_000,
    )
    reference_brl_text = st.text_input("Valor em BRL da referencia", value="1,40")
    max_artifacts = st.number_input(
        "Quantidade maxima de Artefatos",
        min_value=1,
        value=1000,
        step=100,
    )
    save_debug_html = st.checkbox("Salvar HTML em data/debug", value=False)

    best_package = calculate_best_joycoin_package()
    st.caption(
        "Pacote usado: "
        f"{format_zeny(best_package.joy_coin)} Joy Coin por {format_brl(best_package.brl)}"
    )

st.subheader("Lista de drops")
drop_text = st.text_area(
    "Cole ou edite a lista",
    value=drop_text,
    height=280,
)

try:
    drops = parse_drop_text(drop_text)
    reference_brl = decimal_from_input(reference_brl_text)
    zeny_per_real = calculate_zeny_per_real(reference_zeny, reference_brl)
except (ValueError, InvalidOperation) as exc:
    st.error(f"Configuracao invalida: {exc}")
    st.stop()

if not drops:
    st.warning("Nenhum item encontrado na lista.")
    st.stop()

if len(drops) > MAX_DROP_ITEMS_ONLINE:
    st.error(
        f"A lista tem {len(drops)} itens. "
        f"Para proteger o app online, o limite atual e {MAX_DROP_ITEMS_ONLINE} itens."
    )
    st.stop()

st.info(
    f"Cotacao usada: {format_zeny(reference_zeny)} zeny = {format_brl(reference_brl)}. "
    f"Simulacao: {max_artifacts} Artefatos."
)

log_box = st.empty()

if st.button("Buscar GNJOY e analisar", type="primary"):
    result_df, summary_df, debug_logs = analyze_online(
        drops=drops,
        server=server,
        delay_seconds=REQUEST_DELAY_SECONDS,
        save_debug_html=save_debug_html,
        max_artifacts=max_artifacts,
        zeny_per_real=zeny_per_real,
        log_box=log_box,
    )

    metrics = st.session_state["metrics"]
    simulation_df = st.session_state["simulation_df"]
    coupon_rewards_df = st.session_state["coupon_rewards_df"]
    final_simulation_row = simulation_df.iloc[-1]

    metric_columns = st.columns(6)
    metric_columns[0].metric("Custo por Artefato", format_brl(metrics["artifact_cost_brl"]))
    metric_columns[1].metric("Custo total", format_brl(final_simulation_row["Custo BRL"]))
    metric_columns[2].metric("Zeny da venda", format_zeny(final_simulation_row["Retorno esperado zeny"]))
    metric_columns[3].metric("BRL da venda", format_brl(final_simulation_row["Retorno esperado BRL"]))
    metric_columns[4].metric("Lucro esperado", format_brl(final_simulation_row["Lucro esperado BRL"]))
    metric_columns[5].metric("ROI", f"{float(metrics['roi_percent']):.2f}%")

    if metrics["expected_profit_brl_per_box"] > 0:
        st.success("Compensa estatisticamente com os valores atuais encontrados.")
    else:
        st.error("Nao compensa estatisticamente com os valores atuais encontrados.")

    st.subheader("Resumo")
    st.dataframe(summary_df, use_container_width=True, hide_index=True)

    st.subheader("Tabela por item")
    st.dataframe(result_df, use_container_width=True, hide_index=True)

    st.subheader("Cupons da Kachua")
    st.dataframe(coupon_rewards_df, use_container_width=True, hide_index=True)

    st.subheader("Simulacao de lucro")
    st.line_chart(simulation_df, x="Artefatos", y="Lucro esperado BRL")
    st.dataframe(simulation_df, use_container_width=True, hide_index=True)

    with st.expander("Debug completo das buscas", expanded=True):
        st.text_area(
            "Debug completo",
            value="\n".join(debug_logs),
            height=420,
            disabled=True,
            label_visibility="collapsed",
        )

    if save_debug_html:
        st.caption(f"HTMLs salvos em {DEBUG_DIR}")
